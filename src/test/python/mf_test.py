import unittest
import src.main.python.mf as mf
import numpy as np

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

    def test_entropy_single(self):
        e = mf.entropy_single(np.array([1, 1, 1]))
        self.assertEqual(e, 0.0, 'single random variable entropy wrong')


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
        print(s2)
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


if __name__ == '__main__':
    unittest.main()