from experimentNao.data_analysis.pre_process_data.bulk_processing_of_data import extract_value_of_wrong_attempts
from experimentNao.model_ID.data_processing import excel_data_processing as edp


def get_metric_in_step(performance_df, step, metric):
    return edp.get_value_of_row_that_satisfies_condition_in_another_column(performance_df, 'Step', step, metric)


def get_var_value_from_step(step_df, var_name):
    return edp.get_value_of_row_that_satisfies_condition_in_another_column(step_df, 'Var Name', var_name, 'Value')


def get_final_metric_in_a_puzzles(performance_df, puzzle_number, metric):
    steps_in_puzzle = list(range(5, -1, -1))
    for step in steps_in_puzzle:
        step_number = float(puzzle_number) + (step * 0.1)
        try:
            metric_value = get_metric_in_step(performance_df, step_number, metric)
            if metric == 'n_wrong_attempts':
                metric_value = extract_value_of_wrong_attempts(metric_value)
            return metric_value
        except IndexError:
            pass


def get_first_metric_in_a_puzzles(performance_df, puzzle_number, metric):
    metric_value = get_metric_in_step(performance_df, float(puzzle_number), metric)
    if metric == 'n_wrong_attempts':
        metric_value = extract_value_of_wrong_attempts(metric_value)
    return metric_value
