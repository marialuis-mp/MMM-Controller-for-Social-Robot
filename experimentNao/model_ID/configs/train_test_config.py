from enum import Enum


def get_train_valid_steps(training_sets):
    """ declares the datapoints used as training and as test data for the preliminary participants

    Parameters
    ----------
    training_sets : TrainingSets
        the training set

    Returns
    -------

    """
    if training_sets == TrainingSets.A:
        train_steps = [2, 3, 4, 5, 8, 9, 10, 11, 14, 15, 17, 18, 20, 21, 22, 23, 25, 26, 29, 30, 31, 32, 35, 36, 38,
                       40, 41, 43, 44, 46, 47, 48, 50, 52, 53, 54, 56, 57, 59, 60, 63, 64, 66, 67, 68, 70, 72, 73, 75,
                       77, 78, 80, 82, 83, 84, 86, 88, 89, 91, 92, 93, 95, 96, 97]
        test_steps = [1, 6, 7, 12, 13, 16, 19, 24, 27, 28, 33, 34, 39, 42, 45, 49, 51, 55, 58, 61, 62, 65, 69, 71, 76,
                      79, 81, 85, 87, 90, 94, 98]
    elif training_sets == TrainingSets.B:
        train_steps = [1, 3, 4, 5, 8, 9, 10, 12, 13, 14, 16, 17, 19, 21, 23, 24, 26, 27, 29, 30, 32, 33, 35, 36, 39, 40,
                       41, 43, 44, 45, 47, 49, 50, 52, 54, 55, 57, 58, 59, 60, 62, 63, 65, 67, 68, 69, 71, 73, 75, 76,
                       78, 80, 82, 83, 85, 86, 88, 89, 91, 92, 94, 95, 96, 97]
        test_steps = [2, 6, 7, 11, 15, 18, 20, 22, 25, 28, 31, 34, 38, 42, 46, 48, 51, 53, 56, 61, 64, 66, 70, 72, 77,
                      79, 81, 84, 87, 90, 93, 98]
    else:
        train_steps, test_steps = None, None
    return train_steps, test_steps


class TrainingSets(Enum):
    """ Groups of training/test data. The chosen set defines which datapoints are used as training and which ones are
    used as test data in the identification of the model

    """
    A = 1
    B = 2
    C = 3
    UNDEFINED = 4
