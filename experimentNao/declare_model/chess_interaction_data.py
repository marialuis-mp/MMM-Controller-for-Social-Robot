import math


class ChessInteractionData:
    def __init__(self):
        """ Metrics data regarding the performance of the participants in the chess puzzles. These chess interaction
        data also acts as the vector of real-life data

        """
        self.n_hints = 0                # number of hints
        self.n_wrong_attempts = []      # number of wrong attempts
        self.puzzle_difficulty = 0
        self.proportion_of_moves_revealed = 0
        self.time_2_solve = None
        self.nao_helping = None
        self.nao_offering_rewards = None
        self.reward_given = False
        self.skipped_puzzle = False
        self.df_columns = get_data_titles()

    def reset_data(self):
        """ resets indicators

        """
        self.n_hints = 0
        self.n_wrong_attempts = []
        self.puzzle_difficulty = 0
        self.proportion_of_moves_revealed = 0
        self.time_2_solve = None
        self.nao_helping = None
        self.nao_offering_rewards = None
        self.reward_given = False
        self.skipped_puzzle = False

    def get_as_array(self):
        """ returns all the indicators as an array

        Returns
        -------
        List[int]
        """
        return [self.n_hints, str(self.n_wrong_attempts), self.puzzle_difficulty,
                self.proportion_of_moves_revealed, self.time_2_solve, self.nao_helping, self.nao_offering_rewards,
                self.reward_given, self.skipped_puzzle]

    def get_from_data_frame(self, df):
        """ gets the attributes of the object from a dataframe

        Parameters
        ----------
        df : pandas.core.frame.DataFrame

        Returns
        -------
        experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        raw_data = []
        for col in self.df_columns:
            raw_data.append(df.iloc[0][col])
        self.fill_data(*raw_data)
        return self

    def normalise_mid_step(self):
        """ normalises the values of the indicators in a discrete time step that corresponds to the middle of a puzzle

        """
        self.n_hints *= 2
        self.n_wrong_attempts *= 2
        self.time_2_solve *= 2

    def fill_data(self, number_of_hints: int = None, number_of_wrong_attempts: list = None,
                  puzzle_difficulty: int = None, prop_moves_revealed: float = None, time_2_solve: float = None,
                  nao_helping: bool = None, nao_offering_reward: bool = None, reward_given: bool = None,
                  skipped: bool = None):
        """ fills the attributes of the object with the values given as argument

        Parameters
        ----------
        number_of_hints : Union[numpy.int64, None, int, None, None]
        number_of_wrong_attempts : Union[str, None, List[int], None, None]
        puzzle_difficulty : Union[numpy.int64, int]
        prop_moves_revealed : Union[numpy.float64, float, int]
        time_2_solve : Union[numpy.float64, float, int]
        nao_helping : Union[numpy.bool_, bool]
        nao_offering_reward : Union[numpy.bool_, bool]
        reward_given : Union[numpy.bool_, None, bool, None, None]
        skipped : Union[numpy.bool_, bool]
        """
        if number_of_hints is not None:
            self.n_hints = number_of_hints
        if number_of_wrong_attempts is not None:
            if isinstance(number_of_wrong_attempts, str):
                self.n_wrong_attempts = number_of_wrong_attempts[1:-1].split(',')
                self.n_wrong_attempts = [int(ele if len(ele) > 0 else 0) for ele in self.n_wrong_attempts]
            else:
                self.n_wrong_attempts = number_of_wrong_attempts
        if puzzle_difficulty is not None:
            self.puzzle_difficulty = puzzle_difficulty
        if prop_moves_revealed is not None:
            self.proportion_of_moves_revealed = prop_moves_revealed
        if time_2_solve is not None:
            self.time_2_solve = time_2_solve
        if nao_helping is not None:
            self.nao_helping = nao_helping
        if nao_offering_reward is not None:
            self.nao_offering_rewards = nao_offering_reward
        if reward_given is not None:
            self.reward_given = reward_given
        if skipped is not None:
            self.skipped_puzzle = skipped


def interpolate_between_two_points(data_previous: ChessInteractionData, data_after: ChessInteractionData):
    """ interpolates the indicators between two objects of ChessInteractionData, returning a third one with the
    interpolated values.

    Parameters
    ----------
    data_previous :
    data_after :

    Returns
    -------

    """
    new_point = ChessInteractionData()
    if sum(data_previous.n_wrong_attempts) == sum(data_after.n_wrong_attempts):
        n_wrong_attempts = data_previous.n_wrong_attempts
    else:
        n_wrong_attempts = [(sum(data_previous.n_wrong_attempts) + sum(data_after.n_wrong_attempts)) / 2]
    new_point.fill_data(number_of_hints=interpolate_attribute(data_previous, data_after, 'n_hints'),
                        number_of_wrong_attempts=n_wrong_attempts,
                        puzzle_difficulty=data_after.puzzle_difficulty,
                        prop_moves_revealed=interpolate_attribute(data_previous, data_after,
                                                                  'proportion_of_moves_revealed'),
                        time_2_solve=interpolate_attribute(data_previous, data_after, 'time_2_solve'),
                        nao_helping=data_after.nao_helping, nao_offering_reward=data_after.nao_offering_rewards,
                        reward_given=data_previous.reward_given, skipped=data_previous.skipped_puzzle)
    return new_point


def interpolate_attribute(data_previous: ChessInteractionData, data_after: ChessInteractionData, attrname):
    """ interpolates one indicator of two objects of ChessInteractionData, returning the interpolated indicator

    Parameters
    ----------
    data_previous : ChessInteractionData
    data_after : ChessInteractionData
    attrname : str

    Returns
    -------

    """
    return math.ceil((getattr(data_previous, attrname) + getattr(data_after, attrname)) / 2)


def get_data_titles():
    """ Names of the columns of the dataframes that hold the indicators of "chess interaction data".

    Returns
    -------
    Tuple[str, str, str, str, str, str, str, str, str]
    """
    return ('n_hints', 'n_wrong_attempts', 'puzzle_difficulty', 'proportion_of_moves_revealed', 'time_2_solve',
            'nao_helping', 'nao_offering_rewards', 'reward_given', 'skipped_puzzle')
