import numpy as np
import mf
import multiprocessing
import os
import os.path
import logging.config


log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'log_config.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)


class SynergyRandomizer:

    def __init__(self, synergy):
        self.logger = logger
        self.case_N = synergy.case_N
        self.control_N = synergy.control_N
        self.m1 = synergy.m1
        self.m2 = synergy.m2
        self.S = synergy.pairwise_synergy()
        self.empirical_distribution=np.zeros([1, 1])
        logger.info('randomizer initiated')

    def p_value(self, per_simulation=None, simulations=100):
        """
        Estimate p values for each observed phenotype pair by comparing the
        observed synergy score with empirical distributions created by random
        sampling.
        :param sampling: sampling times
        :return: p value matrix
        """
        TOTAL = self.case_N + self.control_N
        diag_prob = self.case_N / TOTAL
        phenotype_prob = np.sum(self.m1[:, 0:1], axis=1) / TOTAL
        if per_simulation is None:
            per_simulation = TOTAL
        self.empirical_distribution = create_empirical_distribution(diag_prob,
                                                               phenotype_prob,
                                                               per_simulation,
                                                               simulations,
                                                               self.logger)
        return p_value_estimate(self.S, self.empirical_distribution,
                                'two.sided')


def p_value_estimate(observed, empirical_distribution, alternative='two.sided'):
    """
    Estimate P value of observed synergy scores from the empirical distribution.
    :param observed: a M x M matrix of observed synergy scores. M is the
     number of phenotypes being analyzed
    :param empirical_distribution: a M x M x n. Each vector of the M x M
    matrix represent an empirical distribution with size n.
    :param alternative: alternative hypothesis
    :return: a M x M matrix of which each element represent the p value for
    the observed synergy score of the phenotype pair.
    """

    M1, N1 = observed.shape
    M2, N2, P = empirical_distribution.shape
    assert M1 == M2
    assert N1 == N2
    ordered = np.sort(empirical_distribution, axis=-1)
    center = np.mean(empirical_distribution, axis=-1)
    if alternative == 'two.sided':
        return matrix_searchsorted(ordered, center - np.abs(observed - center),
                                   side='right') / P + \
               1 - \
               matrix_searchsorted(ordered, center + np.abs(observed - center),
                                   side='left') / P
    elif alternative == 'left':
        return matrix_searchsorted(ordered, observed, side='right') / P
    elif alternative == 'right':
        return 1 - matrix_searchsorted(ordered, observed, side='left') / P
    else:
        raise ValueError


def matrix_searchsorted(ordered, query, side='left'):
    """
    A matrix implementation of Numpy searchsorted. It searches the 3D array
    for each element of the 2D query, and returns the indices as a
    2D array.
    :param ordered: an ordered 3D array with shape M x M x n
    :param query: a 2D array with shape M x M
    :return: a 2D array, each element represent the index where the query
    element should be inserted into the vector at the corresponding place in
    the ordered 3D array.
    """
    (m, n) = query.shape
    assert m == ordered.shape[0]
    assert n == ordered.shape[1]
    idx = np.zeros([m, n])
    for i in np.arange(m):
        for j in np.arange(n):
            idx[i,j] = np.searchsorted(ordered[i, j, :], query[i, j], side)
    return idx


def create_empirical_distribution(diag_prevalence, phenotype_prob,
                                  sample_per_simulation, SIMULATION_SIZE,
                                  logger=None):
    """
    Create empirical distributions for each phenotype pair.
    :param diag_case_prob: a scalar for the prevalence of the diagnosis under
    study
    :param phenotype_prob: a size M vector for the prevalence of the phenotypes
    under study
    :param sample_per_simulation: number of samples for each simulation
    :param SIMULATION_SIZE: total simulations
    :return: a M x M x SIMULATION_SIZE matrix for the empirical distributions
    """
    if logger is not None:
        logger.info('number of CPU: {}'.format(os.cpu_count()))
    workers = multiprocessing.Pool()
    results = [workers.apply_async(synergy_random, args=(diag_prevalence,
                                                        phenotype_prob,
                                                        sample_per_simulation,
                                                        i))
         for i in np.arange(SIMULATION_SIZE)]
    workers.close()
    workers.join()
    assert(len(results) == SIMULATION_SIZE)
    empirical_distribution = np.stack([res.get() for res in results], axis=-1)

    return empirical_distribution


def synergy_random(disease_prevalence, phenotype_prob, sample_size,
                   seed=None):
    """
    Simulate disease condition and phenotype matrix with provided
    probability distributions and calculate the resulting synergy.
    :param disease_prevalence: a scalar representation of the disease prevalence
    :param phenotype_prob: a size M vector representing the observed
    prevalence of phenotypes
    :param sample_size: number of cases to simulate
    :return: a M x M matrix representing the pairwise synergy from the
    simulated disease conditions and phenotype profiles.
    """
    if seed is not None:
        np.random.seed(seed)
    mocked = mf.Synergy(disease='mocked', phenotype_list=np.arange(len(
        phenotype_prob)))
    BATCH_SIZE = 100
    M = len(phenotype_prob)
    total_batches = int(np.ceil(sample_size / BATCH_SIZE))
    logger.debug('start simulation: {} '.format(seed))
    for i in np.arange(total_batches):
        logger.debug(f'add batch {i} -> simulation {seed}')
        if i == total_batches - 1:
            actual_batch_size = sample_size - BATCH_SIZE * (i - 1)
        else:
            actual_batch_size = BATCH_SIZE
        d = (np.random.uniform(0, 1, actual_batch_size) <
             disease_prevalence).astype(int)
        # the following is faster than doing choice with loops
        P = np.random.uniform(0, 1, actual_batch_size*M).reshape([
            actual_batch_size, M])
        P = (P < phenotype_prob.reshape([1, M])).astype(int)
        mocked.add_batch(P, d)
    logger.debug('end simulation {}'.format(seed))
    return mocked.pairwise_synergy()