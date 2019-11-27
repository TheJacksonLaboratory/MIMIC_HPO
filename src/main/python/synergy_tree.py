import itertools
import treelib
import networkx as nx
import numpy as np
import pickle
import copy
import sys
import logging


class SynergyTree:
    """
    Class to represent a synergy tree. An instance of the class takes in a
    set of variables and precomputed mutual information between subsets of
    variables and an outcome and generate a synergy tree
    """
    def __init__(self, var_ids, var_dict, mf_dict):
        """
        :param var_ids: a list of variable ids
        :param var_dict: a dictionary that annotate variable ids
        :param mf_dict: a dictionary from subsets of the variables to their
        mutual information with an outcome. The key is a tuple and the value
        is a number.
        """
        self.var_ids = var_ids
        self.var_dict = var_dict
        self.mf_dict = mf_dict
        self.tree = None

    def _construct_tree(self):
        self.tree = treelib.Tree()
        root_id = tuple(sorted(self.var_ids))
        self.tree = populate_syn_tree(self.tree, None, root_id,
                                      self.mf_dict)

    def _all_keys_sorted(self):
        """
        Checks whether the keys of precomputed mutual information is sorted
        :return: true or false
        """
        sorted_keys = set([tuple(sorted(key)) for key in
                           self.mf_dict.keys()])
        return sorted_keys == set(self.mf_dict.keys())

    def _all_subset_mf_present(self):
        """
        Checks whether the the mutual information of all subsets are present
        :return: true or false
        """
        for subset in subsets(self.var_ids, include_self=True):
            if subset not in self.mf_dict.keys():
                Warning("subset not found: ", subset)
                return False
        return True

    def add_or_update_subset_mf(self, key, value):
        """
        Update precomputed mutual information
        :param key: a tuple of variable ids
        :param value: mutual information with an outcome
        """
        sorted_key = tuple(sorted(key))
        if sorted_key != key:
            raise RuntimeError("key is not sorted")
        self.mf_dict[key] = value

    def synergy_tree(self):
        """
        Return synergy tree
        :return: synergy tree
        """
        if not self._all_keys_sorted():
            raise RuntimeError("variables in subsets are not sorted")

        if not self._all_subset_mf_present():
            raise RuntimeError("subset mutual information not complete")
        self._construct_tree()
        return self.tree


class DisjointSerie:
    """
    Class to represent a disjoint serie as a list of sorted tuples. For
    example, if the set is (1, 2, 3, 4), example disjoint series are:
    -- (1,), (2, 3, 4)
    -- (2,), (1, 3, 4)
    -- (1, 2), (3, 4)
    """
    def __init__(self, series=None):
        if series is None:
            self.serie = []
        else:
            self.serie = series
            self._sort()

    def __eq__(self, other):
        if isinstance(other, DisjointSerie):
            return self.serie == other.serie
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # list of not hashable. frozenset is.
        return hash(frozenset(self.serie))

    def _sort(self):
        # first, sort each tuple
        for i in range(len(self.serie)):
            self.serie[i] = tuple(sorted(self.serie[i]))
        self.serie = sorted(self.serie)

    def _insertion_position(self, element):
        n = len(self.serie)
        if n == 0:
            return 0
        else:
            i = 0
            while i < n:
                if element > self.serie[i]:
                    i = i + 1
                else:
                    break
        return i

    def add(self, subset):
        """
        Add a subset represent with a tuple
        :param subset: a subset to be added
        :return: void
        """
        n = len(self.serie)
        if n == 0:
            self.serie.append(subset)
        else:
            i = 0
            while i < n:
                if subset > self.serie[i]:
                    i = i + 1
                else:
                    break
            self.serie.insert(i, subset)


def populate_syn_tree(tree, parent, current, mf_dict,
                      disjoint_series_dict=None):
    """
    A recursive method to populate the synergy tree from the current node.
    :param tree: synergy tree
    :param parent: parent id (a tuple)
    :param current: a tuple of variable names
    :param mf_dict: a dictionary of precomputed mutual information, key is a
    tuple of variables, value is the mutual information between the joint
    distribution of those variables and the outcome
    :return: synergy tree
    """
    # if tree has not been defined, or root not added
    if tree is None:
        raise ValueError("tree not initialized error")

    # if there is only one element, this is a leaf and there is no synergy to
    # compute
    if len(current) == 1:
        tree.create_node(current, current, parent=parent, data=None)
        return tree

    # if there are more than one element, find the partition that gives the
    # max summed mutual information, because:
    # synergy = I - max(I' + I'')
    mf_joint = mf_dict[current]

    # Important: set it slight below zero to avoid finding no partition at all (
    # when all
    #  mf of subsets is zero)
    mf_max_subset = -0.0000001
    # We should test all possible disjoint series,
    # instead of just testing bi-partitions.
    # It will take a long time to compute all complement series. One solution
    #  is to precompute them, and load them from disk
    if disjoint_series_dict is None or len(current) not in \
            disjoint_series_dict.keys():
        partitions = disjoint_series(set(current))
        best_partition = partitions.pop()
        for partition in partitions:
            mf_subset = []
            for i in range(len(partition.serie)):
                mf_subset.append(mf_dict[partition.serie[i]])
            if sum(mf_subset) > mf_max_subset:
                mf_max_subset = sum(mf_subset)
                best_partition = partition
    else:
        # disjoint_series_dict is using integers to represent each element
        # for example, (0,), (1, 2, 3)
        # need to convert them into variable ids, such as
        # ('V1',), ('V2', 'V3', 'V4')
        current_sorted = np.array(sorted(current))
        partitions = disjoint_series_dict[current_sorted.size]
        best_partition = partitions.pop()
        for partition in partitions:
            mf_subset = []
            for i in range(len(partition.serie)):
                key = tuple(current_sorted[list(partition.serie[i])])
                mf_subset.append(mf_dict[key])
            if sum(mf_subset) > mf_max_subset:
                mf_max_subset = sum(mf_subset)
                best_partition = partition

    synergy = mf_joint - mf_max_subset

    # update synergy of current node
    tree.create_node(current, current, parent=parent, data=synergy)

    # recursively call the function on left subset and right subset
    for i in range(len(best_partition.serie)):
        tree = populate_syn_tree(tree, current, best_partition.serie[i],
                                 mf_dict)

    return tree


def complement_pairs(parent_set, include_self=False):
    """
    Given a set, return the complement pairs of subsets
    :param parent_set: a set of variables
    :param include_self: whether to include (original set, empty set) in results
    :return: pairs of complement subsets
    """
    # use a set to store complement pairs
    # we use set so to remove duplicate pairs
    pairs = set()
    n = len(parent_set)
    if include_self:
        end = n
    else:
        end = n - 1
    for i in range(end):
        for combo in itertools.combinations(list(parent_set), i + 1):
            left = set(combo)
            right = parent_set.difference(left)
            if (tuple(sorted(right)), tuple(sorted(left))) not in pairs:
                pairs.add((tuple(sorted(left)), tuple(sorted(right))))

    return pairs


def disjoint_series(parent_set, include_self=False):
    """
    Given a set, return all series of disjoint subsets
    :param parent_set:
    :return:
    """
    # maintain three sets that store disjoint set series
    # one for series that are finalized
    # second for series that are waiting to be finalized
    # last for series that are recently generated
    done = set()
    intermediates = set()
    latest = set()

    # initialize intermediates by adding parent set
    parent_serie = DisjointSerie([tuple(sorted(parent_set))])
    intermediates.add(parent_serie)

    # while there are intermediates, process one by one by:
    # taking one intermediate serial out, divide each subset into a pair of
    # complement subset to form new series
    while len(intermediates) > 0:
        for intermediate in intermediates:
            done.add(intermediate)
            for i in range(len(intermediate.serie)):
                if len(intermediate.serie[i]) == 1:
                    continue
                else:
                    temp = intermediate.serie.copy()
                    to_partition = temp.pop(i)
                    c_pairs = complement_pairs(set(to_partition))
                    for left, right in c_pairs:
                        new_serie = temp.copy()
                        new_serie.append(left)
                        new_serie.append(right)
                        new_instance = DisjointSerie(sorted(new_serie))
                        if new_instance not in latest:
                            latest.add(new_instance)
        intermediates.clear()
        intermediates = latest
        latest = set()

    if not include_self:
        done.remove(parent_serie)
    return done


def subsets(parent_set, include_empty=False, include_self=False):
    """
    Given a set of variable names, return all subsets
    :param parent_set: a set, or tuple, of variables
    :return: a set of tuples, each one denoting a subset
    """
    s = set()
    n = len(parent_set)
    for i in range(n - 1):
        for combo in itertools.combinations(list(parent_set), i + 1):
            s.add(tuple(sorted(combo)))
    if include_empty:
        s.add(tuple())
    if include_self:
        s.add(tuple(sorted(parent_set)))
    return s


def trim_edges(conditional_mf_network, hpo_network, threshold=0.8):
    """
    Trim a conditional mutual information network based on the hierarchy of
    HPO. The trimming policy is as follows:
    Put edges into a priority queue based on conditional mutual information in
    respect to a disease. Pop one edge at a time. For each node of the edge (
    v, w), analyze its other neighbors (use v as an example):
    If the edge to the neighbor is no longer in the queue, nothing needs to
    be done;
    If the edge to the neighbor is still in the queue, check two conditions:
        if the neighbor is an ancestor of w, get rid of it because it is worse
        than w;
        if the neighbor is a descendant of w, we need to decide whether we
        want to keep the neighbor or w. We have a desire to keep the neighbor
        because it is more specific in HPO tree. But we also know that it and v
        carries less mutual information to disease than (v, w), so have a
        desire to keep w. In the end, we define a threshold (0 - 1): as
        along as the descendant carries a certain fraction of mf, we choose
        it over its ancestor (w).
    :param conditional_mf_network: a network of mutual information
    conditioned on a common variable
    :param hpo_network: a MultiDiGraph for hpo
    :return: a trimmed network
    """
    # make a copy of original conditional_mf_network
    trimmed = copy.deepcopy(conditional_mf_network)
    ordered_edges = sorted(conditional_mf_network.edges.data('mf'),
                           key=lambda edge: edge[2], reverse=True)
    # find the first edge from the remaining_edges that is still a valid edge
    #  in the conditional_mf_network
    remove_list = set()
    while len(ordered_edges) > 1:
        next_edge = ordered_edges.pop(0)
        v, w, mf = next_edge

        # check both nodes:
        # for each node, check neighbors:
        #   if neighbor is ancestor of the other node and the mf is
        # smaller, remove the node
        #   if neighbor is descendant of the other node and the mf is
        # still above a threshold (percentage), remove the current edge;
        # otherwise, remove the descendant
        if v not in remove_list:
            for neighbor in trimmed.adj[v].keys():
                mf_edge = trimmed[v][neighbor]['mf']
                # check whether the edge is waiting to be analyzed
                if (v, neighbor, mf_edge) in ordered_edges:
                    # note: to find ancestors of an ontology term,
                    # use networkx descendants
                    if neighbor in nx.descendants(hpo_network, w):
                        remove_list.add(neighbor)
                        logging.info('worse ancestor detected: {} for {}, '
                                     'remove {}'.format(neighbor, w, neighbor))
                    if w in nx.descendants(hpo_network, neighbor) and \
                            mf_edge/mf > threshold:
                        remove_list.add(w)
        if w not in remove_list:
            for neighbor in trimmed.adj[w].keys():
                mf_edge = trimmed[w][neighbor]['mf']
                # check whether the edge is waiting to be analyzed
                if (w, neighbor, mf_edge) in ordered_edges:
                    if neighbor in nx.descendants(hpo_network, v):
                        remove_list.add(neighbor)
                    if v in nx.descendants(hpo_network, neighbor) and \
                            mf_edge/mf > threshold:
                        remove_list.add(v)

    for node in remove_list:
        trimmed.remove_node(node)
    remove_list.clear()

    return trimmed


def precompute_disjoint_series(n, include_self=False, save_path=None):
    original_set = list(range(n))
    result = disjoint_series(original_set, include_self)
    if save_path is not None:
        try:
            with open(save_path, 'wb') as f:
                pickle.dump(result, f)
        except:
            Warning("cannot save result to {}".format(save_path))


###############################################################################
# the follow section can be deleted
###############################################################################

def bit_array(decimal, n):
    bit = format(decimal, '0{}b'.format(n))
    return [int(i) for i in bit]


def subsets2(parent_set, include_self=False, include_empty=False):
    parent_array = np.array(list(parent_set))
    n = len(parent_set)
    if n == 0:
        return np.empty(1)

    if include_empty:
        start = 0
    else:
        start = 1

    if include_self:
        end = 2**n
    else:
        end = 2**n - 1

    partition_bit = np.array([bit_array(i, n) for i in np.arange(start,
                         end)]).astype(bool)
    subset_array = np.array([parent_array[partition_bit[i, :]] for i in
                             np.arange(len(partition_bit))])
    return subset_array


def complement_pairs2(variable_list, include_self=False):
    """
    Given a list of variables, return the complement pairs of subsets.
    @TOTO: it is actually slower than the above one
    :param parent_set: a set of variables
    :return: pairs of complement subsets
    """
    # use a set to store complement pairs
    # we use set so to remove duplicate pairs
    variable_array = np.array(variable_list)
    n = variable_array.size
    if include_self:
        end = 2 ** (n - 1)
    else:
        end = 2 ** (n - 1) - 1
    partition_bit = np.array([bit_array(i, n - 1) for i in np.arange(end)])
    partition_bit = np.concatenate([np.repeat(1, len(partition_bit)).reshape(-1, 1),
                                    partition_bit], axis=-1)
    partition_bit_bool = partition_bit.astype(bool)
    # TODO: how to force the data type to be [[(),()]]
    pairs = np.array([(tuple(variable_array[partition_bit_bool[i, :]]),
                       tuple(variable_array[np.logical_not(
                           partition_bit_bool[i, :])]))
                      for i in np.arange(len(partition_bit_bool))])
    return pairs

def disjoint_series2(parent_set, include_self=False):
    """
    implement the above one with
    :param parent_set:
    :param include_self:
    :return:
    """
    # maintain three sets that store disjoint set series (each series is a
    # list):
    # one for series that are finalized
    # second for series that are waiting to be finalized
    # last for series that are recently generated
    done = set()
    intermediates = set()
    latest = set()

    # initialize intermediates by adding parent set
    parent_serie = DisjointSerie([tuple(parent_set)])
    intermediates.add(parent_serie)

    # while there are intermediates, process one by one by:
    # taking one intermediate serial out, divide each subset into a pair of
    # complement subset to form new series
    while len(intermediates) > 0:
        for intermediate in intermediates:
            done.add(intermediate)
            for i in range(len(intermediate.serie)):
                if len(intermediate.serie[i]) == 1:
                    continue
                else:
                    temp = intermediate.serie.copy()
                    to_partition = temp.pop(i)
                    c_pairs = complement_pairs2(list(to_partition),
                                                include_self=False)
                    for left, right in c_pairs:
                        new_serie = temp.copy()
                        new_serie.append(tuple(left))
                        new_serie.append(tuple(right))
                        new_instance = DisjointSerie(sorted(new_serie))
                        if new_instance not in latest:
                            latest.add(new_instance)
        intermediates.clear()
        intermediates = latest
        latest = set()

    if not include_self:
        done.pop(0)
    return done


if __name__=='__main__':
    print(sys.argv)