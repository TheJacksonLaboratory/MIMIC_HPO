import unittest
import src.main.python.mf as mf
import numpy as np
import math
import tempfile


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
        self.tempdir = tempfile.mkdtemp()

    def test_summarize_z(self):
        positive_N, negative_N = mf.summarize_z(self.d)
        self.assertEqual(positive_N, 4)
        self.assertEqual(negative_N, 3)

    def test_summarize_Xz(self):
        s1 = mf.summarize_Xz(self.P, self.d)
        self.assertEqual(s1.tolist(), np.array([[3,1,1,2],
                                       [2,1,2,2],
                                       [3,1,1,2],
                                       [3,1,1,2]]).tolist())

    def test_summarize_Xz2(self):
        np.random.seed(799)
        P = np.random.randint(0, 2, 24).reshape([6, 4])
        d = np.random.randint(0, 2, 6)
        s1 = mf.summarize_Xz(P, d)
        self.assertEqual(s1.tolist(), np.array([[2,2,0,2],
                                       [1,3,1,1],
                                       [2,1,0,3],
                                       [0,2,2,2]]).tolist())


    def test_summarize_XYz(self):
        s2 = mf.summarize_XYz(self.P, self.P, self.d)
        self.assertEqual(s2[0,1,0], 1)
        self.assertEqual(s2[0, 2, 5], 1)
        self.assertEqual(s2[0,3,0], 3)
        self.assertEqual(s2[1,2,6], 1)

    def test_summarize_XYz2(self):
        np.random.seed(799)
        P = np.random.randint(0,2,24).reshape([6,4])
        d = np.random.randint(0,2,6)
        ppd = mf.summarize_XYz(P, P, d)
        self.assertEqual(ppd[0, 0, :].tolist(), [2,2,0,0,0,0,0,2])
        self.assertEqual(ppd[0, 1, :].tolist(), [1,1,1,1,0,2,0,0])
        self.assertEqual(ppd[0, 2, :].tolist(), [2,0,0,2,0,1,0,1])
        self.assertEqual(ppd[0, 3, :].tolist(), [0,1,2,1,0,1,0,1])
        self.assertEqual(ppd[1, 1, :].tolist(), [1,3,0,0,0,0,1,1])
        self.assertEqual(ppd[1, 2, :].tolist(), [1,1,0,2,1,0,0,1])
        self.assertEqual(ppd[1, 3, :].tolist(), [0,1,1,2,0,1,1,0])
        self.assertEqual(ppd[2, 2, :].tolist(), [2,1,0,0,0,0,0,3])
        self.assertEqual(ppd[2, 3, :].tolist(), [0,0,2,1,0,2,0,1])
        self.assertEqual(ppd[3, 3, :].tolist(), [0,2,0,0,0,0,2,2])

    def test_outcome(self):
        current = mf.summarize(self.P, self.P, self.d)
        m1, m2, case_N, control_N = current
        self.assertEqual(case_N, 4)
        self.assertEqual(control_N, 3)
        self.assertEqual(m1['set1'].tolist(), np.array([[3, 1, 1, 2],
                                                [2, 1, 2, 2],
                                                [3, 1, 1, 2],
                                                [3, 1, 1, 2]]).tolist())

        updated = mf.summarize(self.P, self.P, self.d, current)
        m1, m2, case_N, control_N = updated
        self.assertEqual(case_N, 8)
        self.assertEqual(control_N, 6)
        self.assertEqual(m1['set1'].tolist(), (2 * np.array([[3, 1, 1, 2],
                                                [2, 1, 2, 2],
                                                [3, 1, 1, 2],
                                                [3, 1, 1, 2]])).tolist())

    def test_mf_Xz(self):
        case_N = 4
        control_N = 3
        m1 = np.array([[3,1,1,2],
                       [2,1,2,2],
                       [3,1,1,2],
                       [3,1,1,2]])
        I,_,_ = mf.mf_Xz(m1, np.array([case_N, control_N]))
        I_HP1 = 3/7 * math.log2(21/16) + 1/7 * math.log2(7/12) + 1/7 * \
                 math.log2(7/12) + 2/7 * math.log2(14/9)
        I_HP2 = 2/7 * math.log2(14/12) + 1/7 * math.log2(7/9) + 2/7 * math.log2(
            14/16) + 2/7 * math.log2(14/12)
        I_HP3 = 3/7 * math.log2(21/16) + 1/7 * math.log2(7/12) + 1/7 * \
                 math.log2(7/12) + 2/7 * math.log2(14/9)
        I_HP4 = 3/7 * math.log2(21/16) + 1/7 * math.log2(7/12) + 1/7 * \
                 math.log2(7/12) + 2/7 * math.log2(14/9)
        np.testing.assert_almost_equal(I, [I_HP1, I_HP2, I_HP3,
                                                  I_HP4])

    def test_mf_Xz2(self):
        N = 100000
        M = 10
        d = np.random.randint(0, 2, N)
        P = np.random.randint(0, 2, M * N).reshape([N, M])
        m1, m2, case_N, control_N = mf.summarize(P, P, d)
        I, _, _ = mf.mf_Xz(m1['set1'], np.array([case_N, control_N]))
        np.testing.assert_almost_equal(I, np.zeros_like(I), decimal=4,
                                       err_msg='mutual information of two '
                                               'random variables is not zero')

    def test_mf_XY_z(self):
        case_N = 4
        control_N = 3
        m1 = np.array([[3, 1, 1, 2],
                       [2, 1, 2, 2],
                       [3, 1, 1, 2],
                       [3, 1, 1, 2]])
        m2 = np.array([int(i) for i in '''
                3. 1. 0. 0. 0. 0. 1. 2. 1. 1. 2. 0. 1. 0. 0. 2. 2. 0. 1. 1. 1. 1. 0. 1.
                3. 0. 0. 1. 0. 1. 1. 1. 1. 1. 1. 0. 2. 0. 0. 2. 2. 1. 0. 0. 0. 0. 2. 2.
                2. 0. 0. 1. 1. 1. 1. 1. 1. 0. 1. 1. 2. 1. 0. 1. 2. 0. 1. 1. 1. 1. 0. 1.
                2. 0. 1. 1. 0. 1. 1. 1. 3. 1. 0. 0. 0. 0. 1. 2. 2. 1. 1. 0. 1. 0. 0. 2.
                3. 0. 0. 1. 0. 1. 1. 1. 1. 0. 2. 1. 1. 1. 0. 1. 2. 1. 1. 0. 1. 0. 0. 2.
                3. 1. 0. 0. 0. 0. 1. 2'''.replace('\n', ' ').split('. ')]).reshape([4, 4, 8])
        II = mf.mf_XY_z(m2, np.array([case_N, control_N]))
        self.assertAlmostEqual(II[0,0], 3/7 * math.log2(21/16) +
                               1/7 * math.log2(7/12) +
                               1/7 * math.log2(7/12) +
                               2/7 * math.log2(14/9))
        self.assertAlmostEqual(II[0,1], 1/7 * math.log2(7/8) + 1/7 *
                               math.log2(7/6) + 2/7 * math.log2(14/8) + 1/7 *
                               math.log2(7/4) + 2/7 * math.log2(14/6))
        self.assertAlmostEqual(II[0,2], 2/7 * math.log2(14/8) + 1/7 *
                               math.log2(7/8) + 1/7 * math.log2(7/6) + 1/7 *
                               math.log2(7/8) + 1/7 * math.log2(7/6) + 1/7 *
                               math.log2(7/3))
        self.assertAlmostEqual(II[0,3], 3/7 * math.log2(21/12) + 1/7 *
                               math.log2(7/3) + 1/7 * math.log2(7/3) + 1/7 *
                               math.log2(7/8) + 1/7 * math.log2(7/6))
        self.assertAlmostEqual(II[1,2], 2/7 * math.log2(14/8) + 1/7 *
                               math.log2(7/3) + 1/7 * math.log2(7/8) + 1/7 *
                               math.log2(7/6) + 1/7 * math.log2(7/8) + 1/7 *
                               math.log2(7/6))
        self.assertAlmostEqual(II[1,3], 1/7 * math.log2(7/4) + 1/7 *
                               math.log2(7/8) + 1/7 * math.log2(7/6) + 2/7 *
                               math.log2(14/12) + 1/7 * math.log2(7/9) + 1/7
                               * math.log2(7/3))
        self.assertAlmostEqual(II[2,3], 2/7 * math.log2(14/12) +
                               1/7 * math.log2(7/9) +
                               1/7 * math.log2(7/4) +
                               1/7 * math.log2(7/4) +
                               2/7 * math.log2(14/6))

    def test_mf_XY_given_z(self):
        m1 = np.array([4, 3])
        m2 = np.array([int(i) for i in '''
                        3. 1. 0. 0. 0. 0. 1. 2. 1. 1. 2. 0. 1. 0. 0. 2. 2. 0. 1. 1. 1. 1. 0. 1.
                        3. 0. 0. 1. 0. 1. 1. 1. 1. 1. 1. 0. 2. 0. 0. 2. 2. 1. 0. 0. 0. 0. 2. 2.
                        2. 0. 0. 1. 1. 1. 1. 1. 1. 0. 1. 1. 2. 1. 0. 1. 2. 0. 1. 1. 1. 1. 0. 1.
                        2. 0. 1. 1. 0. 1. 1. 1. 3. 1. 0. 0. 0. 0. 1. 2. 2. 1. 1. 0. 1. 0. 0. 2.
                        3. 0. 0. 1. 0. 1. 1. 1. 1. 0. 2. 1. 1. 1. 0. 1. 2. 1. 1. 0. 1. 0. 0. 2.
                        3. 1. 0. 0. 0. 0. 1. 2'''.replace('\n', ' ').split(
            '. ')]).reshape([4, 4, 8])
        mf_XY_condition_on_z = mf.mf_XY_given_z(m2, m1)
        #print(mf_XY_condition_on_z)
        #print(m2)
        # +++, ++-, +-+, +--, -++, -+-, --+, ---
        self.assertAlmostEqual(mf_XY_condition_on_z[0, 0], 3/7 * np.log2(3/7
             * (4/7) / (3/7 * (3/7))) + 1/7 * np.log2(1/7 * (3/7) / (1/7 * (
            1/7))) + 1/7 * np.log2(1/7 * (4/7)/(1/7 * 1/7)) + 2/7 * np.log2(
            2/7 * 3/7/(2/7 * 2/7)))
        self.assertAlmostEqual(mf_XY_condition_on_z[0,2],
                               2/7 * np.log2(2/7*4/7 / (3/7 * 3/7)) +
                               0 +
                               1/7 * np.log2(1/7 * 4/7 / (3/7 * 1/7)) +
                               1/7 * np.log2(1/7 * 3/7 / (1/7 * 2/7)) +
                               1/7 * np.log2(1/7 * 4/7 / (1/7 * 3/7)) +
                               1/7 * np.log2(1/7 * 3/7 / (2/7 * 1/7)) +
                               0 +
                               1/7 * np.log2(1/7 * 3/7 / (2/7 * 2/7)))
        self.assertAlmostEqual(mf_XY_condition_on_z[1, 0],
                               1/7 * np.log2(1/7 * 4/7 / (2/7 * 3/7)) +
                               1/7 * np.log2(1/7 * 3/7 / (1/7 * 1/7)) +
                               1/7 * np.log2(1/7 * 4/7 / (2/7 * 1/7)) +
                               0 +
                               2/7 * np.log2(2/7 * 4/7 / (2/7 * 3/7)) +
                               0 +
                               0 +
                               2/7 * np.log2(2/7 * 3/7 / (2/7 * 2/7)))

    def test_synergy(self):
        I = np.array([0.1, 0.2, 0.3])
        II = np.array([[0.1, 0.4, 0.2],
                       [0.4, 0.1, 0.0],
                       [0.2, 0.0, 0.3]])
        S = mf.synergy(I, I, II)
        np.testing.assert_almost_equal(S,
                               np.array([[-0.1, 0.1, -0.2],
                                         [0.1, -0.3, -0.5],
                                         [-0.2, -0.5, -0.3]]))

    def test_SummaryXYz_constructor(self):
        disease_name = 'MONDO:heart failure'
        pl = np.array(['HP:001', 'HP:002', 'HP:003'])
        heart_failure = mf.SummaryXYz(X_names=pl, Y_names=pl,
                                         z_name=disease_name)
        self.assertEqual(heart_failure.z_name, 'MONDO:heart failure')
        self.assertEqual(heart_failure.vars_labels['set1'].tolist(),
                         pl.tolist())
        pl_reset = ['Hypokalemia', 'Hyperglycemia', 'Hypertension']
        heart_failure.vars_labels['set1'] = pl_reset
        self.assertEqual(heart_failure.vars_labels['set1'],
                         pl_reset)

    def test_MutualInfoXYz(self):
        summary = mf.SummaryXYz(
            X_names=['HP:001', 'HP:002', 'HP:003', 'HP:004'],
            Y_names=['HP:001', 'HP:002', 'HP:003', 'HP:004'],
            z_name='heart failure')
        summary.add_batch(self.P, self.P, self.d)
        heart_failure = mf.MutualInfoXYz(summary)
        S = heart_failure.synergy_XY2z()
        # update with the same set of data should not affect synergy
        summary.add_batch(self.P, self.P, self.d)
        heart_failure = mf.MutualInfoXYz(summary)
        S_updated = heart_failure.synergy_XY2z()
        self.assertEqual(S.all(), S_updated.all())

        self.assertEqual(heart_failure.case_N, 8)
        self.assertEqual(heart_failure.control_N, 6)
        synergies = {}
        synergies['heart failure'] = heart_failure
        heart_failure.__getattribute__('m1')

    def test_MF_withinSet(self):
        labels = ['HP:001', 'HP:002','HP:003', 'HP:004']
        summary = mf.SummaryXYz(X_names=labels,
                                Y_names=labels,
                                z_name='heart failure')
        summary.add_batch(self.P, self.P, self.d)
        heart_failure = mf.MutualInfoXYz(summary)
        S = heart_failure.synergy_XY2z()
        # update with the same set of data should not affect synergy
        summary.add_batch(self.P, self.P, self.d)
        heart_failure = mf.MutualInfoXYz(summary)
        S_updated = heart_failure.synergy_XY2z()
        self.assertEqual(S.all(), S_updated.all())

        self.assertEqual(heart_failure.case_N, 8)
        self.assertEqual(heart_failure.control_N, 6)



if __name__ == '__main__':
    unittest.main()
