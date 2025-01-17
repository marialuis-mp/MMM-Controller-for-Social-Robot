import math
import time
import multiprocess as mp

from lib import excel_files
from lib.algorithms.gradient_descent import settings as sett
from lib.algorithms.gradient_descent.output_data import output_data_of_iteration
from lib.algorithms.gradient_descent.parameters2optimise import Parameter2Optimise


def run_gradient_descent(settings: sett.Settings, parameters2optimise: list, cost_function, writer=None, random=None):
    # 1. Initialization parameters
    initialize_parameters(parameters2optimise, settings, random)
    costs_of_iterations = []
    # 1a. Choose multiprocessing or not & 2. Optimisation loop
    if settings.multiprocess:
        with mp.Pool(max(len(parameters2optimise), 4)) as pool:
            costs_of_iterations, df = run_gradient_descent_loop(settings, cost_function, parameters2optimise, costs_of_iterations,
                                                                writer, update_parameters_w_multiprocessing, pool=pool)
    else:
        costs_of_iterations, df = run_gradient_descent_loop(settings, cost_function, parameters2optimise, costs_of_iterations,
                                                            writer, update_parameters_no_multiprocessing, pool=None)

    # 3. End
    if settings.write_to_excel and not settings.save_immediately_to_excel:
        excel_files.save_df_to_excel_sheet(writer, df, 'Optimisation')
    return get_array_w_values_of_parameters(parameters2optimise), costs_of_iterations


def run_gradient_descent_loop(settings: sett.Settings, cost_function, parameters, costs_of_iterations, writer,
                              update_parameters_function, pool=None):
    for i in range(settings.n_iterations):
        if settings.varying_learning_rate:
            settings.current_learning_rate = settings.initial_learning_rate * math.exp(settings.learning_rate_decay * i)
        if settings.verbose >= 1:
            print('\n****** Iteration: ', i, '    Parameters: ', [par.value for par in parameters],
                  '    alpha: ', settings.current_learning_rate, '******')
        # Update the parameters
        old_parameters = parameters.copy()
        st = time.time()
        costs4output, step, gradient_values = update_parameters_function(parameters, settings, cost_function, pool)
        df = output_data_of_iteration(writer, i, old_parameters, step, st, costs4output, cost_function,
                                      costs_of_iterations, None, settings)
        if prune(settings, costs_of_iterations):
            break
    return costs_of_iterations, df


def initialize_parameters(parameters2optimise, settings, random=None):
    for i in range(len(parameters2optimise)):
        assert (isinstance(parameters2optimise[i], Parameter2Optimise))
        if settings.randomly_initialize_parameters:
            parameters2optimise[i].generate_random_value(random)


def update_parameters_w_multiprocessing(parameters, settings, cost_function, pool):
    # steps = [None] * len(parameters)                 # For storage only: will contain the step h used
    # cost_values4output = [None] * len(parameters)    # For storage only: Will contain all costs of this interaction
    # gradient_values = [None] * len(parameters)       # For storage only: will contain the gradient values
    # next_parameters = [0]*len(parameters)
    # Get new values of parameters by computing gradient descent formula

    result = pool.starmap(compute_new_value_of_1_parameter,
                          [(i, parameters, cost_function, settings) for i in range(len(parameters))])

    gradient_values = [el[0] for el in result]
    steps = [el[1] for el in result]
    next_parameters = [el[2] for el in result]
    cost_values4output = [el[3] for el in result]

    # Update the parameters
    for i in range(len(parameters)):
        parameters[i] = next_parameters[i]
    return cost_values4output, steps, gradient_values


def update_parameters_no_multiprocessing(parameters, settings, cost_function, pool_not_used):
    # Get new values of parameters by computing gradient descent formula
    cost_values4output, steps, gradient_values = [], [], []
    for i in range(len(parameters)):
        gradient_value, step, next_par_value, cost_value = compute_new_value_of_1_parameter(i, parameters, cost_function, settings)
        cost_values4output.append(cost_value)
        steps.append(step)
        gradient_values.append(gradient_value)
        parameters[i].set_value_of_parameter(next_par_value)      # Update the parameter value
    return cost_values4output, steps, gradient_values


def compute_new_value_of_1_parameter(i, parameters, cost_function, settings):
    st = time.time()
    if settings.verbose >= 2:
        print('  Parameter ', i + 1, '/', len(parameters))
    cost_value4output = [None] * 2
    gradient_value = gradient_in_one_component(parameters, i, cost_function, cost_value4output, settings)
    new_param_value = parameters[i].value - settings.current_learning_rate * gradient_value
    if settings.verbose >= 3:
        print('      Time for simulation ( parameter', i, ') ', time.time() - st)
    return gradient_value, settings.current_step, new_param_value, cost_value4output


def gradient_in_one_component(parameters, component_number, cost_function, cost_value4output, settings):
    settings.current_step = settings.step
    gradient_value = 0
    while gradient_value == 0 and settings.current_step <= settings.maximum_step:
        gradient_value, forward_cost, previous_cost = compute_gradient(parameters, component_number, cost_function, settings)
        if settings.verbose >= 3:
            print('   Gradient J: ', gradient_value, 'h: ', settings.current_step, 'J(x+h): ', forward_cost, 'J(x-h): ', previous_cost)
        settings.current_step *= 2
    # done: save output and move on
    cost_value4output[0] = round(previous_cost, 4)
    cost_value4output[1] = round(forward_cost, 4)
    return gradient_value


def compute_gradient(parameters, component_number, cost_function, settings):
    # Compute cost for x+h and x-h
    forward_cost = cost_of_close_point(True, parameters, component_number, cost_function, settings)
    previous_cost = cost_of_close_point(False, parameters, component_number, cost_function, settings)
    # Gradient approximation obtained based on (f(x+h)-f(x-h)) / 2h
    gradient_value = (forward_cost - previous_cost) / (2 * settings.current_step)
    return gradient_value, forward_cost, previous_cost


def cost_of_close_point(next_not_previous, parameters, component_number, cost_function, settings):
    parameters = parameters.copy()      # Generate x+h (next_not_previous==True) or x-h
    if next_not_previous:
        parameters[component_number].value = min(parameters[component_number].value + settings.current_step,
                                                 parameters[component_number].maximum_value)
    else:
        parameters[component_number].value = max(parameters[component_number].value - settings.current_step,
                                                 parameters[component_number].minimum_value)
    return cost_function(parameters)    # Compute cost for x+h or x-h


def get_array_w_values_of_parameters(parameters2optimise):
    return [par.value for par in parameters2optimise]


def prune(settings, all_costs):
    if settings.prune_by_epsilon:
        if len(all_costs) > 2:
            if abs(all_costs[-1] - all_costs[-2]) < settings.epsilon and \
                    abs(all_costs[-2] - all_costs[-3]) < settings.epsilon:
                return True
    if settings.prune_half_time:
        if len(all_costs) == int(settings.n_iterations / 2):
            if all_costs[-1] > settings.cost_required_half_time:
                return True
    return False
