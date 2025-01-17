from experimentNao.declare_model.modules import declare_cognitive_module
from experimentNao.model_ID.configs import model_configs


def declare_questions(model, model_config):
    """ declares the questions to be asked to the participants about their mental states

    Parameters
    ----------
    model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        model that contains the variables about which the questions will be asked
    model_config : experimentNao.model_ID.configs.model_configs.ModelConfigs
        the configuration of the model

    Returns
    -------
    Tuple[List[experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars], List[experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars], List[experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars], List[experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsActions]]
    """
    questions_b, questions_g, questions_e, questions_a = list(), list(), list(), list()
    included_vars = model_configs.get_model_configuration(model_config)
    s_vars, hidden_vars = declare_cognitive_module.return_vars_2_id_and_hidden_vars(model.cognitive_module.get_beliefs(),
                                                                                    included_vars)
    beliefs_dict = model.cognitive_module.beliefs_dict
    goals_dict = model.cognitive_module.goals_dict
    emotions_dict = model.cognitive_module.emotions_dict
    actions = model.decision_making_module.action_selector.outputs
    for var in hidden_vars:
        if var.name in beliefs_dict.keys():
            beliefs_dict.pop(var.name)

    add_question_to_list(questions_b, beliefs_dict, 'game difficulty', 'the difficulty of the game is:',
                         verbal_terms=('too easy', 'suitable', 'too difficult'))
    add_question_to_list(questions_b, beliefs_dict, 'nao helping', 'Nao is helping me.')
    add_question_to_list(questions_b, beliefs_dict, 'made progress', 'I made progress.')
    add_question_to_list(questions_b, beliefs_dict, 'nao offering rewards', 'Nao is offering me rewards.')

    add_question_to_list(questions_g, goals_dict, 'change game difficulty', 'change the difficulty of the game.',
                         verbal_terms=('to easier', 'keep', 'to more difficult'))
    add_question_to_list(questions_g, goals_dict, 'quit game', 'quit.')
    add_question_to_list(questions_g, goals_dict, 'get help', 'be helped by Nao.')
    add_question_to_list(questions_g, goals_dict, 'get reward', 'receive a reward from Nao.')
    add_question_to_list(questions_g, goals_dict, 'skip puzzle', 'skip this puzzle.',
                         end_of_puzzle_question='have skipped this puzzle')

    add_question_to_list(questions_e, emotions_dict, 'confident/frustrated', 'frustrated.')
    add_question_to_list(questions_e, emotions_dict, 'interested/bored', 'bored.')
    add_question_to_list(questions_e, emotions_dict, 'happy/unhappy', 'unhappy.')

    if included_vars.action_change_diff:
        questions_a = [QuestionsActions(actions[1], 'Ask Nao for an easier game.'),
                       QuestionsActions(actions[2], 'Ask Nao for a more difficult game.')]
    else:
        questions_a = []

    return questions_b, questions_g, questions_e, questions_a


def add_question_to_list(list_of_questions, dict_, var_name, question, verbal_terms=None, end_of_puzzle_question=None):
    """ used to declare one question and add it to the list of questions

    Parameters
    ----------
    list_of_questions : Union[List, List[experimentNao.interaction.performance_of_participant.feedback_questions.QuestionsStateVars]]
    dict_ : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    var_name : str
    question : str
    verbal_terms : Union[Tuple[str, str, str], None]
    end_of_puzzle_question : Union[None]
    """
    if var_name in dict_:
        if verbal_terms is None:
            list_of_questions.append(QuestionsStateVars(dict_[var_name], question,
                                                        end_of_puzzle_question=end_of_puzzle_question))
        else:
            list_of_questions.append(QuestionsStateVars(dict_[var_name], question, verbal_terms=verbal_terms,
                                                        end_of_puzzle_question=end_of_puzzle_question))


def declare_titles():
    """ declares the titles to each group of questions

    Returns
    -------
    Tuple[str, str, str, str]
    """
    ttl_txt_b = 'I believe that...'
    ttl_txt_g = 'I would like to...'
    ttl_txt_e = 'I feel...'
    ttl_txt_a = 'You can ask Nao to change the difficulty of the game, if you want to.'
    return ttl_txt_b, ttl_txt_g, ttl_txt_e, ttl_txt_a


def declare_subtitles():
    """ declares the subtitles to each group of questions

    Returns
    -------
    Tuple[str, str, str, str]
    """
    sub_ttl_txt_4_questions = 'Please select from 0 to 10 how much you agree with the following expressions'
    sub_ttl_txt_b = sub_ttl_txt_4_questions + '.'
    sub_ttl_txt_g = sub_ttl_txt_4_questions + ' regarding your desires.'
    sub_ttl_txt_e = sub_ttl_txt_4_questions + '.'
    sub_ttl_txt_a = 'Nao may or may not consider your request.'
    return sub_ttl_txt_b, sub_ttl_txt_g, sub_ttl_txt_e, sub_ttl_txt_a


class Question:
    def __init__(self, associated_variable, question, number_of_buttons, verbal_terms, numbered_buttons, pad,
                 require_answer, default_answer):
        """

        Parameters
        ----------
        associated_variable : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief,
                                    lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal,
                                    lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotions,
                                    experimentNao.declare_model.modules.declare_decision_making.ActionChessGame]
        question : str
        number_of_buttons : int
        verbal_terms : tuple[str]
        numbered_buttons : bool
        pad : float
        require_answer : bool
        default_answer : str
        """
        self.associated_variable = associated_variable
        self.question_text = question
        self.verbal_terms = verbal_terms
        self.number_of_buttons = number_of_buttons
        self.pad = pad
        self.numbered_buttons = numbered_buttons
        self.require_answer = require_answer
        if not self.require_answer:
            self.default_answer = default_answer

    def get_question_txt(self, end_of_puzzle=False):
        """ get the question text

        Parameters
        ----------
        end_of_puzzle : whether question is being asked at the end of the puzzle

        Returns
        -------

        """
        return self.question_text


class QuestionsStateVars(Question):
    def __init__(self, associated_variable, question, end_of_puzzle_question=None, number_of_buttons=11, pad=0.27,
                 verbal_terms=('completely disagree', 'disagree', 'no opinion', 'agree', 'completely agree'),
                 numbered_buttons=True, require_answer=True, default_answer=None):
        """ question where the variable associated to the question is a fast dynamics state variable (belief, goal, or
        emotion)

        Parameters
        ----------
        associated_variable : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        question : str
        end_of_puzzle_question : Union[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, str, None, None]
        number_of_buttons : int
        pad : float
        verbal_terms : Union[Tuple[str, str, str], Tuple[str, str, str, str, str], Tuple[str, str, str], Tuple[str, str, str], Tuple[str, str, str, str, str], Tuple[str, str, str], Tuple[str, str, str], Tuple[str, str, str, str, str], Tuple[str, str, str], Tuple[str, str, str], Tuple[str, str, str], Tuple[str, str, str, str, str], Tuple[str, str, str], Tuple[str, str, str], Tuple[str, str, str, str, str], Tuple[str, str, str, str, str], Tuple[str, str, str, str, str], Tuple[str, str, str]]
        numbered_buttons : bool
        require_answer : bool
        default_answer : Union[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        """
        super().__init__(associated_variable, question, number_of_buttons, verbal_terms, numbered_buttons, pad,
                         require_answer, default_answer)
        self.end_of_puzzle_question = end_of_puzzle_question if end_of_puzzle_question is not None else question

    def get_question_txt(self, end_of_puzzle=False):
        """ get the question text

        Parameters
        ----------
        end_of_puzzle : whether question is being asked at the end of the puzzle

        Returns
        -------

        """
        return '...' + (self.question_text if not end_of_puzzle else self.end_of_puzzle_question)


class QuestionsActions(Question):
    def __init__(self, associated_variable, question, number_of_buttons=2, pad=0.45,
                 verbal_terms=('No ', 'Yes'), numbered_buttons=False, require_answer=False, default_answer=0):
        """ questions where the associated variable is an action

        Parameters
        ----------
        associated_variable : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame
        question : str
        number_of_buttons : int
        pad : float
        verbal_terms : Tuple[str, str]
        numbered_buttons : bool
        require_answer : bool
        default_answer : int
        """
        super().__init__(associated_variable, question, number_of_buttons, verbal_terms, numbered_buttons, pad,
                         require_answer, default_answer)



