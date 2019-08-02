import src.main.python.mf as mf
import src.main.python.mf_random as mf_random
import unittest
import numpy as np
from os import path
import pickle
import tempfile
import multiprocessing
import datetime


class TestMFRandom(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.heart_failure = mf.Synergy(disease='heart failure',
                                   phenotype_list=['HP:001', 'HP:002',
                                                   'HP:003',
                                                   'HP:004', 'HP:005',
                                                   'HP:006', 'HP:007',
                                                   'HP:008'])
        np.random.seed(1)
        self.d = np.random.randint(0, 2, 10000)
        self.P = np.random.randint(0, 2, 80000).reshape([10000, 8])

        self.heart_failure.add_batch(self.P, self.d)

    def test_matrix_searchsorted(self):
        ordered = np.arange(24).reshape([2, 3, 4])
        query = np.array([[-1, 4, 8.5], [13.5, 19, 24]])
        idx = mf_random.matrix_searchsorted(ordered, query)
        expected = [[0, 0, 1],
                    [2, 3, 4]]
        self.assertEqual(idx.tolist(), expected)

    def test_create_empirical_distribution(self):
        diag_prob = np.array([0.3, 0.7])
        phenotype_prob = np.random.uniform(0, 1, 10)
        sample_per_simulation = 500
        simulations = 100
        distribution = mf_random.create_empirical_distribution(diag_prob,
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
                                                                  ordered,
                                                                  alternative='e'))

    def test_synergy_random(self):
        diag_prob = [0.4, 0.6]
        phenotype_prob = np.random.uniform(0, 1, 10)
        sample_per_simulation = 5000
        S = mf_random.synergy_random(diag_prob, phenotype_prob,
                              sample_per_simulation)
        # self.assertAlmostEqual(S.astype(np.float32).all(),
        #                        np.zeros(S.shape).astype(np.float32).all(),
        #                        delta=0.001)
        self.assertAlmostEqual(S[0, 0], 0.0, delta=0.001)
        self.assertAlmostEqual(S[5, 5], 0.0, delta=0.001)

    def test_synergy_random_multiprocessing(self):
        diag_prob = [0.4, 0.6]
        phenotype_prob = np.random.uniform(0, 1, 10)
        sample_per_simulation = 5000
        empirical_distributions = np.zeros([10, 10, 2])
        self.assertTrue(np.sum(np.abs(empirical_distributions)) == 0)
        mf_random.synergy_random_multiprocessing(diag_prob, phenotype_prob,
                                     sample_per_simulation, 0,
                                                 empirical_distributions)
        self.assertTrue(np.sum(np.abs(empirical_distributions)) > 0)


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
        p_matrix = randomiser.p_value(sampling=100)
        print(p_matrix)

    def test_multiprocessing(self):
        start = datetime.datetime.now()
        np.random.seed(2)
        M = 20
        diag_prob = np.array([0.3, 0.7])
        phenotype_prob = np.random.uniform(0, 1, M)
        sample_per_simulation = 5000
        simulations = 5
        S_distribution = np.zeros([M, M, simulations])
        workers = []
        for i in np.arange(simulations):
            workers.append(multiprocessing.Process(
                target=mf_random.synergy_random_multiprocessing,
                args=(diag_prob, phenotype_prob,sample_per_simulation,
                      i, S_distribution)))
        for i in np.arange(simulations):
            workers[i].start()

        for i in np.arange(simulations):
            workers[i].join()

        end = datetime.datetime.now()
        duration = end - start
        print("time for multiprocessing: {} ".format(duration.total_seconds()))

        start = datetime.datetime.now()
        S_distribution = np.zeros([M, M, simulations])
        for i in np.arange(simulations):
            print('start simulation: {}'.format(i))
            S_distribution[:, :, i] = mf_random.synergy_random(diag_prob,
                                                       phenotype_prob,
                                                     sample_per_simulation)
        end = datetime.datetime.now()
        duration = end - start
        print("time for non-multiprocessing: {} ".format(
            duration.total_seconds()))



if __name__ == '__main__':
    unittest.main()