import pickle
import argparse
import os.path
from mf_random import SynergyRandomizer
import logging.config

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'log_config.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)


def main():
    HOME_DIR = os.path.expanduser('~')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file path',
                        action='store', dest='input_path')
    parser.add_argument('-o', '--out', help='output directory',
                        action='store', dest='out_dir', default=HOME_DIR)
    parser.add_argument('-n', '--n_per_simulation',
                        help='sample size per simulation. ignore if to use '
                             'the same size in original data',
                        dest='n_per_run', type=int, default=None)
    parser.add_argument('-N', '--N_SIMULATIONS', help='total simulations',
                        dest='N_SIMULATIONS', type=int, default=1000)
    parser.add_argument('-v', '--verbose', help='print messages',
                        dest='verbose', action='store_true', default=False)
    args = parser.parse_args()
    if args.verbose:
        print(args)

    if args.input_path is None:
        print('no input is defined')
        parser.print_help()
        exit(1)

    if not os.path.exists(args.input_path):
        print('input file does not exist')
        parser.print_help()
        exit(1)

    with open(args.input_path, 'rb') as in_file:
        synergies = pickle.load(in_file)
        logger.info('number of diseases to run simulations for {}'.format(
            len(synergies)))

    run(synergies, per_simulation=args.n_per_run,
        simulations=args.N_SIMULATIONS, verbose=args.verbose,
        dir=args.out_dir)


def run(disease_synergy_map, per_simulation, simulations, verbose, dir):
    for disease, synergy in disease_synergy_map.items():
        if disease != '428':
            pass
        randmizer = SynergyRandomizer(synergy)
        if verbose:
            print('start calculating p values for {}'.format(disease))
        p = randmizer.p_value(per_simulation, simulations)
        p_filepath = os.path.join(dir, disease + '_p_value_.obj')
        with open(p_filepath, 'wb') as f:
            pickle.dump(p, file=f, protocol=2)

        distribution_file_path = os.path.join(dir, disease +
                                              '_distribution.obj')
        with open(distribution_file_path, 'wb') as f2:
            pickle.dump(randmizer.empirical_distribution, file=f2, protocol=2)

        if verbose:
            print('saved p values for {}'.format(disease))


if __name__=='__main__':
    main()