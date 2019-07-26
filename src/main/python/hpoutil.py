import obonet


class HPO:

    def __init__(self, url):
        self.graph = obonet.read_obo(url)
        self.id2name_map = {id_: data.get('name') for (id_, data) in
                            self.graph.nodes(data=True)}

    def hpograph(self):
        return self.graph

    def nodes(self):
        return self.graph.nodes(data=True)

    def term_id2name_map(self):
        return self.id2name_map

    def is_ancestor_descendent(self, termid1, termid2):
        return self.graph.has_predecessor(termid1, termid2)

    def is_descendent_ancestor(self, termid1, termid2):
        return self.graph.has_successor(termid1, termid2)

    def has_dependency(self, termid1, termid2):
        return self.is_ancestor_descendent(termid1, termid2) or \
               self.is_descendent_ancestor(termid1, termid2)


def main():
    hpo = HPO('/Users/zhangx/git/human-phenotype-ontology/hp.obo')
    print(hpo.term_id2name_map()['HP:0000003'])
    print('{} is ancestor of {}: {}'.format('HP:0001238', 'HP:0001166',
                                            hpo.is_ancestor_descendent(
                                                'HP:0001238', 'HP:0001166')))
    print('{} is ancestor of {}: {}'.format('HP:0001166','HP:0001238',
                                            hpo.is_ancestor_descendent(
                                                'HP:0001166','HP:0001238')))
    print('{} is ancestor of {}: {}'.format('HP:0001238', 'HP:0001166',
                                            hpo.is_descendent_ancestor(
                                                'HP:0001238', 'HP:0001166')))
    print('{} is ancestor of {}: {}'.format('HP:0001166', 'HP:0001238',
                                            hpo.is_descendent_ancestor(
                                                'HP:0001166', 'HP:0001238')))
    print('{} is ancestor of {}: {}'.format('HP:0001238', 'HP:0001166',
                                            hpo.has_dependency(
                                                'HP:0001238', 'HP:0001166')))
    print('{} is ancestor of {}: {}'.format('HP:0001166', 'HP:0001238',
                                            hpo.has_dependency(
                                                'HP:0001166', 'HP:0001238')))
    print('{} is ancestor of {}: {}'.format('HP:0001166', 'HP:0025546',
                                            hpo.has_dependency(
                                                'HP:0001166', 'HP:0025546')))


if __name__ == '__main__':
    main()