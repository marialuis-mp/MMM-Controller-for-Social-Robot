import time

import pandas as pd

from lib import excel_files


def add_data_of_it_to_df(df, values, data_columns, iteration_number):
    if iteration_number == 0:
        return pd.DataFrame([values], columns=data_columns)
    else:
        df = pd.concat([df,  pd.DataFrame([values], columns=data_columns)])
        return df


def output_data_of_iteration(writer, i, old_parameters, step, starting_time, costs4output, cost_function,
                             costs_of_iterations, df, settings):
    to_print = '  Time for iteration ' + str(i) + ': ' + str(time.time() - starting_time)
    if settings.write_to_excel:
        output_parameters = ['%.3f' % elem for elem in old_parameters]
        values, data_columns = process_data_of_iteration_for_output(output_parameters, costs4output, step)
        if settings.save_immediately_to_excel:
            df = output_data_of_iteration_to_excel(writer, i, values, data_columns, sheet_name='Iterations')
        else:
            df = add_data_of_it_to_df(df, values, data_columns, i)
    if settings.compute_cost_at_end_of_iteration:
        costs_of_iterations.append(round(cost_function(old_parameters), 3))
        to_print = to_print + '   Cost: ' + str(costs_of_iterations[-1])
    if settings.verbose >= 1:
        print(to_print)
    return df


def process_data_of_iteration_for_output(current_parameters, values_of_cost_function, step):
    data_columns = []
    values = []
    assert len(current_parameters) == len(values_of_cost_function)
    for i in range(len(current_parameters)):
        data_columns = data_columns + ['Parameter ' + str(i), 'Step h_' + str(i),
                                       'Cost in x_' + str(i) + '-h', 'Cost in x_' + str(i) + '+h']
        values = values + [current_parameters[i]] + [step[i]] + values_of_cost_function[i]
    return values, data_columns


def output_data_of_iteration_to_excel(writer, iteration_number, values, data_columns, sheet_name):
    if iteration_number == 0:
        df = pd.DataFrame([values], columns=data_columns)
        df.to_excel(writer, engine='xlsxwriter', sheet_name=sheet_name)
        writer.save()
    else:
        df = excel_files.add_data_to_existing_excel_sheet(writer, values_to_add=values, data_columns_names=data_columns,
                                                          sheet_name=sheet_name)
        return df
