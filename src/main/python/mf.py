import numpy as np
import pandas as pd


def entropy_single(x):
    """
    Compute entropy of a single random variable X
    :param x: a single variable (X) value vector
    :return: the entropy of variable X
    """
    SIZE = len(x)
    x = pd.DataFrame(data= {'x': x})
    p = x.groupby('x').size() / SIZE
    return np.dot(p, np.log2(p))


def entropy_double(x, y):
    """
    Compute joint entropy of two random variables X,Y
    :param x: a single variable (X) value vector
    :param y: a single variable (Y) value vector
    :return: the joint entropy of X, Y
    """
    if len(x) != len(y):
        raise Exception('variables have different lengths ')
    SIZE = len(x)
    data = pd.DataFrame(data={'x': x, 'y': y})
    p = data.groupby(['x', 'y']).size() / SIZE
    return np.dot(p, np.log2(p))


def entropy(x, y=None):
    """
    Compute the entropy of single random variable X, or joint entropy of X, Y
    :param x: value vector of random varialbe X
    :param y: value vector of random variable Y
    :return:
    """
    if y is None:
        return entropy_single(x)
    else:
        return entropy_double(x, y)

def mutual_information(prob, axis=0):
    """
    Compute the mutual information of two random variables X, Y
    :param prob: a vector of probability masses
    :return: the mutual information common to X and Y
    """
    return np.sum(prob * np.log2(prob), axis=axis)


def entropy_phenotype(P, d):
    """
    Compute the mutual information of diagnosis-phenotype pairs.
    :param P: a MXN matrix of patient phenotype profiles, M-phenotypes, N-patients
    :param d: a vector representing patient diagnosis
    :return:
    """
    M, N = P.shape
    I = np.zeros(M)
    for i in np.arange(M):
        I[i] = entropy(P[i, :].reshape([1, N]), d)
    return I


def summarize_diagnosis(d):
    '''
    Calculate the summary statistics: count of positive diagnosis and negative diagnosis
    :param d:
    :return:
    '''
    case_N = np.sum(d)
    control_N = np.sum(1 - d)
    return case_N, control_N


def summarize_diagnosis_phenotype(P, d):
    '''
    Calculate the summary statistics of diagnosis*phenotype joint distributions
    :param P: phenotype profile matrix, N x M
    :param d: diagnosis vector
    :return: summary statistics. row, phenotype; column, counts in the order of Phenotype:diagnosis(++, +-, -+, --)
    '''
    N, M = P.shape
    d = d.reshape([N, 1])
    pd = np.stack([np.sum(P * d, axis=0),
                   np.sum(P * (1 - d), axis=0),
                   np.sum((1 - P) * d, axis=0),
                   np.sum((1 - P) * (1 - d), axis=0)], axis=-1)
    return pd


def summarize_diagnosis_phenotype_pair(P, d):
    '''
    Calculate the summary statistics of diagnosis*phenotype_pair joint distributions
    :param P: N x M phenotype profile. row, one record of phenotype profile; column, phenotype profile
    :param d: a size N vector representing diagnosis (0 or 1) for each phenotype profile
    :return: the summary statistics of diagnosis*phenotype_pair joint distribution
    '''
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
    Given the summary statistics for single phenotypes, return the
    :param m1: summary statistics for the joint distribution of diagnosis*phenotype (Phenotype:diagnosis(++, +-, -+, --)
    :param case_N: total count of cases
    :param control_N: total count of controls
    :return: mutual information of single phenotypes and diagnosis
    '''
    M = m1.shape[0]
    N = case_N + control_N
    prob = m1 / N
    prob_diag = case_N / N
    prob_pheno = np.sum(prob[:, 0:1], axis=0)
    prob_diag_M = np.stack([np.repeat(prob_diag, M),
                            np.repeat(1 - prob_diag, M),
                            np.repeat(prob_diag, M),
                            np.repeat(1 - prob_diag, M)], axis=1)
    prob_pheno_M = np.stack([prob_pheno, prob_pheno, 1 - prob_pheno, 1 - prob_pheno], axis=1)




def synergy(m1, m2, case_N, control_N):
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


    return S
