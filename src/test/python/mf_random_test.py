import src.main.python.mf as mf
import src.main.python.mf_random as mf_random
import unittest
import numpy as np
from os import path
import pickle
import tempfile


class TestMFRandom(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        M = 10
        N = 10000
        phenotype_list = ['HP:' + str(i + 1) for i in np.arange(M)]
        self.heart_failure = mf.Synergy(disease='heart failure',
                                   phenotype_list=phenotype_list)
        np.random.seed(11)
        self.d = np.random.randint(0, 2, N)
        self.P = np.random.randint(0, 2, M * N).reshape([N, M])

        self.heart_failure.add_batch(self.P, self.d)

    def test_matrix_searchsorted(self):
        ordered = np.arange(24).reshape([2, 3, 4])
        query = np.array([[-1, 4, 8.5], [13.5, 19, 24]])
        idx = mf_random.matrix_searchsorted(ordered, query)
        expected = [[0, 0, 1],
                    [2, 3, 4]]
        self.assertEqual(idx.tolist(), expected)

    def test_create_empirical_distribution(self):
        diag_prevalence = 0.3
        phenotype_prob = np.random.uniform(0, 1, 10)
        sample_per_simulation = 500
        simulations = 100
        distribution = mf_random.create_empirical_distribution(diag_prevalence,
                                                        phenotype_prob,
                                                        sample_per_simulation,
                                                        simulations)
        self.assertEqual(list(distribution.shape), [10, 10, 100])

    def test_p_value_estimate(self):
        ordered = np.arange(24).reshape([2, 3, 4])
        query = np.array([[-1, 4, 8.5], [13.5, 19, 24]])
        idx = mf_random.p_value_estimate(query, ordered, alternative='two.sided')
        expected = [[0, 0.5, 0.5],
                    [1, 0.5, 0]]
        self.assertEqual(idx.tolist(), expected,
                         'two.sided p value estimate '
                         'failed')

        idx = mf_random.p_value_estimate(query, ordered, alternative='left')
        expected = [[0, 0.25, 0.25],
                    [0.5, 1, 1]]
        self.assertEqual(idx.tolist(), expected,
                         'left sided p value estimate '
                         'failed')

        idx = mf_random.p_value_estimate(query, ordered, alternative='right')
        expected = [[1, 1, 0.75],
                    [0.5, 0.25, 0]]
        self.assertEqual(idx.tolist(), expected,
                         'right sided p value estimate '
                         'failed')

        self.assertRaises(ValueError, lambda: mf_random.p_value_estimate(query,
                                            ordered, alternative='e'))

    def test_synergy_random(self):
        disease_prevalence = 0.4
        phenotype_prob = np.random.uniform(0, 1, 10)
        sample_per_simulation = 5000
        S = mf_random.synergy_random(disease_prevalence, phenotype_prob,
                              sample_per_simulation)
        np.testing.assert_almost_equal(S, np.zeros(S.shape), decimal=3)

    def test_serializing_instance(self):
        cases = sum(self.d)
        with open(path.join(self.tempdir, 'test_serializing.obj'), 'wb') as \
                serializing_file:
            pickle.dump(self.heart_failure, serializing_file)

        with open(path.join(self.tempdir, 'test_serializing.obj'), 'rb') as \
                serializing_file:
            deserialized = pickle.load(serializing_file)

        self.assertEqual(deserialized.get_disease(), 'heart failure')
        self.assertEqual(deserialized.get_case_count(), cases)
        self.assertEqual(deserialized.pairwise_synergy().all(),
                         self.heart_failure.pairwise_synergy().all())

    def test_SynergyRandomiser(self):
        randomiser = mf_random.SynergyRandomizer(self.heart_failure)
        # print(self.heart_failure.m1)
        # print(self.heart_failure.m2)
        p_matrix = randomiser.p_value(simulations=100)
        M = p_matrix.shape[0]
        print(p_matrix)
        # print(np.diagonal(p_matrix))
        # print(np.sum(np.triu(p_matrix < 0.05)) / (M * (M - 1) / 2))
        self.assertTrue(np.sum(np.triu(p_matrix < 0.05)) < 2 * 0.05 *
                        (M * (M - 1) / 2))


if __name__ == '__main__':
    unittest.main()