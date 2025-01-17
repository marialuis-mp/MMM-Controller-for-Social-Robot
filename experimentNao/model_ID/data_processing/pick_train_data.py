import random


def get_settings(simple_dynamics, n_horizon):
    """ returns the settings object regarding how to generate the training and test data, according to the input
    arguments

    Parameters
    ----------
    simple_dynamics : bool
    n_horizon : int

    Returns
    -------
    experimentNao.model_ID.data_processing.pick_train_data.Settings
    """
    if simple_dynamics and n_horizon == 2:
        return Settings(first_data_point_included=False, last_data_point_included=False)
    else:
        return get_default_settings()


def get_default_settings():
    """ returns the default settings regarding how to generate the training and test data

    Returns
    -------
    experimentNao.model_ID.data_processing.pick_train_data.Settings
    """
    return Settings(first_data_point_included=False, last_data_point_included=True)


class Settings:
    def __init__(self, len_groups: int = 3, percentage_train: float = 2/3,
                 separate_by_interactions: bool = False, last_data_point_included: bool = True,
                 first_data_point_included: bool = True, remove_first_data_point_of_puzzle: bool = False):
        """ settings object regarding how to generate the training and test data

        Parameters
        ----------
        len_groups : int
            number of puzzles in each group of puzzles during the interaction sessions used to collect data. In each
            group, the difficulty of the puzzle is kept constant
        percentage_train : float
            percentage of the datapoints used to train the model
        separate_by_interactions : bool
            separate the training and test data by interactions (for eaxmple)
        last_data_point_included : bool
        first_data_point_included : bool
        remove_first_data_point_of_puzzle : bool
        """
        self.len_of_groups = len_groups
        self.percentage_train = percentage_train
        self.separate_by_interactions = separate_by_interactions
        self.last_data_point_included = last_data_point_included
        self.first_data_point_included = first_data_point_included
        self.remove_first_data_point_of_puzzle = remove_first_data_point_of_puzzle

    def get_number_of_data_points(self, list_of_data_points):
        """ gets the number of total data points

        Parameters
        ----------
        list_of_data_points :

        Returns
        -------

        """
        number_to_remove = 0 + (1 if self.last_data_point_included else 0) + (1 if self.first_data_point_included else 0)
        return len(list_of_data_points) - number_to_remove


def select_train_valid_data(data_points_by_iteration, settings, random_=None):
    """ selects the data points that will be used as training and test data

    Parameters
    ----------
    data_points_by_iteration : List[List[float]]
    settings : experimentNao.model_ID.data_processing.pick_train_data.Settings
    random_ : random.Random

    Returns
    -------
    Tuple[List[int], List[int], List[float]]
    """
    random_ = random_ if random_ is not None else random
    all_data_points_aggregated, valid_data_points_indices = get_valid_data_points(data_points_by_iteration, settings)
    if settings.separate_by_interactions:
        train_indices, test_indices = separate_data_points_by_slicing(len(valid_data_points_indices), settings)
    else:
        train_indices, test_indices = pick_data_points_evenly_distributed(len(valid_data_points_indices), settings, random_)
    train_data_points = [valid_data_points_indices[i] for i in train_indices]
    test_data_points = [valid_data_points_indices[i] for i in test_indices]
    return train_data_points, test_data_points, all_data_points_aggregated


def get_valid_data_points(datapoints_by_interaction, settings):
    """ returns the indices of the datapoints that can be used as training or testing data. For example, depending on
    the settings, the first or the last data point of each interaction may not be used as a datapoint, thus it is not
    returned.

    Parameters
    ----------
    datapoints_by_interaction : List[List[float]]
    settings : experimentNao.model_ID.data_processing.pick_train_data.Settings

    Returns
    -------
    Tuple[List[float], List[int]]
    """
    aggregated_dps = []
    indices_of_invalid_dps = []
    for data_points_of_this_interaction in datapoints_by_interaction:
        if not settings.first_data_point_included:
            if not settings.remove_first_data_point_of_puzzle:  # if remove 1st data point of puzzle, 1st data point overall is deleted (not even considered as invalid)
                indices_of_invalid_dps.append(len(aggregated_dps))   # add index of first data point of this interaction
        aggregated_dps.extend(data_points_of_this_interaction)
        if not settings.last_data_point_included:
            indices_of_invalid_dps.append(len(aggregated_dps)-1)     # add index of last data point of this interaction
    indices_of_valid_dps = []
    for i in range(len(aggregated_dps)):           # only append if
        if i not in indices_of_invalid_dps:                     # 1. Not in invalid indices (first or last of each interaction)
            if settings.remove_first_data_point_of_puzzle:    # 2. Not the first of puzzle (if this setting option is on)
                if '.0' not in str(aggregated_dps[i]):
                    indices_of_valid_dps.append(i)
            else:
                indices_of_valid_dps.append(i)
    return aggregated_dps, indices_of_valid_dps


def separate_data_points_by_slicing(total_number_of_data_points, settings):
    """ separates the data points by choosing the first m for train data (where m is the ammount of data points to be
    allocated for training data) and the last (n-m) for test data

    Parameters
    ----------
    total_number_of_data_points : int
    settings : experimentNao.model_ID.data_processing.pick_train_data.Settings

    Returns
    -------

    """
    number_of_training_data_points = round(total_number_of_data_points * settings.percentage_train)
    training_data_points = range(number_of_training_data_points)   # First n data points are for training
    test_data_points = range(number_of_training_data_points, total_number_of_data_points) # Last m data points are for test
    return training_data_points, test_data_points


def pick_data_points_evenly_distributed(total_number_data_points, settings, random_):
    """ divides the datapoint into training and test by picking (as much as possible) the same quantity of training data
    from each group of puzzles

    Parameters
    ----------
    total_number_data_points : int
    settings : experimentNao.model_ID.data_processing.pick_train_data.Settings
    random_ : random.Random

    Returns
    -------
    Tuple[List[int], List[int]]
    """
    len_groups = settings.len_of_groups
    n_complete_groups = total_number_data_points // len_groups
    n_train_data_points = round(total_number_data_points * settings.percentage_train)
    train_data_points, val_data_points = distribute_data_points_train_and_test(len_groups, n_complete_groups,
                                                                           n_train_data_points, random_)
    distribute_remaining_data_points(train_data_points, val_data_points, n_train_data_points, total_number_data_points)
    return train_data_points, val_data_points


def distribute_data_points_train_and_test(len_of_groups, n_complete_groups, n_train_data_points, random_):
    """ performs an initial evenly distribution of the train and testing data points, by taking
    "n_train_data_points_p_group" of each group for training, and the rest for testing. This function only goes through
    the "n_complete_groups" groups of puzzles that were completed. The puzzles from uncompleted groups (the last puzzles
    of each session) are not distributed in this function.

    Parameters
    ----------
    len_of_groups : int
    n_complete_groups : int
    n_train_data_points : int
    random_ : random.Random

    Returns
    -------
    Tuple[List[int], List[int]]
    """
    n_train_data_points_p_group = n_train_data_points // n_complete_groups
    training_data_points, testing_data_points = [], []
    for i in range(n_complete_groups):
        train_in_group = random_.sample(range(len_of_groups), n_train_data_points_p_group)
        for j in range(len_of_groups):
            data_point_number = i * len_of_groups + j
            if j in train_in_group:
                training_data_points.append(data_point_number)
            else:
                testing_data_points.append(data_point_number)
    return training_data_points, testing_data_points


def distribute_remaining_data_points(train_data_points, test_data_points, n_train_data_points, total_number_data_points):
    """ distributes the remaining data points (the ones that were not in complete groups) into training and test data
    points. This is done by 1st) allocating the remaining data points as training, until the number of training data
    points is "n_train_data_points"; 2) allocating the remaining as test data points


    Parameters
    ----------
    train_data_points : List[int]
    test_data_points : List[int]
    n_train_data_points : int
    total_number_data_points : int
    """
    while len(train_data_points) + len(test_data_points) < total_number_data_points:
        next_data_point_number = len(train_data_points) + len(test_data_points)
        if len(train_data_points) < n_train_data_points:
            train_data_points.append(next_data_point_number)
        else:
            test_data_points.append(next_data_point_number)
