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
        return ancestor_descendent(self.graph, termid1, termid2)

    def is_descendent_ancestor(self, termid1, termid2):
        return ancestor_descendent(self.graph, termid2, termid1)

    def has_dependency(self, termid1, termid2):
        return self.is_ancestor_descendent(termid1, termid2) or \
               self.is_descendent_ancestor(termid1, termid2)


def ancestor_descendent(graph, ancestor, descendent):
    """
    Perform a breadth first search to find whether they have
    ancestor-descendent relationship
    :param graph: a graph
    :param ancestor: potential ancestor
    :param descendent: potential descendent
    :return: true if they are ancestor-descendent
    """
    parents = []
    for node in graph.successors(descendent):
        if node == ancestor:
            return True
        else:
            parents.append(node)

    for parent in parents:
        if ancestor_descendent(graph, ancestor, parent):
            return True

    return False
