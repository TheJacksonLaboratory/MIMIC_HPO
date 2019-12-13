import obonet

"""
TODO: This module is deprecated. Use the new obonet instead

"""
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

    def is_ancestor_descendant(self, termid1, termid2):
        return ancestor_descendant(self.graph, termid1, termid2)

    def is_descendant_ancestor(self, termid1, termid2):
        return ancestor_descendant(self.graph, termid2, termid1)

    def has_dependency(self, termid1, termid2):
        return self.is_ancestor_descendant(termid1, termid2) or \
               self.is_descendant_ancestor(termid1, termid2)


def ancestor_descendant(graph, ancestor, descendant):
    """
    Perform a breadth first search to find whether they have
    ancestor-descendant relationship
    :param graph: a graph
    :param ancestor: potential ancestor
    :param descendant: potential descendant
    :return: true if they are ancestor-descendant
    """
    parents = []
    for node in graph.successors(descendant):
        if node == ancestor:
            return True
        else:
            parents.append(node)

    for parent in parents:
        if ancestor_descendant(graph, ancestor, parent):
            return True

    return False
