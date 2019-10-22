import unittest
import src.main.python.hpoutil as hpoutil

class TestHpoUtil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hpo = hpoutil.HPO(
            '/Users/zhangx/git/human-phenotype-ontology/hp.obo')

    def testConstructor(self):
        self.assertIsNotNone(self.hpo, 'failed to load in constructor call')

    def testGraph(self):
        self.assertIsNotNone(self.hpo.hpograph())

    def testNodes(self):
        self.assertIsNotNone(self.hpo.nodes())

    def test_term_id2name_map(self):
        self.assertTrue(len(self.hpo.term_id2name_map().items()) > 0)

    def test_is_ancestor_descent(self):
        ancestor = 'HP:0001238'
        descendent = 'HP:0001166'
        self.assertTrue(self.hpo.is_ancestor_descendent(ancestor, descendent))
        self.assertFalse(self.hpo.is_ancestor_descendent(descendent, ancestor))

    def test_is_descendent_ancestor(self):
        ancestor = 'HP:0001238'
        descendent = 'HP:0001166'
        self.assertTrue(self.hpo.is_descendent_ancestor(descendent, ancestor))
        self.assertFalse(self.hpo.is_descendent_ancestor(ancestor, descendent))
        ancestor = 'HP:0000001'
        descendent = 'HP:0001939'
        self.assertTrue(self.hpo.is_descendent_ancestor(descendent, ancestor))

    def test_has_dependent(self):
        ancestor = 'HP:0001238'
        descendent = 'HP:0001166'
        unrelated = 'HP:0025546'
        self.assertTrue(self.hpo.has_dependency(descendent, ancestor))
        self.assertTrue(self.hpo.has_dependency(ancestor, descendent))
        self.assertFalse(self.hpo.has_dependency(ancestor, unrelated))
        self.assertFalse(self.hpo.has_dependency(descendent, unrelated))
        ancestor = 'HP:0000001'
        descendent = 'HP:0001939'
        self.assertTrue(self.hpo.has_dependency(descendent, ancestor))

    def test_ancestor_descendent(self):
        ancestor = 'HP:0000001'
        descendent = 'HP:0001939'
        self.assertTrue(hpoutil.ancestor_descendent(self.hpo.graph, ancestor,
                                           descendent))



if __name__ == '__main__':
    unittest.main()