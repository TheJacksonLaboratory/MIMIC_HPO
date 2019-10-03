import unittest
import src.main.python.mf as mf
import numpy as np
import tempfile


class TestMu(unittest.TestCase):

    def setUp(self):
        self.X_names = ['X1', 'X2', 'X3']
        self.Y_names = ['Y1', 'Y2', 'Y3', 'Y4', 'Y5']
        # set up: for each record, record 3 variables
        self.X = np.array([[1,0,1],
                          [0,0,0],
                          [1,1,0],
                          [1,1,1],
                          [1,0,0],
                          [0,0,1],
                          [0,1,0]])
        # set up: for each record, record 5 phenotypes
        self.Y = np.array([[0,0,1,1,1],
                           [1,0,1,1,0],
                           [0,0,0,0,1],
                           [1,1,1,1,0],
                           [1,1,0,0,1],
                           [1,0,0,1,1],
                           [0,1,1,0,0]])
        self.tempdir = tempfile.mkdtemp()

    def test_constructor(self):
        mfv = mf.MutualInformationVectorized(self.X_names, self.Y_names)
        self.assertIsNotNone(mfv)

    def test_add_batch(self):
        mfv = mf.MutualInformationVectorized(self.X_names, self.Y_names)
        mfv.add_batch(self.X, self.Y)
        summary = mfv.m
        np.testing.assert_array_equal(summary[0, 0, :], np.array([2, 2, 2, 1]))
        np.testing.assert_array_equal(summary[0, 1, :], np.array([2, 2, 1, 2]))
        np.testing.assert_array_equal(summary[1, 0, :], np.array([1, 2, 3, 1]))
        np.testing.assert_array_equal(summary[1, 2, :], np.array([2, 1, 2, 2]))

    def test_mf(self):
        mfv = mf.MutualInformationVectorized(self.X_names, self.Y_names)
        mfv.add_batch(self.X, self.Y)
        mf_info = mfv.mf()
        self.assertAlmostEqual(mf_info[0, 0], 0.02024421)

    def test_entropy(self):
        # re-specify X, Y
        X = np.array([[1, 0, 1],
                           [0, 0, 1],
                           [1, 0, 1],
                           [1, 0, 1],
                           [1, 0, 1],
                           [0, 0, 1],
                           [0, 0, 1]])
        # set up: for each record, record 5 phenotypes
        Y = np.array([[1, 0, 1, 1, 1],
                      [1, 0, 1, 1, 0],
                      [0, 0, 1, 1, 0],
                      [1, 1, 1, 1, 0],
                      [1, 1, 1, 1, 0],
                      [1, 0, 0, 1, 0],
                      [0, 1, 1, 1, 0]])
        mfv = mf.MutualInformationVectorized(self.X_names, self.Y_names)
        mfv.add_batch(X, Y)
        h = mfv.entropies()
        self.assertAlmostEqual(-h['X'][0], 4/7 * np.log2(4/7) + 3/7 * np.log2(
            3/7))
        self.assertAlmostEqual(-h['X'][1], 0)
        self.assertAlmostEqual(-h['X'][2], 0)

        self.assertAlmostEqual(-h['Y'][0], 5/7 * np.log2(5/7) + 2/7 *
                               np.log2(2/7))
        self.assertAlmostEqual(-h['Y'][1], 3/7 * np.log2(
            3/7) + 4/7 * np.log2(4/7))
        self.assertAlmostEqual(-h['Y'][2], 6/7 * np.log2(6/7) + 1/7 *
                               np.log2(1/7))
        self.assertAlmostEqual(-h['Y'][3], 0)
        self.assertAlmostEqual(-h['Y'][4], 1/7 *
                               np.log2(1/7) + 6/7 * np.log2(6/7))


if __name__ == '__main__':
    unittest.main()
