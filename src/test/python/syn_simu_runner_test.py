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
        self.f = os.path.join(self.temppath, 'summaries.obj')
        M1 = 20
        N1 = 10000
        p1 = ['HP:' + str(i) for i in np.arange(M1)]
        summary1 = mf.SummaryXYz(p1, p1, 'D1')
        summary1.add_batch(np.random.randint(0, 2, M1 * N1).reshape([N1, M1]),
                           np.random.randint(0, 2, M1 * N1).reshape([N1, M1]),
                           np.random.randint(0, 2, N1))

        M2 = 30
        N2 = 5000
        p2 = ['HP:' + str(i) for i in np.arange(M2)]
        summary2 = mf.SummaryXYz(p2, p2, 'D2')
        summary2.add_batch(np.random.randint(0, 2, M2 * N2).reshape([N2, M2]),
                           np.random.randint(0, 2, M2 * N2).reshape([N2, M2]),
                           np.random.randint(0, 2, N2))

        summaries = {'D1': summary1, 'D2': summary2}
        with open(self.f, 'wb') as f1:
            pickle.dump(summaries, file=f1, protocol=2)

    def test_test_data_created(self):
        self.assertTrue(os.path.exists(os.path.join(self.temppath,
                                                    'summaries.obj')))

    def test_simulate(self):
        args = MockedArgsObj()
        args.input_path = self.f
        args.n_per_run = 10002
        args.N_SIMULATIONS = 10
        args.verbose = True
        args.out_dir = self.temppath
        args.cpu = 4
        args.job_id = 1
        args.disease_of_interest = 'D2'
        syn_simu_runner.simulate(args)

        result_out_path = os.path.join(args.out_dir,
            args.disease_of_interest + '_' + str(args.job_id) +
                                       '_distribution.obj')
        self.assertTrue(os.path.exists(result_out_path))

    def test_serialize_empirical_distributions(self):
        distribution = np.random.randn(10000).reshape([10,10,-1])
        path = os.path.join(self.temppath + 'distribution_subset.obj')
        syn_simu_runner.serialize_empirical_distributions(distribution,
                                                        path)
        self.assertTrue(os.path.exists(path))
        with open(path, 'rb') as f:
            subset = pickle.load(f)
        print(subset.shape)
        np.testing.assert_array_equal(subset.shape, np.array([5,5,100]))


class MockedArgsObj(object):
    pass


if __name__ == '__main__':
    unittest.main()
