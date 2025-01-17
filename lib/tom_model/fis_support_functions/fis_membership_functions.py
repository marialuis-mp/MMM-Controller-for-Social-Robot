import skfuzzy as fuzz
import numpy as np


def create_membership_functions(terms, value_range, mf_type='default'):
    if mf_type == 'default':
        mf_array = create_default_mf(terms, value_range)
    elif mf_type == 'binary':
        if len(terms) != 2 and len(terms) != 3:
            raise ValueError('For binary mf, the number of terms should be 2 (or 3)')
        mf_array = create_binary_mf(terms, value_range)
    elif mf_type == 'neg and pos':
        mf_array = create_pos_neg_mf(terms[0], terms[1], terms[2],  value_range)
    elif mf_type == 'sig and bell':
        mf_array = create_sigmoid_and_bell_mf(terms, value_range)
    return mf_array


def create_sigmoid_and_bell_mf(terms, value_range):
    min_value = value_range[0]
    max_value = value_range[1]
    range_value = max_value - min_value
    mfs_width = range_value / (len(terms)-1)

    mf_array = np.zeros((len(terms), 3))
    sigmoid_width = 50     #todo: experiment with this value
    slope_bell = 2
    for i in range(len(terms)):
        if i == 0:
            mf_array[i][0] = min_value + mfs_width/2
            mf_array[i][1] = -1 * sigmoid_width
        elif i == len(terms)-1:
            mf_array[i][0] = max_value - mfs_width/2
            mf_array[i][1] = sigmoid_width
        else:
            mf_array[i][0] = mfs_width/4
            mf_array[i][1] = slope_bell
            mf_array[i][2] = min_value + i * mfs_width
    return mf_array


def create_binary_mf(terms, value_range):
    min_value = value_range[0]
    max_value = value_range[1]
    range_value = max_value - min_value
    medium_point = (min_value + max_value) / 2

    mf_array = np.zeros((len(terms), 4))    # 4 because trapezoid mf required 4 values

    trap_size = 0.1             # size of trapezoid base
    away_from_centre = 0.05     # how much after middle value the 1st MF finishes (or how much before it the 2nd starts)
    mf_array[0] = (min_value, min_value, min_value + range_value*trap_size, medium_point + away_from_centre)
    mf_array[-1] = (medium_point - away_from_centre, max_value - range_value * trap_size, max_value, max_value)
    if len(terms) == 3:
        mf_array[1] = (-away_from_centre*2, -away_from_centre, away_from_centre, away_from_centre*2)
    return mf_array


def create_default_mf(terms,  value_range):
    min_value = value_range[0]
    max_value = value_range[1]
    number_sets = len(terms)
    mf_array = np.zeros((number_sets, 3))
    set_step = (max_value-min_value) / (number_sets - 1)   # translation between consecutive sets
    for i in range(number_sets):
        if i == 0:
            mf_array[i] = (min_value, min_value, min_value + set_step)
        elif i == number_sets - 1:
            mf_array[i] = (max_value - set_step, max_value, max_value)
        else:
            mf_array[i][1] = mf_array[i-1][1] + set_step
            mf_array[i][0] = mf_array[i][1] - set_step
            mf_array[i][2] = mf_array[i][1] + set_step
        # create membership function
    return mf_array


def create_pos_neg_mf(neg_terms, neutral_terms, positive_terms,  value_range):
    min_value = value_range[0]
    max_value = value_range[1]
    # For negative terms
    mf_array_neg = create_default_mf(neg_terms + neutral_terms, [min_value, 0])
    last_row_neg_mfs = mf_array_neg[-1]
    mf_array_neg = np.delete(mf_array_neg, (-1), axis=0)     # ignore last mf
    # For positive terms
    mf_array_pos = create_default_mf(neutral_terms + positive_terms, [0, max_value])
    first_row_pos_mfs = mf_array_pos[0]
    mf_array_pos = np.delete(mf_array_pos, (0), axis=0)  # ignore first mf
    # For neutral terms
    mf_neutral = np.array([[last_row_neg_mfs[0], 0, first_row_pos_mfs[-1]]])

    mf_array = np.concatenate((mf_array_neg, mf_neutral, mf_array_pos,), axis=0)

    return mf_array


def attribute_membership_functions(variable, terms, mf_array, mf_type):
    list_of_terms = []
    for term in terms:
        if isinstance(term, list):
            for element in term:
                assert(isinstance(element, str))
                list_of_terms.append(element)
        else:
            assert (isinstance(term, str))
            list_of_terms.append(term)
    terms = list_of_terms
    if mf_type == 'default':
        for i in range(len(terms)):
            variable[terms[i]] = fuzz.trimf(variable.universe, mf_array[i])
    elif mf_type == 'binary':
        for i in range(len(terms)):
            variable[terms[i]] = fuzz.trapmf(variable.universe, mf_array[i])
    elif mf_type == 'sig and bell':
        for i in range(len(terms)):
            if i == 0 or i == len(terms) - 1:
                variable[terms[i]] = fuzz.sigmf(variable.universe, mf_array[i][0], mf_array[i][1])
            else:
                variable[terms[i]] = fuzz.gbellmf(variable.universe, mf_array[i][0], mf_array[i][1], mf_array[i][2])
    else:
        for i in range(len(terms)):
            variable[terms[i]] = fuzz.trimf(variable.universe, mf_array[i])
    return variable
