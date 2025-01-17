import threading
import time
from enum import Enum

import pandas as pd
import tkinter as tk

from experimentNao.interaction import verbose
from experimentNao.interaction.performance_of_participant import feedback_questions as fq
from lib import excel_files, util
from lib.util import Point


class ParticipantFeedback:
    def __init__(self, interaction, save_steps_to_excel):
        """ Class that manages the questions asked to the participants during the interactions regarding their
        mental states.

        Parameters
        ----------
        interaction : experimentNao.interaction.interaction_manager.Interaction
            the interaction objects
        save_steps_to_excel : bool
            whether the answers given are to saved to Excel file in real time
        """
        self.window = interaction.chess_display.main_window
        self.output_command = interaction.conversation_manager.output_command
        self.tom_model = interaction.tom_model
        self.save_steps_to_excel = save_steps_to_excel
        # Questions
        self.questions_b, self.questions_g, self.questions_e, self.questions_a \
            = fq.declare_questions(self.tom_model, interaction.model_config)
        self.ttl_txt_b, self.ttl_txt_g, self.ttl_txt_e, self.ttl_txt_a = fq.declare_titles()
        self.sub_ttl_txt_b, self.sub_ttl_txt_g, self.sub_ttl_txt_e, self.sub_ttl_txt_a = fq.declare_subtitles()
        # Saving data
        self.df_columns = ['Type', 'Var Name', 'Question', 'Value', 'Replied']
        self.time_step_answers = []   # the list will hold all the sheets of answers
        self.current_page_answers = pd.DataFrame(columns=self.df_columns)       # hold answers of 1 page (1 type of var)
        self.current_time_step_answers = pd.DataFrame(columns=self.df_columns)  # holds answers of time step (all types)
        self.current_page_buttons = []
        self.current_page_done = False
        self.writer = None
        self.sheet_names = SheetNamesExtras()
        self.dict_feedback_events = dict()
        self.fill_dict_w_properties_of_feedback_event()
        # Which puzzles to ask for feedback
        self.n_questions_asked_in_current_puzzle = 0
        # Continuous time Periodic questions
        self.periodic_time = 200
        self.thread = None
        self.ask_asynchronous_feedback = False
        self.interaction_counter = interaction.counter
        self.initialize_periodic_action()

    def ask_feedback_from_participant(self, feedback_circumstance):
        """ Asks the questions about the mental states to the participants

        Parameters
        ----------
        feedback_circumstance : experimentNao.interaction.performance_of_participant.participant_feedback.FBEvent
        """
        fb_event_properties = self.get_properties_of_feedback_event(feedback_circumstance)
        for questions, group in zip([self.questions_b, self.questions_g, self.questions_e],
                                    [QGroup.BELIEF, QGroup.GOAL, QGroup.EMOTION]):
            self.show_questions_page(questions, group, fb_event_properties)
        if fb_event_properties.ask_about_actions:
            self.output_command('You can ask me to change the difficulty of the game, if you want to.')
            self.show_questions_page(self.questions_a, QGroup.ACTION, fb_event_properties, font_size=17)
        self.save_info_of_time_step(self.interaction_counter.current_puzzle, fb_event_properties.sheet_name_extra)
        self.current_time_step_answers = pd.DataFrame(columns=self.df_columns)  # holds answers of time step (all types)
        self.n_questions_asked_in_current_puzzle += 1
        self.reset_periodic_action()

    def ask_feedback_before_helping_participant(self, n_asks_b4_help):
        """ Asks the questions about the mental states to the participants when they ask for help (special case)

        Parameters
        ----------
        n_asks_b4_help : int
            number of times that the questions before helping were asked in the current puzzle
        """
        fb_event_properties = self.get_properties_of_feedback_event(FBEvent.HELP)
        pages_to_save, questions, questions_group = [], [], []
        ask4help_act = next((a for a in self.tom_model.decision_making_module.intention_selector.outputs if 'help' in a.name))
        if ask4help_act.belief is not None:     # ask about belief associated w/ action if existent
            questions.append(next((q for q in self.questions_b if q.associated_variable == ask4help_act.belief)))
            questions_group.append(QGroup.BELIEF)
        questions.extend([next((q for q in self.questions_g if q.associated_variable == ask4help_act.goal))])
        questions_group.extend([QGroup.GOAL])
        for question, group in zip(questions, questions_group):
            self.show_questions_page([question], group, fb_event_properties, canvas_proportion=0.8)
            pages_to_save.append(self.current_page_answers)
        sheet_name = 'Step {}.{}.help.{}'.format(self.interaction_counter.current_puzzle,
                                                 self.n_questions_asked_in_current_puzzle, n_asks_b4_help)
        self.save_to_excel_sheet(pd.concat(pages_to_save), sheet_name)
        self.reset_periodic_action()

    def show_questions_page(self, questions_, question_group, fb_event_props, font_size=15, canvas_proportion=0.9):
        """ Shows a page with 1 group of questions to be asked to the participants on the screen

        Parameters
        ----------
        questions_ : List[experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars]
            list of questions to be asked
        question_group : experimentNao.interaction.performance_of_participant.participant_feedback.QGroup
            the groups of questions, each group corresponding to a type of mental state
        fb_event_props : experimentNao.interaction.performance_of_participant.participant_feedback.FBEventProperties
        font_size : int
        canvas_proportion : float
        """
        self.reset_current_page_answers()
        cv, canvas_size = self.draw_canvas_for_questions(canvas_proportion, fb_event_props.full_screen)
        y_axis_positions = self.window.equally_distribute_positions(len(questions_) + 2, canvas_size.y)
        tt, stt = self.add_ttl_and_subtitle_to_page(question_group, canvas_size, y_axis_positions, font_size)
        for i in range(len(questions_)):
            self.prefill_current_page_answers(questions_, i)
            self.show_question(questions_[i], y_axis_positions, i, canvas_size, font_size, fb_event_props.puzzle_ended)
        if any(q.require_answer for q in questions_):                # if required
            while not (self.current_page_answers['Replied']).all():  # While not all answers given -> don't show button
                self.window.update()
        self.show_next_button(canvas_size)                           # Show button
        while not self.current_page_done:
            self.window.update()
        self.window.remove_canvas()
        if fb_event_props.save_in_the_time_step_page:
            self.merge_current_answers_2_time_step_page()

    def add_ttl_and_subtitle_to_page(self, question_group, canvas_size, y_axis_positions, font_size):
        """ adds the title and subtitle to a page of questions

        Parameters
        ----------
        question_group : experimentNao.interaction.performance_of_participant.participant_feedback.QGroup
        canvas_size : lib.util.Point
        y_axis_positions : List[float]
        font_size : int

        Returns
        -------
        Tuple[NoneType, NoneType]
        """
        w = self.window
        ttl_txt, subtitle_txt = self.get_ttl_and_subtitle_txt(question_group)
        title_on_top = True if question_group == QGroup.ACTION else False
        y_offset = 50 if title_on_top else 35
        if subtitle_txt is not None:
            reference_point = Point(canvas_size.x / 2, y_axis_positions[0])
            if title_on_top:
                pos_ttl = reference_point + Point(0, y_offset)
                pos_subtitle = reference_point + Point(0, y_offset * 2)
            else:
                pos_subtitle = reference_point + Point(0, y_offset)
                pos_ttl = Point(canvas_size.x * 0.23 + len(ttl_txt) * 5, y_axis_positions[1] - y_offset)
            stt = w.add_text_to_canvas(-1, subtitle_txt, pos_subtitle,
                                       font_=self.window.default_font + ' ' + str(font_size-1))
        else:
            pos_ttl = Point(canvas_size.x / 2, y_axis_positions[0] + y_offset)
            stt = None
        tt = w.add_text_to_canvas(-1, ttl_txt, pos_ttl, font_=w.default_font + ' ' + str(font_size+2), bold=True)
        return tt, stt

    def draw_canvas_for_questions(self, canvas_proportion=0.9, full_screen=False):
        """

        Parameters
        ----------
        canvas_proportion : float
        full_screen : bool

        Returns
        -------
        Tuple[tkinter.Canvas, lib.util.Point]
        """
        cnvs, cnvs_size = self.window.draw_pop_up_canvas(canvas_proportion=(1.0 if full_screen else canvas_proportion))
        return cnvs, cnvs_size

    def show_question(self, question, y_axis_positions, index, canvas_size, font_size, puzzle_ended):
        """ displays one question of a subgroup on the canvas

        Parameters
        ----------
        question : experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars
        y_axis_positions : List[float]
        index : int
        canvas_size : lib.util.Point
        font_size : int
        puzzle_ended : bool
        """
        position = Point(canvas_size.x / 2, y_axis_positions[index + 1])
        self.window.add_text_to_canvas(text=question.get_question_txt(puzzle_ended), canvas_id=-1, position=position,
                                       font_=self.window.default_font + ' ' + str(font_size))
        self.show_buttons_of_question(question, position, canvas_size, index)
        if question.numbered_buttons:
            self.show_text_legend_of_buttons(question, position, canvas_size, font_size=12)
        if not question.require_answer:
            self.save_answer_of_button(question, question.default_answer, index)

    def show_buttons_of_question(self, question, position, canvas_size, index):
        """ displays the buttons from 0 to 10 underneath the question, for the user to reply to the question

        Parameters
        ----------
        question : experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars
        position : lib.util.Point
        canvas_size : lib.util.Point
        index : int
        """
        x_axis_positions = self.window.equally_distribute_positions(question.number_of_buttons, canvas_size.x,
                                                                    pad_top_percentage=question.pad,
                                                                    pad_bottom_percentage=question.pad)
        buttons_of_var = []
        for j in range(question.number_of_buttons):
            button_text = str(j) if question.numbered_buttons else question.verbal_terms[j]
            b = self.window.add_button_to_canvas(canvas_id=-1, text=button_text, pad_x=12, pad_y=0, font_size=12,
                                                 position=Point(x_axis_positions[j] - 15, position.y + 20),
                                                 bg_color=self.window.colors.dark,
                                                 active_bg_color=self.window.colors.very_dark,
                                                 foreground='black', disabled_foreground='white',
                                                 command=lambda q_=question, value_=j, index_=index:
                                                 self.save_answer_of_button(q_, value_, index_))
            buttons_of_var.append(b)
        self.current_page_buttons.append(buttons_of_var)

    def show_text_legend_of_buttons(self, question, position, canvas_size, font_size=11):
        """ displays the numbers bellow the buttons from 0 to 10, for the user to reply to the question

        Parameters
        ----------
        question : experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars
        position : lib.util.Point
        canvas_size : lib.util.Point
        font_size : int
        """
        x_axis_pos = self.window.equally_distribute_positions(len(question.verbal_terms), canvas_size.x,
                                                              pad_top_percentage=question.pad,
                                                              pad_bottom_percentage=question.pad)
        for j in range(len(question.verbal_terms)):
            self.window.add_text_to_canvas(text=question.verbal_terms[j], canvas_id=-1,
                                           position=Point(x_axis_pos[j], position.y + 65),
                                           font_=self.window.default_font + ' ' + str(font_size))

    def reset_current_page_answers(self):
        """ cleans the canvas from the previous questions, so that the canvas can be used again for new questions

        """
        self.current_page_done = False
        self.current_page_buttons = []
        self.current_page_answers = pd.DataFrame(columns=self.df_columns)

    def merge_current_answers_2_time_step_page(self):
        """ merges the answers from 1 group of questions to the dataframe that contains all the answers from the
        current feedback event

        """
        self.current_time_step_answers = pd.concat([self.current_time_step_answers, self.current_page_answers])

    def show_next_button(self, canvas_size=None):
        """ shows the button that allows the participant to move on to the next group of questions, once the current
        group is fully answered

        Parameters
        ----------
        canvas_size : lib.util.Point
        """
        if canvas_size is None:
            canvas_size = self.window.window_size
        self.window.add_button_to_canvas(canvas_id=-1, text='Next', font_size=16, position=canvas_size*0.9,
                                         pad_x=12, command=self.command_next, bg_color=self.window.colors.dark)

    def command_next(self):
        """ function that serves as the 'next' button command (see self.show_next_button method)

        """
        self.current_page_done = True

    def get_ttl_and_subtitle_txt(self, question_group):
        """ returns the title and subtitle corresponding to the question_group

        Parameters
        ----------
        question_group : experimentNao.interaction.performance_of_participant.participant_feedback.QGroup

        Returns
        -------
        Tuple[str, str]
        """
        if question_group == QGroup.BELIEF:
            return self.ttl_txt_b, self.sub_ttl_txt_b
        if question_group == QGroup.GOAL:
            return self.ttl_txt_g, self.sub_ttl_txt_g
        if question_group == QGroup.EMOTION:
            return self.ttl_txt_e, self.sub_ttl_txt_e
        if question_group == QGroup.ACTION:
            return self.ttl_txt_a, self.sub_ttl_txt_a

    def reset_beginning_of_puzzle(self):
        """ reset to the variables to be done at the beggining of the puzzle

        """
        self.n_questions_asked_in_current_puzzle = 0

    # ****************** Periodic Action ******************
    def periodic_action(self):
        """ defines the periodic action of asking for feedback, so that the questions can be asked to the participants
        in a timely periodic manner

        """
        if verbose.VERBOSE.feedback_information:
            print(' [F] Timer is up: ', time.ctime())     # replace with calling the right function
        self.ask_asynchronous_feedback = True      # activate flag that signalizes that feedback must be asked

    def initialize_periodic_action(self):
        """ initializes the necessary variables when the periodic action is reset

        """
        self.ask_asynchronous_feedback = False
        self.thread = threading.Timer(self.periodic_time, self.periodic_action)
        self.thread.start()

    def reset_periodic_action(self):
        """ restarts the periodic action

        """
        self.cancel_periodic_action()
        self.initialize_periodic_action()

    def cancel_periodic_action(self):
        """ cancels the periodic action of requesting help

        """
        if self.thread is not None:
            self.thread.cancel()

    def save_info_of_time_step(self, current_puzzle, sheet_name_extra=''):
        """ saves the answers given by the participant in the current feedback event to the excel file

        Parameters
        ----------
        current_puzzle : int
        sheet_name_extra : str
        """
        self.time_step_answers.append(self.current_time_step_answers)
        sheet_name = self.sheet_names.step + str(current_puzzle) + '.' + str(self.n_questions_asked_in_current_puzzle)
        if isinstance(sheet_name_extra, str):
            sheet_name += sheet_name_extra
        self.save_to_excel_sheet(self.current_time_step_answers, sheet_name)

    # ****************** Save Data ******************
    def save_answer_of_button(self, question, value, index):
        """ saves the answer of the participant corresponding to the button they clicked on. E.g., if the participant
        clicks the button with the number 7, this functions saves that information.

        Parameters
        ----------
        question : experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars
        value : int
        index : int
        """
        for button in self.current_page_buttons[index]:                     # activate all buttons of row
            button['state'] = tk.NORMAL
        self.current_page_buttons[index][value].flash()
        self.current_page_buttons[index][value]['state'] = tk.DISABLED      # deactivate this button
        assert self.current_page_answers.at[index, 'Question'] == question.question_text
        self.current_page_answers.at[index, 'Value'] = value
        self.current_page_answers.at[index, 'Replied'] = True

    def prefill_current_page_answers(self, questions_, quest_number):
        """ prefills the dataframe that will contain the answers of the current page (group of questions)

        Parameters
        ----------
        questions_ : List[experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars]
        quest_number : int
        """
        self.current_page_answers.loc[quest_number] = [str(type(questions_[quest_number].associated_variable).__name__),
                                                       questions_[quest_number].associated_variable.name,
                                                       questions_[quest_number].question_text, None, False]

    def save_to_excel_sheet(self, df, sheet_name):
        """ saves a dataframe to the Excel file with the 'sheet_name'

        Parameters
        ----------
        df : pandas.core.frame.DataFrame
        sheet_name : str
        """
        if self.save_steps_to_excel:
            excel_files.save_df_to_excel_sheet(self.writer, df, sheet_name)

    def set_excel(self, writer_file):
        """ sets up the writer file of the interaction as an attribute to this object, so it is easily accessible

        Parameters
        ----------
        writer_file : pandas.io.excel._openpyxl.OpenpyxlWriter
        """
        self.writer = writer_file

    def get_properties_of_feedback_event(self, feedback_circumstance):
        """ returns the characteristics of the feedback event (see FBEventProperties)

        Parameters
        ----------
        feedback_circumstance : experimentNao.interaction.performance_of_participant.participant_feedback.FBEvent

        Returns
        -------
        experimentNao.interaction.performance_of_participant.participant_feedback.FBEventProperties
        """
        return self.dict_feedback_events[feedback_circumstance]

    def fill_dict_w_properties_of_feedback_event(self):
        """ fills a dict with the characteristics of the feedback event (see FBEventProperties)

        """
        # ask_about_actions, puzzle_end, sheet_name_extra
        self.dict_feedback_events = {
            FBEvent.MID_PUZZLE: FBEventProperties(ask_about_actions=False, puzzle_end=False, sheet_name_extra=''),
            FBEvent.END_PUZZLE: FBEventProperties(ask_about_actions=True, puzzle_end=True,
                                                  sheet_name_extra=self.sheet_names.puzzle_end),
            FBEvent.QUIT: FBEventProperties(ask_about_actions=False, puzzle_end=True,
                                            sheet_name_extra=self.sheet_names.quit),
            FBEvent.HELP: FBEventProperties(ask_about_actions=False, puzzle_end=False, save_in_the_time_step_page=False,
                                            sheet_name_extra=self.sheet_names.help)
        }


class SheetNamesExtras:
    def __init__(self):
        """ prefixes of the sheet names that are used depending on the type of feedback event

        """
        self.step = 'Step '
        self.puzzle_end = '.puzzle_end'
        self.quit = '.quit'
        self.help = '.help'


class FBEventProperties:
    def __init__(self, ask_about_actions, puzzle_end, sheet_name_extra, save_in_the_time_step_page=True,
                 full_screen=None):
        """ characteristics of the Feedback event (see parameters)

        Parameters
        ----------
        ask_about_actions : bool
            whether the questions about the actions should be posed in this feedback event
        puzzle_end : bool
            whether this is a feedback event corresponding to a puzzle end
        sheet_name_extra : str
            prefix of the sheet names of this type of feedback event
        save_in_the_time_step_page : bool
            whether this event should be stored in the page with all the time steps (general results page)
        full_screen : None
            whether questions should be asked covering the fullscreen
        """
        self.ask_about_actions = ask_about_actions
        self.puzzle_ended = puzzle_end
        self.sheet_name_extra = sheet_name_extra
        if full_screen is None:
            full_screen = puzzle_end
        self.full_screen = full_screen
        self.save_in_the_time_step_page = save_in_the_time_step_page


class FBEvent(Enum):    # Feedback Events
    MID_PUZZLE = 1
    END_PUZZLE = 2
    QUIT = 3
    HELP = 4


class QGroup(Enum):     # Questions Group
    BELIEF = 1
    GOAL = 2
    EMOTION = 3
    ACTION = 4
