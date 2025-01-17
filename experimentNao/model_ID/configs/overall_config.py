from experimentNao import folder_path
from lib import excel_files
from experimentNao.model_ID.configs import model_configs, train_test_config, id_cog_modes


class IDConfig:
    def __init__(self, model_config: model_configs.ModelConfigs, participant_id: str,
                 id_cog_mode: id_cog_modes.IdCogModes, training_set: train_test_config.TrainingSets,
                 simplified_dynamics, incremental, n_horizon: int, cog_2_id: bool,
                 normalise_rld_mid_steps=False, online_data_sets_division=None):
        """ this object holds the configuration options related to the identification procedure, such as the model
        configuration, the identification procedure, and the design choices regarding the dynamics of the model,
        assumptions, and approximations.

        Parameters
        ----------
        model_config : experimentNao.model_ID.configs.model_configs.ModelConfigs
        participant_id : str
        id_cog_mode : experimentNao.model_ID.configs.id_cog_modes.IdCogModes
        training_set : experimentNao.model_ID.configs.train_test_config.TrainingSets
        simplified_dynamics : bool
        incremental : bool
        n_horizon : int
        cog_2_id : bool
        normalise_rld_mid_steps : bool
        online_data_sets_division : bool
        """
        self.id_cog_mode = id_cog_mode
        self.participant_id = participant_id
        self.model_config = model_config
        self.training_set = training_set
        self.simple_dynamics = simplified_dynamics
        self.incremental = incremental
        self.n_horizon = n_horizon
        self.cog_2_id = cog_2_id
        self.online_data_sets_division = online_data_sets_division
        self.normalise_rld_mid_steps = normalise_rld_mid_steps

    def set_incremental(self, incremental):
        """ sets the incremental parameter

        Parameters
        ----------
        incremental : bool
        """
        self.incremental = incremental

    def get_model_id_file_name(self):
        """ generates the name of the output file of the identification procedure depending on the chosen configurations

        Returns
        -------
        str
        """
        txt_settings = 'model_id_' + self.participant_id
        if self.cog_2_id:
            id_mode_txt = self.id_cog_mode.name.lower() if isinstance(self.id_cog_mode, id_cog_modes.IdCogModes) else self.id_cog_mode
            train_set_txt = '' if self.training_set == train_test_config.TrainingSets.UNDEFINED else self.training_set.name
            # create text
            txt_settings += '_' + self.model_config.name.lower()
            txt_settings += '_incr' if self.incremental else ''
            txt_settings += '_SpDyn' if self.simple_dynamics else ''
            txt_settings += '_nh2' if (self.simple_dynamics and self.n_horizon == 2) else ''
            txt_settings += '_NormRLD' if self.normalise_rld_mid_steps else ''
            txt_settings += ('_' + id_mode_txt) if len(id_mode_txt) > 0 else ''
            txt_settings += ('_' + train_set_txt) if len(train_set_txt) > 0 else ''
            return txt_settings
        else:
            return txt_settings + '_dm'

    def get_model_id_file_path(self):
        """ returns the path of the output file of the identification procedure.

        Returns
        -------

        """
        return folder_path.output_folder_path / 'model_id_out' / (self.get_model_id_file_name() + '.xlsx')

    def get_model_id_file(self):
        """ returns the output file of the identification procedure. This function can be called when the file already
        exists (i.e., to read the file).

        Returns
        -------

        """
        return excel_files.get_excel_file(self.get_model_id_file_path())

    def get_model_id_file_from_overall_path(self, general_path):
        """ returns the output file of the identification procedure, which is located in folder "general_path".
        This function can be called when the file already exists (i.e., to read the file).

        Parameters
        ----------
        general_path : str
            path of the folder where the file is

        Returns
        -------

        """
        return excel_files.get_excel_file(general_path + self.get_model_id_file_name() + '.xlsx')
