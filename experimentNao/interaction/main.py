from experimentNao import participant
from experimentNao.behaviour_controllers.best_configs_per_participant import get_best_configs_per_participant
from experimentNao.interaction import interaction_manager
from experimentNao.interaction.interaction_settings import InteractionSettings
from experimentNao.model_ID.configs import model_configs, overall_config as oc

if __name__ == '__main__':
    interaction_settings = InteractionSettings(interaction_mode=interaction_manager.InteractionMode.TRAINING,
                                               demo=False, with_nao=False, say_hello=False, speak_instructions=False,
                                               ask_for_feedback=True, save_excel=True, second_screen=False,
                                               lichess_db=True)
    id_mode, model_config, train_set, n_h = get_best_configs_per_participant(participant.participant_identifier)
    print('id_mode {} \t model_config {} \t train_set {} \tn_h {}'.format(id_mode, model_config, train_set, n_h))
    id_config = oc.IDConfig(model_config, participant.participant_identifier, id_mode, train_set,
                            simplified_dynamics=True, incremental=True, n_horizon=n_h, cog_2_id=True)

    # ************************************ Possible runs ************************************
    # Uncomment one of the following options:
    # interaction_settings.set_settings_demo()
    # interaction_settings.set_settings_training_1st()
    # interaction_settings.set_settings_training_2nd()
    interaction_settings.set_settings_mbc()
    # interaction_settings.set_settings_alternative()

    # To delete
    interaction_settings.with_nao = False
    interaction_settings.save_excel = False
    interaction_settings.second_screen = False

    # ************************************ Run interaction ************************************
    if interaction_settings.interaction_mode == interaction_manager.InteractionMode.TRAINING:   # in first 2 sessions,
        id_config.model_config = model_configs.ModelConfigs.DEFAULT                             # use model default
    interaction_manager.Interaction(interaction_settings, id_config)
