import numpy as np


class Synergy:
    """
    Class to compute the pairwise synergy of disease phenotypes. Initialize class by providing the disease id,
    and a list of HPO terms to analyze.

    Equations:
    mutual information common to X and Y
    I(X;Y) =sum[p(x,y) * log2(p(x,y)/(p(x)*p(y)) for (x in X, y in Y)]
    synergy of X, Y in respect to Z
    Syn(X, Y; Z) = I(X, Y; Z) - [I(X;Z) + I(Y;Z)]

    Reference paper:
    Anastassiou D, Computational analysis of the synergy among multiple interacting genes. Molecular System Biology 3:83
    """

    def __init__(self, disease, phenotype_list):
        # disease id
        self.disease = disease
        M = len(phenotype_list)
        # summary statistic for phenotype*diagnosis joint distribution
        # rows: phenotypes
        # column: ++, +-, -+, -- of phenotype*diagnosis joint distribution
        self.m1 = np.zeros([M, 4])
        # summary statistic for phenotype_pair*diagnosis joint distribution
        # dimension 1: phenotype 1
        # dimension 2: phenotype 2
        # dimension 3: +++, ++-, +-+, +--, -++, -+-, --+, --- of phenotype1 * phenotype 2 * diagnosis joint distribution
        self.m2 = np.zeros([M, M, 8])
        # count of positive diagnoses
        self.case_N = 0
        # count of negative diagnoses
        self.control_N = 0
        # name of phenotypes
        self.phenotype_label = np.array(phenotype_list)

    def set_phenotype_label(self, phenotype_list):
        """
        Set the label of phenotypes
        :param phenotype_list: a string vector for the names of phenotypes
        :return: None
        """
        assert len(phenotype_list) == len(self.phenotype_label)
        self.phenotype_label = np.array(phenotype_list)

    def get_disease(self):
        """
        Function to get the disease id
        :return: disease id
        """
        return self.disease

    def get_phenotype_list(self):
        """
        Function to get the phenotype list
        :return: phenotype list
        """
        return self.phenotype_label

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

    def add_batch(self, P, d):
        """
        Add a batch of samples for the current disease. Calling this function automatically update summary statistics.
        :param P: a batch_size X M matrix of phenotype profiles
        :param d: a batch_size vector of binary values representing the presence (1) or absence (0) of the disease
        :return: None
        """

        self.m1, self.m2, self.case_N, self.control_N = summarize(P, d, current=[self.m1, self.m2, self.case_N, self.control_N])

    def pairwise_synergy(self):
        """
        Calculate the pairwise synergy of phenotype pairs for the current disease.
        :return: the synergy of phenotype pairs for the current disease
        """
        I,_,_ = mf_diagnosis_phenotype(self.m1, self.case_N, self.control_N)
        II = mf_diagnosis_phenotype_pair(self.m2, self.case_N, self.control_N)
        S = synergy(I, II)
        return S


def summarize_diagnosis(d):
    """
    Calculate the summary statistics: count of positive diagnosis and negative diagnosis
    :param d: a vector of binary values (0, or 1) that indicates whether a diagnosis code is observed for each sample.
    :return: the count of cases and controls.
    """
    case_N = np.sum(d)
    control_N = np.sum(1 - d)
    return case_N, control_N


def summarize_diagnosis_phenotype(P, d):
    """
    Calculate the summary statistics of diagnosis*phenotype joint distributions
    :param P: a N x M matrix representing the phenotype profiles of N samples. One row represents one sample. Columns
    represent separate phenotypes. Values are 0 (corresponding phenotype is not observed for the sample) or 1
    (corresponding phenotype is observed for the sample).
    :param d: a vector of binary values (0, or 1) that indicates whether a diagnosis code is observed for each sample.
    :return: a M X 4 matrix of summary statistics. rows, phenotypes;
    columns, outcomes of Phenotype:diagnosis(++, +-, -+, --);
    values, the count of observed samples for the phenotype*diagnosis joint distribution.
    """
    N, M = P.shape
    d = d.reshape([N, 1])
    pd = np.stack([np.sum(P * d, axis=0),
                   np.sum(P * (1 - d), axis=0),
                   np.sum((1 - P) * d, axis=0),
                   np.sum((1 - P) * (1 - d), axis=0)], axis=-1)
    return pd


def summarize_diagnosis_phenotype_pair(P, d):
    """
    Calculate the summary statistics of diagnosis*phenotype_pair joint distributions
    :param P: a N x M matrix representing the phenotype profiles of N samples. One row represents one sample. Columns
    represent separate phenotypes. Values are 0 (corresponding phenotype is not observed for the sample) or 1
    (corresponding phenotype is observed for the sample).
    :param d: a vector of binary values (0, or 1) that indicates whether a diagnosis code is observed for each sample.
    :return: a M X M X 8 matrix for the summary statistics of diagnosis*phenotype_pair joint distributions.
    First dimension, phenotype 1;
    Second dimension, phenotype 2;
    Third dimension, eight outcomes for the joint distribution of phenotype_pair*diagnosis, +++, ++-, +-+, +--, -++, -+-, --+, ---
    """
    N, M = P.shape
    p_reshape1 = P.reshape([N, M, 1])
    p_reshape2 = P.reshape([N, 1, M])

    # distribution of phenotype pairs, 1 if both phenotypes are present, 0 otherwise
    pp = np.matmul(p_reshape1, p_reshape2)
    # compute the joint distribution of diagnosis and phenotype pairs
    d = d.reshape([N, 1, 1])
    # pp * d: 1 if both phenotypes are present and positive diagnosis
    joint = pp * d
    ppd = np.sum(joint, axis=0)  # summary count
    # pp * (1 - d): 1 if both phenotypes are present and negative diagnosis
    joint = pp * (1 - d)
    ppd = np.concatenate((ppd.reshape([M, M, 1]), np.sum(joint, axis=0).reshape([M, M, 1])), axis=-1)

    # distribution of phenotype pairs, 1 if phenotypes are +-, 0 otherwise
    pp = np.matmul(p_reshape1, 1 - p_reshape2)
    # pp * d: 1 if phenotypes are +- and positive diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * d, axis=0).reshape([M, M, 1])), axis=-1)
    # pp * (1 - d): 1 if phenotypes are +- and negative diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * (1 - d), axis=0).reshape([M, M, 1])), axis=-1)

    # distribution of phenotype pairs, 1 if phenotypes are -+, 0 otherwise
    pp = np.matmul(1 - p_reshape1, p_reshape2)
    # pp * d: 1 if phenotypes are -+ and positive diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * d, axis=0).reshape([M, M, 1])), axis=-1)
    # pp * (1 - d): 1 if phenotypes are +- and negative diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * (1 - d), axis=0).reshape([M, M, 1])), axis=-1)

    # distribution of phenotype pairs, 1 if phenotypes are --, 0 otherwise
    pp = np.matmul(1 - p_reshape1, 1 - p_reshape2)
    # pp * d: 1 if phenotypes are -- and positive diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * d, axis=0).reshape([M, M, 1])), axis=-1)
    # pp * (1 - d): 1 if phenotypes are -- and negative diagnosis
    ppd = np.concatenate((ppd, np.sum(pp * (1 - d), axis=0).reshape([M, M, 1])), axis=-1)

    return ppd

def summarize(P, d, current=None):
    """
    Given patient profile matrix and diagnosis vector, return the counts of
    joint distribution.
    :param P: a N X M matrix of patient phenotype profile, N: sample size, M: number of phenotype set
    :param d: a vector representing patient diagnosis
    :param current: a list of summary statistics that new summary statistics will be added to
    :return: a list of summary statistics
    """
    N, M = P.shape
    if current is not None:
        m1, m2, case_N, control_N = current
    else:
    # m1 is a multi-dimension array for the counts of events for
    # the joint distribution of (diagnosis, phenotype)
        m1 = np.zeros([M, 4])
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
        m2 = np.zeros([M, M, 8])
        case_N = 0
        control_N = 0

    # update the counts of cases and controls
    d_positive, d_negative = summarize_diagnosis(d)
    case_N = case_N + d_positive
    control_N = control_N + d_negative

    # compute summary statistics for diagnosis*phenotype
    pd = summarize_diagnosis_phenotype(P, d)
    m1 = m1 + pd

    # compute summary statistics for diagnosis*phenotype_pairs
    ppd = summarize_diagnosis_phenotype_pair(P, d)
    m2 = m2 + ppd

    return [m1, m2, case_N, control_N]


def mf_diagnosis_phenotype(m1, case_N, control_N):
    '''
    Given the summary statistics for single phenotypes, return the mutual information between each of them and diagnosis
    :param m1: summary statistics for the joint distribution of diagnosis*phenotype (Phenotype:diagnosis(++, +-, -+, --)
    :param case_N: total count of cases
    :param control_N: total count of controls
    :return: mutual information of single phenotypes and diagnosis
    '''
    M = m1.shape[0]
    N = case_N + control_N
    prob = m1 / N
    prob_diag = case_N / N
    prob_pheno = np.sum(prob[:, [0,1]], axis=1)
    prob_diag_M = np.stack([np.repeat(prob_diag, M),
                            np.repeat(1 - prob_diag, M),
                            np.repeat(prob_diag, M),
                            np.repeat(1 - prob_diag, M)], axis=1)
    prob_pheno_M = np.stack([prob_pheno, prob_pheno, 1 - prob_pheno, 1 - prob_pheno], axis=1)
    I = np.sum(prob * np.log2(prob / (prob_diag_M * prob_pheno_M)), axis=1)
    return I, prob_diag, prob_pheno


def mf_diagnosis_phenotype_pair(m2, case_N, control_N):
    '''
    Given the summary statistics for phenotype pairs, return the mutual information between each of them and diagnosis
    :param m2:
    :param case_N:
    :param control_N:
    :return:
    '''
    N = case_N + control_N
    prob_diag = case_N / N
    M = m2.shape[0]
    prob = m2 / N
    prob_pheno_M = np.repeat(prob[:,:,[1,3,5,7]] + prob[:,:,[0,2,4,6]], 2, axis=-1)
    prob_diag_M = np.repeat(np.array([prob_diag, 1 - prob_diag]).reshape([1,1,2]), 4, axis=-1)
    temp = np.zeros([M, M, 8])
    non_zero_valued_indices = np.logical_and(prob != 0, prob_pheno_M * prob_diag_M != 0)
    temp2 = prob_pheno_M * prob_diag_M
    temp[non_zero_valued_indices] = np.log2(prob[non_zero_valued_indices] / temp2[non_zero_valued_indices])
    II = np.sum(prob * temp, axis=-1)
    return II


def synergy(I, II):
    """
    Compute pairwise synergy of phenotypes in respect to one diagnosis
    :param P: a M x N matrix of patient phenotype profile
    :param d: a vector representing patient diagnosis
    :return: a matrix of pairwise synergy
    """
    # to compute the synergy of each pair, we need to get
    # 1. the values of a phenotype pair, ++, +-, -+, --
    # 2. the values of diagnosis, which is provided
    # 3. compute the joint value (diagnosis * phenotype pair) as a M x M x 8 matrix
    # organize 8 outcomes as (phenotype1, phenotype2, diagnosis): +++, ++-, +-+, +--, -++, -+-, --+, ---
    # 4. compute the information content, sum(p * log2p)
    # 5. compute the synergy by subtracting out mutual information of individual phenotypes

    # 1. compute the mutual information for single phenotypes and diagnosis
    M = len(I)
    S = II - I.reshape([M, 1]) - I.reshape([1, M])

    return S
