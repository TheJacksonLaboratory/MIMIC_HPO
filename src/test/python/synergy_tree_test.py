import unittest
import src.main.python.synergy_tree as synergy_tree
import treelib


class TestSynergyTree(unittest.TestCase):

    def setUp(self):
        pass

    def test_complement_pairs(self):
        s = {}
        pairs = synergy_tree.complement_pairs(s)
        self.assertEqual(len(pairs), 0)

        s = {'a'}
        pairs = synergy_tree.complement_pairs(s)
        self.assertEqual(len(pairs), 0)

        s = {'a', 'b', 'c'}
        pairs = synergy_tree.complement_pairs(s)
        self.assertEqual(len(pairs), 3)

        s = {'a', 'b', 'c', 'd'}
        pairs = synergy_tree.complement_pairs(s)
        self.assertEqual(len(pairs), 7)

    def test_populate_syn_tree(self):
        var_set = {'a', 'b', 'c', 'd'}
        mf_dict = {('a',): 0.1,
                   ('b',): 0.5,
                   ('c',): 0.3,
                   ('d',): 0.2,
                   ('a', 'b'): 0.8,
                   ('a', 'c'): 0.35,
                   ('a', 'd'): 0.05,
                   ('b', 'c'): 0.99,
                   ('b', 'd'): 0.65,
                   ('c', 'd'): 0.31,
                   ('a', 'b', 'c'): 0.98,
                   ('a', 'b', 'd'): 0.6,
                   ('a', 'c', 'd'): 0.45,
                   ('b', 'c', 'd'): 0.8,
                   ('a', 'b', 'c', 'd'): 0.999}
        syn_tree = treelib.Tree()
        root_id = tuple(sorted(var_set))
        syn_tree = synergy_tree.populate_syn_tree(syn_tree, None, root_id,
                                                   mf_dict)
        #syn_tree.show()

    def test_SynergyTree(self):
        var_set = {'a', 'b', 'c', 'd'}
        mf_dict = {('a',): 0.1,
                   ('b',): 0.5,
                   ('c',): 0.3,
                   ('d',): 0.2,
                   ('a', 'b'): 0.8,
                   ('a', 'c'): 0.35,
                   ('a', 'd'): 0.05,
                   ('b', 'c'): 0.99,
                   ('b', 'd'): 0.65,
                   ('c', 'd'): 0.31,
                   ('a', 'b', 'c'): 0.98,
                   ('a', 'b', 'd'): 0.6,
                   ('a', 'c', 'd'): 0.45,
                   ('b', 'c', 'd'): 0.8,
                   ('a', 'b', 'c', 'd'): 0.999}
        syn_tree = synergy_tree.SynergyTree(var_set, None, mf_dict)
        print(syn_tree.synergy_tree())


if __name__ == '__main__':
    unittest.main()
