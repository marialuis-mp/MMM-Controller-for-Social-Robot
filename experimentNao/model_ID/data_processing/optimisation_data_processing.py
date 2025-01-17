import copy
import statistics
import time
import pandas as pd


# ######################################################################################################################
#                                    Data processing after entire identification
# ######################################################################################################################
def process_final_data_from_identification(df_all_runs, parameters_list):
    """ Processes the information of one gradient descent identification, composed by N runs,
    each one composed by M iterations. The information processed contains the best costs, the best parameters, the
    indices of the runs where the best costs were achieved, and dataframes with the information already organized.

    Parameters
    ----------
    df_all_runs : pandas.core.frame.DataFrame
        data frame with the model_id_out from all the iterations of the identification procedure. The model_id_out include the
        final cost, final values of each parameter, and the costs of each iteration
    parameters_list : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        list of the parameters that were identified

    Returns
    -------
    Tuple[pandas.core.arrays.numpy_.PandasArray, List[int], List[bool], pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
    """
    final_costs = df_all_runs['Final cost'].array  # final cost of each run
    indices_opt_costs_processed, indices_optimal_costs = get_indices_of_best_runs_of_optimisation(final_costs)
    identified_params = find_identified_parameters(df_all_runs, indices_opt_costs_processed)
    df_optimal_sets_of_params = df_all_runs.iloc[indices_opt_costs_processed]
    df_everything = merge_info_into_1_df(df_all_runs, identified_params, df_optimal_sets_of_params, parameters_list)
    return final_costs, indices_opt_costs_processed, identified_params, df_optimal_sets_of_params, df_everything


def merge_info_into_1_df(df_all_runs, identified_params, df_optimal_sets_of_params, parameters_list):
    """

    Parameters
    ----------
    df_all_runs : pandas.core.frame.DataFrame
        data frame with the model_id_out from all the iterations of the identification procedure. The model_id_out include the
        final cost, final values of each parameter, and the costs of each iteration
    identified_params : List[bool]
        list with the information if each parameter was identified. For each parameter in 'parameters_list', the same
        index of 'identified_parameters' contains True if that parameter was identified, and False if it wasn't.
    df_optimal_sets_of_params : pandas.core.frame.DataFrame
        dataframe with the set of the best parameters. For each set (each row), the dataframe contains the final cost,
        the parameter values, and the costs of all iterations
    parameters_list : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        list of the parameters that were identified

    Returns
    -------
    pandas.core.frame.DataFrame
    """
    blank_df = pd.DataFrame([[None] * len(df_all_runs.columns)], columns=df_all_runs.columns)
    df_names_of_params, df_identified_params = copy.deepcopy(blank_df), copy.deepcopy(blank_df)
    for i in range(len(parameters_list)):
        df_names_of_params['Param ' + str(i)] = parameters_list[i].name
        df_identified_params['Param ' + str(i)] = identified_params[i]
    return pd.concat([df_names_of_params, df_identified_params, df_optimal_sets_of_params, blank_df, df_all_runs])


def get_indices_of_best_runs_of_optimisation(final_costs_array, maximum_elements=5, indices_of_lowest_k_elements=None,
                                             percentage_of_min_cost_accepted=0.10):
    """

    Parameters
    ----------
    final_costs_array : pandas.core.arrays.numpy_.PandasArray
        array with the final cost of each gd run
    maximum_elements : int
        maximum number of 'best elements' that whose indices be returned
    indices_of_lowest_k_elements : Union[List[int], None]
        list with the indices of the k best (minimum) costs in 'costs'
    percentage_of_min_cost_accepted : float
        percentage of error between the best overall cost and the other k costs. For example, if best cost is C, and
        percentage=0.10, only the runs with a cost less than C*(1+percentage) = 1.1*C will be returned.

    Returns
    -------
    Union[List[int], Tuple[List[int], List[int]]]
    """
    if indices_of_lowest_k_elements is None:
        indices_of_lowest_k_elements = get_indices_of_lowest_k_elements(final_costs_array, maximum_elements)
    best_costs = [final_costs_array[i] for i in indices_of_lowest_k_elements]
    min_cost = min(best_costs)
    filtered_indices_of_lowest_k_elements = []
    for i in indices_of_lowest_k_elements:         # Makes sure that only indices within percentage_of_min_cost_accepted
        if final_costs_array[i] < (1 + percentage_of_min_cost_accepted) * min_cost:             # of the minimum cost are listed
            filtered_indices_of_lowest_k_elements.append(i)
    if len(filtered_indices_of_lowest_k_elements) == 0:                       # for the case where minimum cost is 0 and
        filtered_indices_of_lowest_k_elements = indices_of_lowest_k_elements              # the processed list is empty
    return filtered_indices_of_lowest_k_elements, indices_of_lowest_k_elements


def get_indices_of_lowest_k_elements(array, k):
    """ Returns the indices of the k elements with the best (minimum) cost

    Parameters
    ----------
    array : pandas.core.arrays.numpy_.PandasArray
        array with all the elements, from which the best k will be found
    k : int
        number of the smallest elements that are to be found

    Returns
    -------
    List[int]
    """
    return sorted(range(len(array)), key=lambda sub: array[sub])[:k]


def find_identified_parameters(df_all_runs, indices_of_minimum_costs):
    """

    Parameters
    ----------
    df_all_runs : pandas.core.frame.DataFrame
        data frame with the model_id_out from all the iterations of the identification procedure. The model_id_out include the
        final cost, final values of each parameter, and the costs of each iteration
    indices_of_minimum_costs : List[int]
        list with the indices of the best (minimum) costs in 'costs'

    Returns
    -------
    List[bool]
    """
    identified_parameters = []
    number_of_parameters = sum(1 for column in list(df_all_runs.columns) if 'param' in column.lower())
    for i in range(number_of_parameters):
        parameter_values = df_all_runs['Param ' + str(i)].array
        success, identified = check_if_parameter_was_identified(parameter_values, indices_of_minimum_costs)
        identified_parameters.append(identified)
    if not success:
        print('warning: std_dev was not computed')
    return identified_parameters


def check_if_parameter_was_identified(parameter_values, indices_with_minimum_costs, threshold_std_dev=0.15):
    """ checks if the values of a parameter theta that were identified in the iterations with the best scores are
    similar to each other, i.e., if the parameter was really identified or if it did not influence the cost function at
    all.

    Parameters
    ----------
    parameter_values : all the values of the parameter that were identified in all iterations
    indices_with_minimum_costs : iterations where the best costs were achieved
    threshold_std_dev : maximum standard deviation between the best identified values for the parameter for the
    parameter to be considered identified.

    Returns
    -------

    """
    best_values_of_par = [parameter_values[i] for i in indices_with_minimum_costs]
    try:
        std_dev = statistics.stdev(best_values_of_par)
    except statistics.StatisticsError:
        return False, False
    if std_dev < threshold_std_dev:
        return True, True
    else:
        return True, False


def print_overall_id_info(costs, indices_w_min_costs, identified_parameters, parameters_list, df_w_everything, verbose):
    """ prints the information of one gradient descent identification, composed by N runs,
    each one composed by M iterations.

    Parameters
    ----------
    costs : pandas.core.arrays.numpy_.PandasArray
        array with the final cost of each gd run
    indices_w_min_costs : List[int]
        list with the indices of the best (minimum) costs in 'costs'
    identified_parameters : List[bool]
        list with the information if each parameter was identified. For each parameter in 'parameters_list', the same
        index of 'identified_parameters' contains True if that parameter was identified, and False if it wasn't.
    parameters_list : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        list of the parameters that were identified
    df_w_everything : pandas.core.frame.DataFrame
        data frame with all the model_id_out from the identification procedure (including the best sets of parameters and
        corresponding costs on top)
    verbose : int
    """
    params_values = extract_parameters_values_from_dataframe(len(parameters_list), df_w_everything)
    if verbose > 0:
        print('\n\tMin costs: ', [costs[i] for i in indices_w_min_costs],
              '\n\tIDed parameters: ', identified_parameters,
              '\n\tParameters: ', [round(ele, 2) for ele in params_values])


def extract_parameters_values_from_dataframe(n_parameters, df_w_everything):
    """ extract the values of the parameters that achieved the best cost from the dataframe that contains all the
    information of the gradient descent identification.

    Parameters
    ----------
    n_parameters : int
        number of parameters that were identified
    df_w_everything : pandas.core.frame.DataFrame
        data frame with all the model_id_out from the identification procedure (including the best sets of parameters and
        corresponding costs on top)

    Returns
    -------
    List[float]
    """
    parameters = []
    for i in range(n_parameters):
        param = df_w_everything.iloc[2]['Param ' + str(i)]
        parameters.append(param if isinstance(param, float) else 0)
    return parameters


# ######################################################################################################################
#                                    Data processing after 1 iteration of gradient descent
# ######################################################################################################################
def print_info_of_1_run(run, costs, parameters, starting_time, n_runs, verbose):
    """ prints the model_id_out of a run of the gradient descent identification

    Parameters
    ----------
    run : int
        number of the current run of the gradient descent identification
    costs : List[numpy.float64]
        costs obtained in the all the iterations of the current run
    parameters : List[numpy.float64]
        values of the optimal parameters found in the current run
    starting_time : float
    n_runs : int
        total number of runs of the gradient descent identification
    verbose : int
    """
    if verbose > 0:
        if verbose > 1:
            print('**** Start: ', run, '\n Costs: ', costs, '\n Parameters: ',
                  [round(ele, 2) for ele in parameters], '\n Final cost: ', costs[-1], '\n Time: ',
                  time.time() - starting_time)
            print('Number parameters:', len(parameters))
        else:
            print_progress_in_fifths(run, n_runs)


def print_progress_in_fifths(run, n_runs, n_milestones=5):
    """

    Parameters
    ----------
    run : int
        number of the current run of the gradient descent identification
    n_runs : int
        total number of runs of the gradient descent identification
    n_milestones : int
    """
    n_milestones = n_milestones if n_runs < 100 else n_milestones * 2
    milestone = int(1 / n_milestones * n_runs)
    if run % milestone == 0:
        milestone_reached = run // milestone
        print('progress: [' + '-' * milestone_reached + ' ' * (n_milestones - milestone_reached) + ']     '
              + str(run / n_runs * 100) + '%')