import time
import argparse
from experimentNao import participant
from experimentNao.model_ID import identification as id_
from experimentNao.model_ID.configs import model_configs, train_test_config, id_cog_modes, overall_config
from experimentNao.model_ID.decision_making import identification_dm as id_dm
from experimentNao.model_ID.data_processing import excel_data_processing
from lib.init_my_random import init_random


if __name__ == '__main__':
    CLI = argparse.ArgumentParser()
    CLI.add_argument('--model_config', nargs='*', type=str, default=['SIMPLEST_W_BIAS'])
    CLI.add_argument('--training_set', nargs='*', type=str, default=['A'])
    CLI.add_argument('--id_cog_mode', nargs='*', type=str, default=['SEP_PER_2'])
    CLI.add_argument('--simple_dyn', nargs='*', type=str, default=['YES'])
    CLI.add_argument('--incremental', nargs='*', type=str, default=['YES'])
    CLI.add_argument('--n_horizon', nargs='*', type=int, default=[1])
    CLI.add_argument('--participant', nargs='*', type=str, default=[None])
    CLI.add_argument('--normalise_rld', nargs='*', type=str, default=['NO'])
    args = CLI.parse_args()
    # Parameters and Configs
    my_random = init_random(seed=42)
    participant_id = participant.participant_identifier if args.participant[0] is None else args.participant[0]
    overall_id_config = overall_config.IDConfig(model_configs.ModelConfigs[args.model_config[0]],
                                                participant_id,
                                                id_cog_modes.IdCogModes[args.id_cog_mode[0]],
                                                train_test_config.TrainingSets[args.training_set[0]],
                                                False if args.simple_dyn[0] == 'NO' else True,
                                                False if args.incremental[0] == 'NO' else True,
                                                n_horizon=args.n_horizon[0], cog_2_id=True,
                                                normalise_rld_mid_steps=False if args.normalise_rld[0] == 'NO' else True,
                                                online_data_sets_division=True)
    writer, reader_files, n_puzzles = excel_data_processing.preprocess(overall_id_config)
    # Identification
    st = time.time()
    if overall_id_config.cog_2_id:
        id_.train_and_validate_cognitive_module(writer, reader_files, n_puzzles, my_random, overall_id_config,
                                                delft_blue=False, short_mode=False)
    else:
        id_.train_and_valid_dm(writer, reader_files, n_puzzles, overall_id_config, my_random,
                               train_mode=id_dm.OptMode.GENETIC_ALGORITHM)
    print('TOTAL TIME: ', time.time() - st)
