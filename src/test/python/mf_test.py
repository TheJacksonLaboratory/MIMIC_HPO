import unittest
import src.main.python.mf as mf
import numpy as np
import math


class TestMF(unittest.TestCase):

    def setUp(self):
        # set up: 7 records of encounters
        self.d = np.array([0,1,0,1,0,1,1])
        # set up: for each encounter, record 4 phenotypes
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


if __name__ == '__main__':
    unittest.main()