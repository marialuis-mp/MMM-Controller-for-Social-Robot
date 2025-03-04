import numpy as np
from sklearn.linear_model import LinearRegression


def generate_average_data_per_diff(N_difficulties, difficulties_by_number, rld_metrics_by_diff):
    max_diff = N_difficulties - 1
    data_for_df = []
    for diff in range(max_diff + 1):
        data_for_df.append([get_average(difficulties_by_number[diff])])
        for rld in rld_metrics_by_diff:
            data_for_df[-1].append(get_average(rld[diff]))
    return interpolation_of_missing_data(data_for_df, max_diff)


def interpolation_of_missing_data(data_for_df, max_diff):
    for diff in range(max_diff + 1):
        if data_for_df[diff][0] is None:
            if diff != 0 and diff != max_diff:
                for i in range(len(data_for_df[diff])):
                    data_for_df[diff][i] = (data_for_df[diff + 1][i] + data_for_df[diff - 1][i]) / 2
    for diff in range(max_diff + 1):
        if diff == 0:
            if data_for_df[diff][0] is None:
                for i in range(len(data_for_df[diff])):
                    data_for_df[diff][i] = 2 * data_for_df[diff + 1][i] - data_for_df[diff + 2][i]
        elif diff == max_diff:
            if data_for_df[diff][0] is None:
                for i in range(len(data_for_df[diff])):
                    data_for_df[diff][i] = 2 * data_for_df[diff - 1][i] - data_for_df[diff - 2][i]
    return data_for_df


def get_average(array_of_values):
    return sum(array_of_values) / len(array_of_values) if len(array_of_values) > 0 else None


def print_arrays_and_averages(array_of_values, name):
    print('\t', name, '\t\tAverage: {}\t\t Values: {}'.format(get_average(array_of_values),
                                                              array_of_values))


def get_var_name(var):
    for name, value in locals().items():
        if value is var:
            return name


def normalize_vector(array_, max_value):
    if max_value == 0:
        return array_
    return [ele / max_value for ele in array_]


def extract_value_of_wrong_attempts(wrong_attempts):
    return sum([int(v if len(v) > 0 else 0) for v in wrong_attempts[1:-1].split(', ')])


def normalise_rld_metrics_per_diff(metrics_by_diff, rld_names_by_diff):
    metrics_by_diff_normalised = []
    for i in range(len(metrics_by_diff)):
        x_array = []    # difficulty
        y_array = []    # metrics
        for diff in range(len(metrics_by_diff[i])):
            for y in metrics_by_diff[i][diff]:
                x_array.append(diff)
                y_array.append(y)
        X = np.array(x_array).reshape(-1, 1)
        y = np.array(y_array)
        reg = LinearRegression().fit(X, y)
        metrics_by_diff_normalised.append([])
        for diff in range(len(metrics_by_diff[i])):
            metrics_by_diff_normalised[i].append(reg.coef_[0] * diff + reg.intercept_)
        print(rld_names_by_diff[i], metrics_by_diff_normalised[i])
    return metrics_by_diff_normalised


def generate_data_for_df_w_normalise_rld_metrics_per_diff(metrics_by_diff_normalised, data):
        new_data = []
        for i_diff in range(len(data)):
            this_diff_data = [data[i_diff][0]] + [ele[i_diff] for ele in metrics_by_diff_normalised]
            new_data.append(this_diff_data)
        return new_data
