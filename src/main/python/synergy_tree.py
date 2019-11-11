import itertools
import treelib


class SynergyTree:
    """
    Class to represent a synergy tree. An instance of the class takes in a
    set of variables and precomputed mutual information between subsets of
    variables and an outcome and generate a synergy tree
    """
    
    def __init__(self, var_ids, var_dict=None, precomputed_subset_mf=None):
        self.var_ids = var_ids
        self.var_dict = var_dict
        self.precomputed_mf = precomputed_subset_mf
        self.tree = None

    def _construct_tree(self):
        self.tree = treelib.Tree()
        root_id = tuple(sorted(self.var_ids))
        self.tree = populate_syn_tree(self.tree, None, root_id,
                                      self.precomputed_mf)

    def _all_keys_sorted(self):
        """
        Checks whether the keys of precomputed mutual information is sorted
        :return: true or false
        """
        sorted_keys = set([tuple(sorted(key)) for key in
                       self.precomputed_mf.keys()])
        return sorted_keys == set(self.precomputed_mf.keys())

    def _all_subset_mf_present(self):
        """
        Checks whether the the mutual information of all subsets are present
        :return: true or false
        """
        return self.precomputed_mf.keys() == subsets(self.var_ids)

    def add_or_update_subset_mf(self, key, value):
        """
        Update precomputed mutual information
        :param key: a tuple of variable ids
        :param value: mutual information with an outcome
        """
        sorted_key = tuple(sorted(key))
        if sorted_key != key:
            raise RuntimeError("key is not sorted")
        self.precomputed_mf[key] = value

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


def populate_syn_tree(tree, parent, current, mf_dict):
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
    mf_max_left_subset = set()
    mf_max_right_subset = set()

    mf_max_subset = 0
    partitions = complement_pairs(set(current))
    for partition in partitions:
        left, right = partition
        mf_left = mf_dict[left]
        mf_right = mf_dict[right]
        if mf_left + mf_right > mf_max_subset:
            mf_max_left_subset = set(left)
            mf_max_right_subset = set(right)
            mf_max_subset = mf_left + mf_right

    synergy = mf_joint - mf_max_subset

    # update synergy of current node
    tree.create_node(current, current, parent=parent, data=synergy)

    # recursively call the function on left subset and right subset
    left_id = tuple(sorted(mf_max_left_subset))
    tree = populate_syn_tree(tree, current, left_id, mf_dict)
    right_id = tuple(sorted(mf_max_right_subset))
    tree = populate_syn_tree(tree, current, right_id, mf_dict)

    return tree


def complement_pairs(parent_set):
    """
    Given a set, return the complement pairs of subsets
    :param parent_set: a set of variables
    :return: pairs of complement subsets
    """
    # use a set to store complement pairs
    # we use set so to remove duplicate pairs
    pairs = set()
    n = len(parent_set)
    for i in range(n - 1):
        for combo in itertools.combinations(list(parent_set), i + 1):
            left = set(combo)
            right = parent_set.difference(left)
            if (tuple(sorted(right)), tuple(sorted(left))) not in pairs:
                pairs.add((tuple(sorted(left)), tuple(sorted(right))))

    return pairs


def subsets(parent_set):
    """
    Given a set of variable names, return all subsets
    :param parent_set: a set, or tuple, of variables
    :return: a set of tuples, each one denoting a subset
    """
    s = set()
    n = len(parent_set)
    for i in range(n):
        for combo in itertools.combinations(list(parent_set), i + 1):
            s.add(tuple(sorted(combo)))

    return s
