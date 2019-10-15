import numpy as np
import pandas as pd
import os
import logging.config

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'log_config.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)

class SummaryXY:
    """
    Class to represent the summary statistics of X, Y. X, Y each is a vector
    of random variables.
    """
    def __init__(self, X_names, Y_names):
        self.X_names = np.array(X_names)
        self.Y_names = np.array(Y_names)
        self.M1 = len(self.X_names)
        self.M2 = len(self.Y_names)
        self.m = np.zeros([self.M1, self.M2, 4])
        self.N = 0

    def add_batch(self, X, Y):
        """
        Add a batch of observations for X and Y
        :param X: a N x M1 matrix of binary values for random variables in X
        :param Y: a N x M2 matrix of binary values for random variables in Y
        :return: updated summary statistics of X and Y
        """
        assert X.shape[1] == self.M1
        assert Y.shape[1] == self.M2
        assert X.shape[0] == Y.shape[0]
        n = X.shape[0]
        self.N = self.N + n
        d = np.repeat(1, n)
        s = summarize_XYz(X, Y, d)[:, :, [0, 2, 4, 6]]
        self.m = self.m + s


class SummaryXYz:
    def __init__(self, X_names, Y_names, z_name):
        # name of random variables
        self.vars_labels = {'set1': np.array(X_names),
                            'set2': np.array(Y_names)}
        self.z_name = z_name
        self.M1 = len(X_names)
        self.M2 = len(Y_names)
        # set1: summary statistics for the joint distribution of xz, x is one
        #  of the random variables in X. dimension, M1 x 4
        # set2: summary statistics for the joint distribution of yz, y is one
        #  of the random variables in Y. dimension, M2 x 4
        # column: counts for joint distribution of xz or yz in the following
        # order: ++, +-, -+, --
        self.m1 = {'set1': np.zeros([self.M1, 4]),
                   'set2': np.zeros([self.M2, 4])}

        # summary statistic for the joint distribution of xyz, x is one of
        # the random variables in X, y is one of the random variables in Y
        # dimension 1: number of random variables in X
        # dimension 2: number of random variables in Y
        # dimension 3: counts for joint distribution of xyz in the
        # following order: +++, ++-, +-+, +--, -++, -+-, --+, ---
        self.m2 = np.zeros([self.M1, self.M2, 8])

        # count of 1s of z
        self.case_N = 0
        # count of 0s of z
        self.control_N = 0

        self.S = np.empty(1)

    def add_batch(self, P1, P2, d):
        """
        Add a batch of samples for the current disease. Calling this
        function automatically update summary statistics.
        :param P: a batch_size X M matrix of phenotype profiles
        :param d: a batch_size vector of binary values representing
        the presence (1) or absence (0) of the disease
        :return: None
        """
        self.m1, self.m2, self.case_N, self.control_N = summarize(
            P1, P2, d, current=[self.m1, self.m2, self.case_N, self.control_N])

class MutualInformation:

    def __init__(self, x_name, y_name):
        self.x_name = x_name
        self.y_name = y_name
        self.x = np.array([])
        self.y = np.array([])

    def add_batch(self, x, y):
        assert len(x) == len(y)
        self.x = np.concatenate((self.x.reshape([1, -1]), np.array(
            x).reshape([1, -1])), axis=1)
        self.y = np.concatenate((self.y.reshape([1, -1]), np.array(
            y).reshape([1, -1])), axis=1)

    def mf(self):
        N = len(self.x)
        df = pd.DataFrame(data={'x_value': self.x, 'y_value': self.y})
        # count the observations
        dist = df.groupby(['x_value', 'y_value']).size.reset_index().rename(
            columns={0: 'N'})
        # partition the observations by x and return the total count for x value
        # same for y
        dist['x_count'] = dist.groupby('x_value').N.transform('count')
        dist['y_count'] = dist.groupby('y_value').N.transform('count')
        dist['p'] = dist['N'] / N
        dist['p_x'] = dist['x_count'] / N
        dist['p_y'] = dist['y_count'] / N
        mf = np.sum(dist.p * np.log2(dist.p / (dist.p_x * dist.p_y)))
        return mf


class MutualInfoXY:
    """
    Class to compute the mutual information between each pair of random
    variables in X and Y, where X and Y are two vectors of random variables
    whose values are binary (0 or 1).
    """

    def __init__(self, X_names, Y_names):
        self.X_names = np.array(X_names)
        self.Y_names = np.array(Y_names)
        self.M1 = len(self.X_names)
        self.M2 = len(self.Y_names)
        self.m = np.zeros([self.M1, self.M2, 4])
        self.N = 0

    def add_batch(self, X, Y):
        """
        Add a batch of observations for X and Y
        :param X: a N x M1 matrix of binary values for random variables in X
        :param Y: a N x M2 matrix of binary values for random variables in Y
        :return: updated summary statistics of X and Y
        """
        assert X.shape[1] == self.M1
        assert Y.shape[1] == self.M2
        assert X.shape[0] == Y.shape[0]
        n = X.shape[0]
        self.N = self.N + n
        d = np.repeat(1, n)
        s = summarize_XYz(X, Y, d)[:, :, [0, 2, 4, 6]]
        self.m = self.m + s

    def mf(self):
        """
        Compute and return the pairwise mutual information between variable
        pairs in X and Y
        :return: a M1 X M2 matrix of pairwise mutual information
        """
        p = self.m / self.N
        p_x = np.repeat(np.sum(self.m.reshape(self.M1, self.M2, 2, 2),
                               axis=-1), 2, axis=-1) / self.N
        p_y = np.tile(np.sum(self.m.reshape(self.M1, self.M2, 2, 2,
                              order='F'), axis=-1), [2]) / self.N
        temp = np.zeros_like(p)
        non_zero_idx = np.logical_not(np.array([p == 0]).squeeze())
        temp[non_zero_idx] = p[non_zero_idx] * np.log2(p[non_zero_idx]/(p_x[non_zero_idx] * p_y[non_zero_idx]))
        mutual_info = np.sum(temp, axis=-1)
        return mutual_info

    def mf_labeled(self):
        """
        Return a labeled dataframe instead of matrix
        :return: a dataframe
        """
        p1 = np.repeat(self.X_names, self.M2)
        p2 = np.tile(self.Y_names, [self.M1])
        mf_value = self.mf().ravel()
        df = pd.DataFrame(data={'P1': p1, 'P2': p2, 'mf': mf_value})
        return df

    def entropies(self):
        X_alone = self.m[:, 0, :].squeeze()
        assert X_alone.shape[0] == self.M1
        assert X_alone.shape[1] == 4
        X_alone_counts = np.sum(X_alone.reshape([self.M1, 2, 2]), axis=-1)
        h ={}
        h['X'] = entropy(X_alone_counts)

        Y_alone = self.m[0, :, :].squeeze()
        assert Y_alone.shape[0] == self.M2
        assert Y_alone.shape[1] == 4
        Y_alone_counts = np.sum(Y_alone.reshape([self.M2, 2, 2], order='F'),
                                axis=-1)
        h['Y'] = entropy(Y_alone_counts)

        return h


class MutualInfoXYz:
    """
    Class to represent and compute the pairwise synergy between a random
    variable X and a random variable Y in respect to random varialbe Z. The
    equations are given below:

    mutual information common to X and Y
    I(X;Y) =sum[p(x,y) * log2(p(x,y)/(p(x)*p(y)) for (x in X, y in Y)]
    synergy of X, Y in respect to Z
    Syn(X, Y; Z) = I(X, Y; Z) - [I(X;Z) + I(Y;Z)]

    For example, in health care study, X could be a set of abnormalities
    measured by radiology imaging, Y could be a set of abnormalities
    measured by clinical lab tests, while Z is the diagnosis of a particular
    disease.

    The class is a vectorized implementation, which means X, Y are two lists of
    random variables [X1, X2, ...] and [Y1, Y2, ...]. Z is a single random
    variable. The class is initialized by providing the names of Z (a string),
    X (a list of strings) and Y (a list of strings. An instance of the
    class takes in batches of data, a value vector for Z, a matrix for X and
    a matrix for Y, and automatically updates summary statistics. The
    mutual information between Z and each random variable of X, each random
    variable of Y, and the joint distribution of (X, Y),
    and the pairwise synergy between the joint distribution of X and Y in
    respect to Z are returned.

    To compute the synergy of phenotypic pairs, we need to get
    1. the values of a phenotype pair, ++, +-, -+, --;
    2. the values of diagnosis, which is provided;
    3. compute the joint value (diagnosis * phenotype pair) as a M x M x 8
    matrix. Organize 8 outcomes as (phenotype1, phenotype2, diagnosis): +++,
    ++-, +-+, +--, -++, -+-, --+, ---;
    4. compute the information content, sum(p * log2p);
    5. compute the synergy by subtracting out mutual information of
    individual phenotypes

    Reference paper:
    Anastassiou D, Computational analysis of the synergy among multiple
    interacting genes. Molecular System Biology 3:83
    """

    def __init__(self, X_names, Y_names, z_name):
        # disease id
        self.disease = z_name
        self.M1 = len(X_names)
        self.M2 = len(Y_names)
        # summary statistic for phenotype*diagnosis joint distribution
        # rows: phenotypes
        # column: ++, +-, -+, -- of phenotype*diagnosis joint distribution
        self.m1 = {'set1': np.zeros([self.M1, 4]),
                   'set2': np.zeros([self.M2, 4])}
        # summary statistic for phenotype_pair*diagnosis joint distribution
        # dimension 1: phenotype 1
        # dimension 2: phenotype 2
        # dimension 3: +++, ++-, +-+, +--, -++, -+-, --+, --- of phenotype1
        # * phenotype 2 * diagnosis joint distribution
        self.m2 = np.zeros([self.M1, self.M2, 8])
        # count of positive diagnoses
        self.case_N = 0
        # count of negative diagnoses
        self.control_N = 0
        # name of phenotypes
        self.vars_labels = {'set1': np.array(X_names),
                            'set2': np.array(Y_names)}
        self.S = np.empty(1)

    def set_XY_labels(self, vars_X_label, vars_Y_label):
        """
        Set the label of phenotypes
        :param phenotype_list: a string vector for the names of phenotypes
        :return: None
        """
        assert len(vars_X_label) == self.M1
        assert len(vars_Y_label) == self.M2
        self.vars_labels['set1'] = np.array(vars_X_label)
        self.vars_labels['set2'] = np.array(vars_Y_label)

    def get_z_name(self):
        """
        Function to get the disease id
        :return: disease id
        """
        return self.disease

    def get_XY_names(self):
        """
        Function to get the phenotype list
        :return: phenotype list
        """
        return self.vars_labels

    def get_case_count(self):
        """
        Function to get the total count of cases
        :return: count of positive diagnoses
        """
        return self.case_N

    def get_control_count(self):
        """
        Function to get the total count of controls
        :return: count of negative diagnoses
        """
        return self.control_N

    def get_sample_size(self):
        """
        Function to get the total count of cases and controls
        :return: total sample size
        """
        return self.case_N + self.control_N

    def add_batch(self, P1, P2, d):
        """
        Add a batch of samples for the current disease. Calling this
        function automatically update summary statistics.
        :param P: a batch_size X M matrix of phenotype profiles
        :param d: a batch_size vector of binary values representing
        the presence (1) or absence (0) of the disease
        :return: None
        """

        self.m1, self.m2, self.case_N, self.control_N = summarize(
            P1, P2, d, current=[self.m1, self.m2, self.case_N, self.control_N])

    def mutual_information(self):
        """
        Calculate and return the mutual information between individual
        phenotypes and diagnosis, and between phenotype pairs and diagnosis.
        :return: two arrays--mutual information between individual phenotypes
        and the diagnosis, and mutual information between phenotype pairs
        and the diagnosis
        """
        Ia, _, _ = mf_Xz(self.m1['set1'], np.array([self.case_N,
                         self.control_N]))
        Ib, _, _ = mf_Xz(self.m1['set2'], np.array([self.case_N,
                         self.control_N]))
        I = {'set1': Ia,
             'set2': Ib}
        II = mf_XY_z(self.m2, np.array([self.case_N, self.control_N]))
        return I, II

    def pairwise_synergy(self):
        """
        Calculate the pairwise synergy of phenotype pairs for the current disease.
        :return: the synergy of phenotype pairs for the current disease
        """
        I, II = self.mutual_information()
        self.S = synergy(I['set1'], I['set2'], II)
        return self.S

    def pairwise_synergy_labeled(self):
        P1 = np.repeat(self.vars_labels['set1'], self.M2)
        P2 = np.tile(self.vars_labels['set2'], [self.M1])
        assert(len(P1) == len(P2))
        S = self.pairwise_synergy()
        df = pd.DataFrame(data = {'P1': P1, 'P2': P2, 'synergy':
            S.flat}).sort_values(by='synergy', ascending=False).reset_index(
            drop=True)
        return df

    def pairwise_synergy_labeled_with_p_values(self, p_values):
        P1 = np.repeat(self.vars_labels['set1'], self.M2)
        P2 = np.tile(self.vars_labels['set2'], [self.M1])
        assert (len(P1) == len(P2))
        S = self.pairwise_synergy()
        df = pd.DataFrame(data={'P1': P1, 'P2': P2, 'synergy':
            S.flat, 'p': p_values.flat}).sort_values(by='synergy', ascending=False).reset_index(
            drop=True)
        return df


class MutualInfoXXz:
    """
    This is a special case of the Synergy class. It only deals with one set
    of independent variables. The aim is to analyze the pairwise synergy
    between each random variables within the set in respect to the dependent
    variable.
    """

    def __init__(self, dependent_var_name, independent_var_names):
        self.synergy = MutualInfoXYz(z_name=dependent_var_name,
                                     X_names=independent_var_names,
                                     Y_names=independent_var_names)

    def set_independent_labels(self, phenotype_list):
        self.synergy.set_XY_labels(phenotype_list)

    def get_independent_var_names(self):
        """
        Function to get the phenotype list
        :return: phenotype list
        """
        return self.synergy.get_XY_names()['set1']

    def get_case_count(self):
        """
        Function to get the total count of cases
        :return: count of positive diagnoses
        """
        return self.synergy.case_N

    def get_control_count(self):
        """
        Function to get the total count of controls
        :return: count of negative diagnoses
        """
        return self.synergy.control_N

    def get_sample_size(self):
        """
        Function to get the total count of cases and controls
        :return: total sample size
        """
        return self.synergy.case_N + self.synergy.control_N

    def add_batch(self, P, d):
        """
        Add a batch of samples for the current disease. Calling this
        function automatically update summary statistics.
        :param P: a batch_size X M matrix of phenotype profiles
        :param d: a batch_size vector of binary values representing
        the presence (1) or absence (0) of the disease
        :return: None
        """
        self.synergy.add_batch(P, P, d)

    def mutual_information(self):
        """
        Calculate and return the mutual information between individual
        phenotypes and diagnosis, and between phenotype pairs and diagnosis.
        :return: two arrays--mutual information between individual phenotypes
        and the diagnosis, and mutual information between phenotype pairs
        and the diagnosis
        """
        I, II = self.synergy.mutual_information()
        return I['set1'], II

    def pairwise_synergy(self):
        """
        Calculate the pairwise synergy of phenotype pairs for the current disease.
        :return: the synergy of phenotype pairs for the current disease
        """
        return self.synergy.pairwise_synergy()

    def pairwise_synergy_labeled(self):
        return self.synergy.pairwise_synergy_labeled()

    def pairwise_synergy_labeled_with_p_values(self, p_values):
        return self.synergy.pairwise_synergy_labeled_with_p_values(p_values)


def summarize_z(z):
    """
    Calculate the summary statistics of a binary vector
    :param z: a vector of binary values (0, or 1).
    :return: the count of 1s and 0s.
    """
    case_N = np.sum(z)
    control_N = np.sum(1 - z)
    return np.array([case_N, control_N])


def summarize_Xz(X, z):
    """
    Calculate the summary statistics for the joint distribution of xz,
    x is a random variable in X
    :param X: a N x M matrix representing the profiles of X in N observations.
    Values are 0 or 1.
    :param z: a vector of binary values (0, or 1).
    :return: a M X 4 matrix for summary statistics. The first dimension (size
    M) indicates random variables, the second dimension represent 4 outcomes (
    ++, +-, -+, --) for the joint distribution of xz.
    """
    N, M = X.shape
    z = z.reshape([N, 1])
    pd = np.stack([np.sum(X * z, axis=0),
                   np.sum(X * (1 - z), axis=0),
                   np.sum((1 - X) * z, axis=0),
                   np.sum((1 - X) * (1 - z), axis=0)], axis=-1)
    return pd


def summarize_XYz(X, Y, z):
    """
    Calculate the summary statistics for the joint distribution of xyz,
    where x is a random variable in X, y is a random variable in Y, and z is
    a random varialbe. x, y, z all have binary outcomes.
    :param X: a N x M1 matrix representing the profiles of X in N
    observations. Each size M1 vector represent the values of M1 random
    variables of X.
    :param Y: a N x M2 matrix representing the profiles of Y in N
    observations. Each size M2 vector represent the values of M2 random
    variables of Y.
    :param z: a vector of binary values (0, or 1).
    :return: a M1 X M2 X 8 matrix for the summary statistics for joint
    distributions of xyz.
    First dimension, random variables of X;
    Second dimension, random variables of Y;
    Third dimension, eight outcomes for the joint distribution
    of xyz, +++, ++-, +-+, +--, -++, -+-, --+, ---
    """
    N1, M1 = X.shape
    N2, M2 = Y.shape
    assert N1 == N2
    N = N1
    p1_reshape1 = X.reshape([N, M1, 1])
    p2_reshape2 = Y.reshape([N, 1, M2])

    # distribution of phenotype pairs, 1 if both phenotypes are present, 0 otherwise
    pp = np.matmul(p1_reshape1, p2_reshape2)
    # compute the joint distribution of diagnosis and phenotype pairs
    z = z.reshape([N, 1, 1])
    # pp * d: 1 if both phenotypes are present and positive diagnosis
    joint = pp * z
    ppd = np.sum(joint, axis=0)  # summary count

    # pp * (1 - d): 1 if both phenotypes are present and negative diagnosis
    joint = pp * (1 - z)
    ppd = np.concatenate((ppd.reshape([M1, M2, 1]), np.sum(joint,
            axis=0).reshape([M1, M2, 1])), axis=-1)

    # distribution of phenotype pairs, 1 if phenotypes are +-, 0 otherwise
    pp = np.matmul(p1_reshape1, 1 - p2_reshape2)
    # pp * d: 1 if phenotypes are +- and positive diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * z, axis=0).reshape([M1, M2, 1])),
                         axis=-1)
    # pp * (1 - d): 1 if phenotypes are +- and negative diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * (1 - z), axis=0).reshape([M1, M2,
                                                                     1])), axis=-1)

    # distribution of phenotype pairs, 1 if phenotypes are -+, 0 otherwise
    pp = np.matmul(1 - p1_reshape1, p2_reshape2)
    # pp * d: 1 if phenotypes are -+ and positive diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * z, axis=0).reshape([M1, M2, 1])),
                         axis=-1)
    # pp * (1 - d): 1 if phenotypes are +- and negative diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * (1 - z), axis=0).reshape([M1, M2,
                                                                     1])), axis=-1)

    # distribution of phenotype pairs, 1 if phenotypes are --, 0 otherwise
    pp = np.matmul(1 - p1_reshape1, 1 - p2_reshape2)
    # pp * d: 1 if phenotypes are -- and positive diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * z, axis=0).reshape([M1, M2, 1])),
                         axis=-1)
    # pp * (1 - d): 1 if phenotypes are -- and negative diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * (1 - z), axis=0).reshape([M1, M2,
                                                                     1])), axis=-1)

    return ppd


def summarize(P1, P2, d, current=None):
    """
    Given patient profile matrix and diagnosis vector, return the counts of
    joint distribution.
    :param P: a N X M matrix of patient phenotype profile, N: sample size,
    M: number of phenotype set
    :param d: a vector representing patient diagnosis
    :param current: a list of summary statistics that new summary statistics
    will be added to
    :return: a list of summary statistics
    """
    N1, M1 = P1.shape
    N2, M2 = P2.shape
    assert N1 == N2
    N = N1
    if current is not None:
        m1, m2, case_N, control_N = current
    else:
    # m1 is a multi-dimension array for the counts of events for
    # the joint distribution of (diagnosis, phenotype)
        m1 = {'set1': np.zeros([M1, 4]),
              'set2': np.zeros([M2, 4])}

    # m2 is a multi-dimension array for the counts of events for
    # joint distribution of (diagnosis, phenotype1, phenotype2)
    # The dimensions:
    # M - phenotype 1
    # M - phenotype 2
    # 8 - 8 potential outcomes for the joint distribution of binary
    # variables diagnosis, phenotype 1, phenotype 2.
    # Values of the joint distribution is ordered in the following way:
    # Phenotype 1     Phenotype 2   diagnosis
    # 1 1 1
    # 1 1 0
    # 1 0 1
    # 1 0 0
    # 0 1 1
    # 0 1 0
    # 0 0 1
    # 0 0 0           1
        m2 = np.zeros([M1, M2, 8])
        case_N = 0
        control_N = 0

    # update the counts of cases and controls
    d_positive, d_negative = summarize_z(d)
    case_N = case_N + d_positive
    control_N = control_N + d_negative

    # compute summary statistics for diagnosis*phenotype
    pd = summarize_Xz(P1, d)
    m1['set1'] = m1['set1'] + pd
    pd = summarize_Xz(P2, d)
    m1['set2'] = m1['set2'] + pd

    # compute summary statistics for diagnosis*phenotype_pairs
    ppd = summarize_XYz(P1, P2, d)
    m2 = m2 + ppd

    return [m1, m2, case_N, control_N]


def mf_Xz(summary_Xd, summary_z):
    '''
    Given the summary statistics for single phenotypes, return the mutual
    information between each of them and diagnosis
    :param summary_Xd: summary statistics for the joint distribution of
    each x in X and z (++, +-, -+, --)
    :param summary_z: summary statistics for random variable z (+, -)
    :return: a vector of mutual information between each x in X and z
    '''
    case_N, control_N = summary_z
    M = summary_Xd.shape[0]
    N = case_N + control_N
    prob = summary_Xd / N
    prob_diag = case_N / N
    prob_pheno = np.sum(prob[:, [0,1]], axis=1)
    prob_diag_M = np.stack([np.repeat(prob_diag, M),
                            np.repeat(1 - prob_diag, M),
                            np.repeat(prob_diag, M),
                            np.repeat(1 - prob_diag, M)], axis=1)
    prob_pheno_M = np.stack([prob_pheno, prob_pheno, 1 - prob_pheno, 1 - prob_pheno], axis=1)
    # prob could be 0
    non_zero_idx = np.logical_and(prob != 0, prob_diag_M * prob_pheno_M != 0)
    temp = np.zeros_like(prob)
    temp[non_zero_idx] = prob[non_zero_idx] * np.log2(prob[non_zero_idx] / (
        prob_diag_M[non_zero_idx] * prob_pheno_M[non_zero_idx]))
    I = np.sum(temp, axis=1)
    return I, prob_diag, prob_pheno


def mf_XY_z(summary_XYz, summary_z):
    '''
    Given the summary statistics for XYz, return the mutual
    information between pairs of XY and z
    :param summary_Xd: summary statistics for the joint distribution of xy
    and z (++, +-, -+, --) for x in X and y in Y
    :param summary_z: summary statistics for random variable z (+, -)
    :return: the mutual information between joint distribution XY and z
    '''
    case_N, control_N = summary_z
    N = case_N + control_N
    prob_diag = case_N / N
    M1, M2 = summary_XYz.shape[0:2]
    prob = summary_XYz / N
    prob_pheno_M = np.repeat(prob[:,:,[1,3,5,7]] + prob[:,:,[0,2,4,6]], 2, axis=-1)
    prob_diag_M = np.tile(np.array([prob_diag, 1 - prob_diag]).reshape([1,1,2]), 4)
    temp = np.zeros([M1, M2, 8])
    non_zero_valued_indices = np.logical_and(prob != 0, prob_pheno_M * prob_diag_M != 0)
    temp2 = prob_pheno_M * prob_diag_M
    temp[non_zero_valued_indices] = np.log2(prob[non_zero_valued_indices] / temp2[non_zero_valued_indices])
    II = np.sum(prob * temp, axis=-1)
    return II


def synergy(I1, I2, II):
    """
    For three random variables, X, Y, Z, compute pairwise synergy given the
    mutual information of (X; Z), (Y; Z) and (X, Y; Z)
    between
    :param I1: a 1 X M1 vector, each scalar indicates the mutual information
    between one random variable X<sub>i<sub> and Z
    :param I2: a 1 X M2 vector, each scalar indicates the mutual information
    between one random variable Y<sub>i<sub> and Z
    :param II: a M1 X M2 matrix, each scalar indicates the mutual information
    between the joint distribution of (X<sub>i<sub>, Y<sub>j<sub>) and Z
    :return: a matrix of pairwise synergy between X<sub>i<sub> and
    Y<sub>j<sub> in respect to Z
    """
    M1 = len(I1)
    M2 = len(I2)
    assert M1, M2 == II.shape
    S = II - I1.reshape([M1, 1]) - I2.reshape([1, M2])

    return S


def entropy(X):
    """
    Vectorized implementation of entropy computation. Given the summary
    statistics of random variables X1, X2, ..., Xn, return the entropies of
    each as a vector.
    :param X: a M x 2 matrix. M is the number of random variables, 2 binary
    outcome counts, + and -.
    :return: a 1 x M vector.
    """
    TOTAL = np.sum(X, axis=-1).reshape([-1, 1])
    p = X / TOTAL
    temp = np.zeros_like(p)
    non_zero_idx = (p != 0)
    temp[non_zero_idx] = -p[non_zero_idx] * np.log2(p[non_zero_idx])
    entropies = np.sum(temp, axis=-1).squeeze()
    return entropies

def mf_XY_given_z(summary_XYz, summary_z):
    """
    Given the summary statistics, return the mutual information between X
    and Y conditioned on z. For single random variables x, y, z, the equation
    to compute I(x, y|z):
    I(x, y|z) = sum(p(x,y,z) * log2(p(z) * p(x, y, z) / p(x, z) * p(y, z)),
    x, y, z take all values in their space
    :param summary_Xd: summary statistics for the joint distribution of xy
    and z (++, +-, -+, --) for x in X and y in Y
    :param summary_z: summary statistics for random variable z (+, -)
    :return: the mutual information between joint distribution XY given z

    """
    case_N, control_N = summary_z
    N = case_N + control_N
    prob_diag = case_N / N
    M1, M2 = summary_XYz.shape[0:2]
    # dimension: M1, M2, 8
    # last axis: +++, ++-, +-+, +--, -++, -+-, --+, --- for xyz joint
    # distribution
    prob = summary_XYz / N

    # calculate Xz joint prob, order ++, +-, -+, --
    prob_Xz = np.sum(np.stack((prob[:, :, [0,1,4,5]], prob[:, :, [2,3,6,7]]),
                              axis=-1),axis=-1)
    ## need to repeat the values in the order: ++, +-, ++, +-, -+, --, -+, --
    prob_Xz = np.tile(prob_Xz.reshape([M1, M2, 2, 2]), 2).reshape([M1, M2, 8,
               1]).squeeze()

    # calculate Yz joint prob, order ++, +-, -+, --
    prob_Yz = np.sum(prob.reshape([M1, M2, 2, 4]), axis=2)
    ## repeat the values twice in the order: ++, +-, -+, --, ++, +-, -+, --
    prob_Yz = np.tile(prob_Yz, [1, 1, 2])

    # format z dimension in the order: +, -, +, -, +, -, +, -
    prob_z = np.tile(np.array([prob_diag, 1-prob_diag]), [4]).reshape([1, 1, 8])

    temp = np.zeros([M1, M2, 8])
    non_zero_valued_indices = np.logical_and(prob != 0,
                                             prob_Xz*prob_Yz != 0)

    temp[non_zero_valued_indices] = prob[non_zero_valued_indices] * \
                                    np.log2((prob_z * prob)[non_zero_valued_indices] /
                                    (prob_Xz[non_zero_valued_indices] * prob_Yz[non_zero_valued_indices]))
    mf_XY_condition_on_z = np.sum(temp, axis=-1)
    return mf_XY_condition_on_z



