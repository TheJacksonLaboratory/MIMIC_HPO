import unittest
import src.main.python.mf as mf
import numpy as np

class TestMF(unittest.TestCase):

    def setUp(self):
        print('set up')

    def test_entropy_single(self):
        e = mf.entropy_single(np.array([1, 1, 1]))
        self.assertEqual(e, 0.0, 'single random variable entropy wrong')


if __name__ == '__main__':
    unittest.main()