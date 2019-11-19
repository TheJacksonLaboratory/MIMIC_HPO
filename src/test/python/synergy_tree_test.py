import unittest
import src.main.python.synergy_tree as synergy_tree
import treelib
import networkx as nx
import time


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

    def test_subsets(self):
        n = 4
        v = set(['V' + str(i + 1) for i in range(n)])
        self.assertEqual(len(synergy_tree.subsets(v)), 2 ** n - 2)
        self.assertEqual(len(synergy_tree.subsets(v, include_self=True)),
                         2 ** n - 1)
        self.assertEqual(len(synergy_tree.subsets(v, include_self=True,
                                                  include_empty=True)), 2 ** n)

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


    def test_disjoint_series(self):
        bell_numbers = [1,
                        2,
                        5,
                        15,
                        52,
                        203,
                        877,
                        4140,
                        21147,
                        115975]
        disjoint_series_count = []
        n = 7
        now = time.time()
        for i in range(n):
            variables = [x + 1 for x in range(i + 1)]
            count_disjoint_series = len(synergy_tree.disjoint_series(
                variables, include_self=True))
            disjoint_series_count.append(count_disjoint_series)
        end = time.time()
        # print('time: {}'.format(end - now))
        # print(disjoint_series_count)
        self.assertEqual(disjoint_series_count, bell_numbers[0:n])

    def test_DisjointSerie(self):
        serie = synergy_tree.DisjointSerie([('d',), ('a',), ('c', 'b')])
        self.assertEqual(serie.serie, [('a',), ('b', 'c'), ('d',)])

        serie2 = synergy_tree.DisjointSerie()
        self.assertEqual(serie2.serie, [])
        serie2.add(('d',))
        self.assertEqual(serie2.serie, [('d',)])
        serie2.add(('b', 'c'))
        self.assertEqual(serie2.serie, [('b', 'c'), ('d',)])
        serie2.add(('a',))
        self.assertEqual(serie2.serie, [('a',), ('b', 'c'), ('d',)])

        self.assertEqual(serie, serie2)

        serie3 = synergy_tree.DisjointSerie([('a','b'), ('c', 'd')])
        self.assertNotEqual(serie, serie3)

    def test_bit_array(self):
        decimal = 11
        self.assertEqual(synergy_tree.bit_array(decimal, 8), [0, 0, 0, 0, 1,
                                                               0, 1, 1])

    def test_complement_pairs2(self):
        variables = [1, 2]
        self.assertEqual(len(synergy_tree.complement_pairs2(variables,
                                                             True)), 2)
        variables = [1, 2, 3, 4]
        self.assertEqual(len(synergy_tree.complement_pairs2(variables,
                                                             True)), 8)

    def test_create_network(self):
        ebunch = [(1,2, {'weight': 0.5}),
                  (1,3, {'weight': 0.4}),
                  (2,5, {'weight': 0.9}),
                  (1,4)]
        g = nx.Graph()
        g.add_edges_from(ebunch)
        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(g[1][2]['weight'], 0.5)

    def test_trim_edges(self):
        mocked_hpo = nx.MultiDiGraph()
        mocked_hpo_nodes = ['HP:' + str(i + 1) for i in range(5)]
        mocked_hpo.add_nodes_from(mocked_hpo_nodes)
        mocked_hpo_edges = [('HP:5', 'HP:2'), ('HP:3', 'HP:2')]
        mocked_hpo.add_edges_from(mocked_hpo_edges)
        # print(mocked_hpo.edges)

        conditional_mf_network = nx.Graph()
        edges = [('HP:1', 'HP:2', {'mf': 0.5}),
                 ('HP:1', 'HP:3', {'mf': 0.7}),
                 ('HP:1', 'HP:4', {'mf': 0.3}),
                 ('HP:1', 'HP:5', {'mf': 0.1}),
                 ('HP:5', 'HP:2', {'mf': 0.2})]
        conditional_mf_network.add_edges_from(edges)
        # print(conditional_mf_network.adj)

        trimed_network = synergy_tree.trim_edges(conditional_mf_network,
                                                 mocked_hpo, 0.8)
        # print(conditional_mf_network.nodes)
        # print(trimed_network.nodes)
        self.assertEqual(list(trimed_network.nodes),
                         ['HP:1', 'HP:2', 'HP:3', 'HP:4'])

        trimed_network = synergy_tree.trim_edges(conditional_mf_network,
                                                 mocked_hpo, 0.6)
        # print(conditional_mf_network.nodes)
        # print(trimed_network.nodes)
        self.assertEqual(list(trimed_network.nodes),
                         ['HP:1', 'HP:3', 'HP:4'])


if __name__ == '__main__':
    unittest.main()
