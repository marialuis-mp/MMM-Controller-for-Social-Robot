import pandas as pd

from experimentNao.behaviour_controllers.mbc.aux_functions import get_all_fast_dyn_vars
from lib import excel_files


class WriteControllerToExcel:
    def __init__(self, tom_model, actions, id_config):
        """ handles the output of the controller information to the Excel.

        Parameters
        ----------
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        actions : List[experimentNao.behaviour_controllers.robot_action.RobotAction]
        id_config : experimentNao.model_ID.configs.overall_config.IDConfig
        """
        self.writer = None
        self.all_variables = None
        self.columns_df_steps = ['Step'] + self.get_vars_names(tom_model) + \
                                ['reward_given', 'puzzle_difficulty', 'from_question']
        self.columns_df_costs = ['reward_given', 'puzzle_difficulty']
        self.df_steps = pd.DataFrame(columns=self.columns_df_steps)
        self.df_costs = pd.DataFrame(columns=self.columns_df_costs)
        self.initialize_df_costs(actions)
        self.simple_dynamics = id_config.simple_dynamics
        self.file_name = id_config.get_model_id_file_name()
        self.step = 0
        self.puzzle_current_difficulty = None

    def write_mid_puzzle(self, puzzle_counter, puzzle_current_difficulty, updated_from_question):
        """ writes the output to the Excel file at the mid-puzzle discrete time step

        Parameters
        ----------
        puzzle_counter : int
        puzzle_current_difficulty : int
        updated_from_question : bool
        """
        self.puzzle_current_difficulty = puzzle_current_difficulty
        if self.simple_dynamics:
            self.add_info_to_df_steps(puzzle_counter, reward_given=None, updated_from_question=updated_from_question)
        else:
            self.add_info_to_df_steps(puzzle_counter, reward_given=None, updated_from_question=updated_from_question,
                                      next_puzzle_diff=self.puzzle_current_difficulty, one_data_point=False)
        self.write_to_excel()

    def write_end_of_puzzle(self, all_actions, selected_action, puzzle_counter):
        """ writes the output to the Excel file at the end-of-puzzle discrete time step

        Parameters
        ----------
        all_actions : List[experimentNao.behaviour_controllers.robot_action.RobotAction]
        selected_action : experimentNao.behaviour_controllers.robot_action.RobotAction
        puzzle_counter : int
        """
        self.add_info_action_costs(all_actions, puzzle_counter)
        if self.simple_dynamics:
            self.add_info_to_df_steps(puzzle_counter, selected_action.give_reward, updated_from_question=False)
        else:
            self.add_info_to_df_steps(puzzle_counter, selected_action.give_reward, updated_from_question=False,
                                      next_puzzle_diff=selected_action.puzzle_difficulty_level, one_data_point=False)
        self.write_to_excel()
        self.step = 0

    def initialize_df_costs(self, actions):
        """ initializes the dataframe that will contain the costs of each action in each puzzle. The dataframe will be
        filled during the interaction, and then saved to the Excel file

        Parameters
        ----------
        actions : List[experimentNao.behaviour_controllers.robot_action.RobotAction]
        """
        data = []
        for action in actions:
            data.append([action.give_reward, action.puzzle_difficulty_level])
        self.df_costs = pd.DataFrame(data=data, columns=self.columns_df_costs)

    def add_info_to_df_steps(self, puzzle_counter, reward_given, updated_from_question=False,
                             next_puzzle_diff=None, one_data_point=True):
        """ adds information to the dataframe that contains the information of the controller (discrete time step,
        the mental states of the participants and whether they were measured or estimated, and the chosen action)

        Parameters
        ----------
        puzzle_counter : int
        reward_given : Union[None, bool, None]
        updated_from_question : bool
        next_puzzle_diff : Union[None, None, None, None]
        one_data_point : bool
        """
        step = puzzle_counter + (self.step / 10)
        if one_data_point:
            new_data = [step] + [var.value for var in self.all_variables] \
                       + [reward_given, self.puzzle_current_difficulty, updated_from_question]
            to_add = pd.DataFrame(data=[new_data], columns=self.columns_df_steps)
        else:
            new_data1 = [step] + [var.values[-2] for var in self.all_variables] \
                        + [reward_given, self.puzzle_current_difficulty, updated_from_question]
            new_data2 = [step] + [var.values[-1] for var in self.all_variables] \
                        + [None, next_puzzle_diff, updated_from_question]
            to_add = pd.DataFrame(data=[new_data1, new_data2], columns=self.columns_df_steps)
        self.df_steps = pd.concat([self.df_steps, to_add])
        self.step += 1

    def add_info_action_costs(self, actions, puzzle_counter):
        """ adds costs of taking each action at the end of the current puzzle to self.df_costs

        Parameters
        ----------
        actions : List[experimentNao.behaviour_controllers.robot_action.RobotAction]
        puzzle_counter : int
        """
        new_column = [action.cost for action in actions]
        self.df_costs.insert(len(self.df_costs.columns), 'Puzzle ' + str(puzzle_counter), new_column)

    def write_to_excel(self):
        """ write the two dataframes (costs and steps information)

        """
        excel_files.save_df_to_excel_sheet(self.writer, self.df_steps, 'Step by step')
        excel_files.save_df_to_excel_sheet(self.writer, self.df_costs, 'Costs')

    def set_excel(self, writer):
        """ initializes the writer Excel file

        Parameters
        ----------
        writer : pandas.io.excel._openpyxl.OpenpyxlWriter
        """
        self.writer = writer
        self.write_file_name()

    def write_file_name(self):
        """ writes the name of the input file used to load the tom model to the output file

        """
        df = pd.DataFrame(data=[self.file_name], columns=['file name'])
        excel_files.save_df_to_excel_sheet(self.writer, df, 'File name')

    def get_vars_names(self, tom_model):
        """ returns the names of the all the variables in the tom model

        Parameters
        ----------
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn

        Returns
        -------
        List[str]
        """
        self.all_variables = get_all_fast_dyn_vars(tom_model)
        vars_names = []
        for var in self.all_variables:
            vars_names.append(str(type(var).__name__)[0:3] + '-' + var.name)
        return vars_names
