import numpy as np
import mf
import multiprocessing


class SynergyRandomizer:

    def __init__(self, synergy):
        self.case_N = synergy.case_N
        self.control_N = synergy.control_N
        self.m1 = synergy.m1
        self.m2 = synergy.m2
        self.S = synergy.pairwise_synergy()
        print('randomizer initiated')

    def p_value(self, sampling=100):
        """
        Estimate p values for each observed phenotype pair by comparing the
        observed synergy score with empirical distributions created by random
        sampling.
        :param sampling: sampling times
        :return: p value matrix
        """
        TOTAL = self.case_N + self.control_N
        diag_prob = np.array([self.case_N, self.control_N]) / TOTAL
        phenotype_prob = np.sum(self.m1[:, 0:1], axis=1) / TOTAL
        sample_per_simulation = TOTAL
        simulations = sampling
        empirical_distribution = create_empirical_distribution(diag_prob,
                                                               phenotype_prob,
                                                               sample_per_simulation,
                                                               simulations)
        return p_value_estimate(self.S, empirical_distribution, 'two.sided')



def p_value_estimate(observed, empirical_distribution, alternative='two.sided'):
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

    :param ordered:
    :param query:
    :return:
    """
    (m, n) = query.shape
    assert m == ordered.shape[0]
    assert n == ordered.shape[1]
    idx = np.zeros([m, n])
    for i in np.arange(m):
        for j in np.arange(n):
            idx[i,j] = np.searchsorted(ordered[i, j, :], query[i, j], side)
    return idx


def create_empirical_distribution(diag_prob, phenotype_prob,
                                  sample_per_simulation, simulations):
    M = len(phenotype_prob)
    S_distribution = np.zeros([M, M, simulations])
    # # TODO: the following could be synchronized
    # for i in np.arange(simulations):
    #     print('start simulation: {}'.format(i))
    #     S_distribution[:, :, i] = synergy_random(diag_prob, phenotype_prob,
    #                                      sample_per_simulation)
    # TODO: refactor the messy implementation
    workers = []
    empirical_distribution = np.zeros([M, M, simulations])
    for i in np.arange(simulations):
        workers.append(multiprocessing.Process(
            target=synergy_random_multiprocessing,
            args=(diag_prob, phenotype_prob, sample_per_simulation,
                  i, empirical_distribution)))
    for i in np.arange(simulations):
        workers[i].start()

    for i in np.arange(simulations):
        workers[i].join()

    return S_distribution


def synergy_random(diag_prob, phenotype_prob, sample_size):
    mocked = mf.Synergy(disease='mocked', phenotype_list=np.arange(len(
        phenotype_prob)))
    BATCH_SIZE = 1000
    M = len(phenotype_prob)
    total_batches = int(np.ceil(sample_size / BATCH_SIZE))
    for i in np.arange(total_batches):
        if (i == total_batches - 1):
            actual_batch_size = sample_size - BATCH_SIZE * (i - 1)
        else:
            actual_batch_size = BATCH_SIZE
        d = np.random.choice([0, 1], actual_batch_size, replace=True,
                             p=diag_prob)
        # the following is faster than doing choice with loops
        P = np.random.uniform(0, 1, actual_batch_size*M).reshape([
            actual_batch_size, M])
        ones_idx = (P < phenotype_prob.reshape([1, M]))
        P = np.zeros_like(P)
        P[ones_idx] = 1
        mocked.add_batch(P, d)
    return mocked.pairwise_synergy()

def synergy_random_multiprocessing(diag_prob, phenotype_prob, sample_size, i,
                                   empirical_distribution):
    synergy = synergy_random(diag_prob, phenotype_prob, sample_size)
    empirical_distribution[:, :, i] = synergy