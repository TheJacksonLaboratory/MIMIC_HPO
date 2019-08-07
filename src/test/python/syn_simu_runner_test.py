import mf
import syn_simu_runner
import unittest
import tempfile
import numpy as np
import pickle
import os.path


class TestSynSimuRunner(unittest.TestCase):

    def setUp(self):
        self.temppath = tempfile.mkdtemp()
        self.f = os.path.join(self.temppath, 'synergies.obj')
        M1 = 10
        N1 = 10000
        p1 = ['HP:' + str(i) for i in np.arange(M1)]
        synergy1 = mf.Synergy('D1', phenotype_list=p1)
        synergy1.add_batch(np.random.randint(0, 2, M1 * N1).reshape([N1, M1]),
                           np.random.randint(0, 2, N1))

        M2 = 20
        N2 = 1500
        p2 = ['HP:' + str(i) for i in np.arange(M2)]
        synergy2 = mf.Synergy('D2', phenotype_list=p2)
        synergy2.add_batch(np.random.randint(0, 2, M2 * N2).reshape([N2, M2]),
                           np.random.randint(0, 2, N2))

        synergies = {'D1': synergy1, 'D2': synergy2}
        with open(self.f, 'wb') as f1:
            pickle.dump(synergies, file=f1)

    def tearDown(self):
        if os.path.exists(self.f):
            os.unlink(self.f)

    def test_test_data_created(self):
        self.assertTrue(os.path.exists(os.path.join(self.temppath,
                                                    'synergies.obj')))

    def test_runner(self):
        with open(self.f, 'rb') as f:
            synergies = pickle.load(f)
        self.assertEqual(len(synergies), 2)
        syn_simu_runner.run(synergies, per_simulation=10000, simulations=1000,
                            verbose=True, dir=self.temppath)
        print(os.listdir(self.temppath))
        self.assertTrue(os.path.exists(os.path.join(self.temppath, 'D1.obj')))
        self.assertTrue(os.path.exists(os.path.join(self.temppath, 'D2.obj')))
        with open(os.path.join(self.temppath, 'D1.obj'), 'rb') as f1:
            p = pickle.load(f1)
            print(p)


if __name__ == '__main__':
    unittest.main()