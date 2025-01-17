import path_config
from experimentNao import folder_path


def get_name_of_file_w_metrics(participant_name_id):
    return 'Metrics_participant_' + participant_name_id


def get_name_of_metric_file_2_write(participant_name_id):
    return str(get_name_of_metric_file_2_read(participant_name_id))


def get_name_of_metric_file_2_read(participant_name_id):
    return get_name_of_folder() / (get_name_of_file_w_metrics(participant_name_id) + '.xlsx')


def get_name_of_folder():
    return folder_path.output_folder_path / 'participants_rld'


def get_names_of_sheets(normalisation: bool):
    return 'Normalization RLD' if normalisation else 'RLD metrics per diff'
