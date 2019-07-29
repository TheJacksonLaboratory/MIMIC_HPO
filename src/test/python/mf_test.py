import unittest
import src.main.python.mf as mf
import numpy as np
import math


class TestMF(unittest.TestCase):

    def setUp(self):
        # set up: 7 records
        self.d = np.array([0,1,0,1,0,1,1])
        # set up: for each record, record 4 phenotypes
        self.P = np.array([[0,0,1,1],
                           [1,0,1,1],
                           [0,0,0,0],
                           [1,1,1,1],
                           [1,1,0,0],
                           [1,0,0,1],
                           [0,1,1,0]])


    def test_summarize_diagnosis(self):
        positive_N, negative_N = mf.summarize_diagnosis(self.d)
        self.assertEqual(positive_N, 4)
        self.assertEqual(negative_N, 3)


    def test_summarize_diagnosis_phenotype(self):
        s1 = mf.summarize_diagnosis_phenotype(self.P, self.d)
        self.assertEqual(s1.tolist(), np.array([[3,1,1,2],
                                       [2,1,2,2],
                                       [3,1,1,2],
                                       [3,1,1,2]]).tolist())


    def test_summarize_diagnosis_phenotype_pair(self):
        s2 = mf.summarize_diagnosis_phenotype_pair(self.P, self.d)
        self.assertEqual(s2[0,1,0], 1)
        self.assertEqual(s2[0, 2, 5], 1)
        self.assertEqual(s2[0,3,0], 3)
        self.assertEqual(s2[1,2,6], 1)


    def test_outcome(self):
        current = mf.summarize(self.P, self.d)
        m1, m2, case_N, control_N = current
        self.assertEqual(case_N, 4)
        self.assertEqual(control_N, 3)
        self.assertEqual(m1.tolist(), np.array([[3, 1, 1, 2],
                                                [2, 1, 2, 2],
                                                [3, 1, 1, 2],
                                                [3, 1, 1, 2]]).tolist())

        updated = mf.summarize(self.P, self.d, current)
        m1, m2, case_N, control_N = updated
        self.assertEqual(case_N, 8)
        self.assertEqual(control_N, 6)
        self.assertEqual(m1.tolist(), (2 * np.array([[3, 1, 1, 2],
                                                [2, 1, 2, 2],
                                                [3, 1, 1, 2],
                                                [3, 1, 1, 2]])).tolist())

    def test_mf_diagnosis_phenotype(self):
        case_N = 4
        control_N = 3
        m1 = np.array([int(i) for i in '3. 1. 1. 2. 2. 1. 2. 2. 3. 1. 1. 2. 3. 1. 1. 2'.split('. ')]).reshape([4, 4])
        I,_,_ = mf.mf_diagnosis_phenotype(m1, case_N, control_N)
        temp = 3/7 * math.log2(21/16) + 1/7 * math.log2(7/12) + 1/7 * math.log2(7/12) + 2/7 * math.log2(14/9)
        self.assertAlmostEqual(I[0], temp)
        temp = 2/7 * math.log2(14/12) + 1/7 * math.log2(7/9) + 2/7 * math.log2(14/16) + 2/7 * math.log2(14/12)
        self.assertAlmostEqual(I[1], temp)

    def test_mf_diagnosis_phenotype_pair(self):
        case_N = 4
        control_N = 3
        m1 = np.array([int(i) for i in '3. 1. 1. 2. 2. 1. 2. 2. 3. 1. 1. 2. 3. 1. 1. 2'.split('. ')]).reshape([4, 4])
        m2 = np.array([int(i) for i in '''
                3. 1. 0. 0. 0. 0. 1. 2. 1. 1. 2. 0. 1. 0. 0. 2. 2. 0. 1. 1. 1. 1. 0. 1.
                3. 0. 0. 1. 0. 1. 1. 1. 1. 1. 1. 0. 2. 0. 0. 2. 2. 1. 0. 0. 0. 0. 2. 2.
                2. 0. 0. 1. 1. 1. 1. 1. 1. 0. 1. 1. 2. 1. 0. 1. 2. 0. 1. 1. 1. 1. 0. 1.
                2. 0. 1. 1. 0. 1. 1. 1. 3. 1. 0. 0. 0. 0. 1. 2. 2. 1. 1. 0. 1. 0. 0. 2.
                3. 0. 0. 1. 0. 1. 1. 1. 1. 0. 2. 1. 1. 1. 0. 1. 2. 1. 1. 0. 1. 0. 0. 2.
                3. 1. 0. 0. 0. 0. 1. 2'''.replace('\n', ' ').split('. ')]).reshape([4, 4, 8])
        II = mf.mf_diagnosis_phenotype_pair(m2, case_N, control_N)
        self.assertAlmostEqual(II[0,0], 3/7 * math.log2(21/16) +
                               1/7 * math.log2(7/12) +
                               1/7 * math.log2(7/12) +
                               2/7 * math.log2(14/9))
        self.assertAlmostEqual(II[2,3], 2/7 * math.log2(14/12) +
                               1/7 * math.log2(7/9) +
                               1/7 * math.log2(7/4) +
                               1/7 * math.log2(7/4) +
                               2/7 * math.log2(14/6))

    def test_synergy(self):
        I = np.array([0.1, 0.2, 0.3])
        II = np.array([[0.1, 0.4, 0.2],
                       [0.4, 0.1, 0.0],
                       [0.2, 0.0, 0.3]])
        S = mf.synergy(I, II)
        self.assertAlmostEqual(S.all(),
                               np.array([[-0.1, 0.1, -0.2],
                                         [0.1, -0.3, -0.5],
                                         [-0.2, -0.5, -0.3]]).all(),
                               delta=0.001)

    def test_class_constructor(self):
        disease_name = 'MONDO:heart failure'
        pl = np.array(['HP:001', 'HP:002', 'HP:003'])
        heart_failure = mf.Synergy(disease_name, phenotype_list=pl)
        self.assertEqual(heart_failure.get_disease(), 'MONDO:heart failure')
        self.assertEqual(heart_failure.get_phenotype_list().tolist(), pl.tolist())
        pl_reset = ['Hypokalemia', 'Hyperglycemia', 'Hypertension']
        heart_failure.set_phenotype_label(pl_reset)
        self.assertEqual(heart_failure.get_phenotype_list().tolist(), pl_reset)

    def test_class_logic(self):
        heart_failure = mf.Synergy(disease='heart failure', phenotype_list=['HP:001', 'HP:002', 'HP:003', 'HP:004'])
        heart_failure.add_batch(self.P, self.d)
        S = heart_failure.pairwise_synergy()
        # update with the same set of data should not affect synergy
        heart_failure.add_batch(self.P, self.d)
        S_updated = heart_failure.pairwise_synergy()
        self.assertEqual(S.all(), S_updated.all())

        self.assertEqual(heart_failure.get_case_count(), 8)
        self.assertEqual(heart_failure.get_control_count(), 6)
        synergies = {}
        synergies['heart failure'] = heart_failure
        synergies['heart failure'].add_batch(self.P, self.d)
        #print(synergies['heart failure'].pairwise_synergy())
        heart_failure.__getattribute__('m1')

    def test_matrix_searchsorted(self):
        ordered = np.arange(24).reshape([2,3,4])
        query = np.array([[-1, 4, 8.5],[13.5, 19, 24]])
        idx = mf.matrix_searchsorted(ordered, query)
        expected = [[0, 0, 1],
                    [2, 3, 4]]
        self.assertEqual(idx.tolist(), expected)

    def test_create_empirical_distribution(self):
        diag_prob = np.array([0.3, 0.7])
        phenotype_prob = np.random.uniform(0, 1, 10)
        sample_per_simulation = 500
        simulations = 100
        distribution = mf.create_empirical_distribution(diag_prob,
                                                       phenotype_prob,
        sample_per_simulation, simulations)
        self.assertEqual(list(distribution.shape), [10, 10, 100])

    def test_p_value_estimate(self):
        ordered = np.arange(24).reshape([2, 3, 4])
        query = np.array([[-1, 4, 8.5], [13.5, 19, 24]])
        idx = mf.p_value_estimate(query, ordered, alternative='two.sided')
        expected = [[0, 0.5, 0.5],
                    [1, 0.5, 0]]
        self.assertEqual(idx.tolist(), expected, 'two.sided p value estimate '
                                                 'failed')

        idx = mf.p_value_estimate(query, ordered, alternative='left')
        expected = [[0, 0.25, 0.25],
                    [0.5, 1, 1]]
        self.assertEqual(idx.tolist(), expected, 'left sided p value estimate '
                                                 'failed')

        idx = mf.p_value_estimate(query, ordered, alternative='right')
        expected = [[1, 1, 0.75],
                    [0.5, 0.25, 0]]
        self.assertEqual(idx.tolist(), expected, 'right sided p value estimate '
                                                 'failed')

        self.assertRaises(ValueError, lambda: mf.p_value_estimate(query,
                                     ordered, alternative='e'))

    def test_synergy_random(self):
        diag_prob = [0.4, 0.6]
        phenotype_prob = np.random.uniform(0, 1, 10)
        sample_per_simulation = 5000
        S = mf.synergy_random(diag_prob, phenotype_prob, sample_per_simulation)
        # self.assertAlmostEqual(S.astype(np.float32).all(),
        #                        np.zeros(S.shape).astype(np.float32).all(),
        #                        delta=0.001)
        self.assertAlmostEqual(S[0,0], 0.0, delta=0.001)
        self.assertAlmostEqual(S[5,5], 0.0, delta=0.001)


if __name__ == '__main__':
    unittest.main()