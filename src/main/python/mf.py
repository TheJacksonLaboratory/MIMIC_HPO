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


def synergy(P, d):
    """
    Compute pairwise synergy of phenotypes in respect to one diagnosis
    :param P: a M x N matrix of patient phenotype profile
    :param d: a vector representing patient diagnosis
    :return: a matrix of pairwise synergy
    """
    M, N = P.shape
    # I is the mutual information between each phenotype and the diagnosis
    I = np.zeros(M)
    for i in np.arange(M):
        I[i] = entropy(P[i, :].reshape([1, N]), d)

    # S is the synergy matrix: each element indicates the synergy of phenotype pairs
    S = np.zeros(M * M).reshape([M, M])

    # to compute the synergy of each pair, we need to get
    # 1. the values of a phenotype pair, ++, +-, -+, --
    # 2. the values of diagnosis, which is provided
    # 3. compute the joint value (diagnosis * phenotype pair) as a M x M x 8 matrix
    # organize 8 outcomes as (phenotype1, phenotype2, diagnosis): +++, ++-, +-+, +--, -++, -+-, --+, ---
    # 4. compute the information content, sum(p * log2p)
    # 5. compute the synergy by subtracting out mutual information of individual phenotypes
    P = P.T
    p_reshape1 = P.reshape([N, M, 1])
    p_reshape2 = P.reshape([N, 1, M])
    pp = np.matmul(p_reshape1, p_reshape2)
    d = d.reshape[N, 1, 1]
    ppd = np.sum(pp * d, axis=0)
    ppd.stack(np.sum(pp * (1 - d), axis=0), axis=-1)
    pp = np.matmul(p_reshape1, 1 - p_reshape2)
    ppd.stack(np.sum(pp * d, axis=0), axis=-1)
    ppd.stack(np.sum(pp * (1 - d), axis=0), axis=-1)
    pp = np.matmul(1 - P.reshape1, p_reshape2)
    ppd.stack(np.sum(pp * d, axis=0), axis=-1)
    ppd.stack(np.sum(pp * (1 - d), axis=0), axis=-1)
    pp = np.matmul(1 - p_reshape1, 1 - p_reshape2)
    ppd.stack(np.sum(pp * d, axis=0), axis=-1)
    ppd.stack(np.sum(pp * (1 - d), axis=0), axis=-1)

    ppd = ppd / N
    ppd = ppd * np.log2(ppd)
    S = ppd - I.reshape([M, 1]) - I.reshape([1, M])
    return S


def main():
    np.random.seed(1)
    # v = np.array([0, 1, 1, 0, 1])
    # print(outer11(v))
    # print(outer10(v))
    # print(outer01(v))
    # print(outer00(v))

    diagnosis = np.repeat(np.random.random_integers(0, 1, 10), 8)
    phenotype = np.zeros(80).reshape([10, 8])
    for i in np.arange(10):
        phenotype[i] = np.random.random_integers(0, 1, 8)

    phenotype = phenotype.reshape([1, 80]).squeeze().astype('int')

    data = pd.DataFrame(data={'diag': diagnosis, 'phenotype': phenotype})
    p_matrix = data.phenotype.values.reshape([10, 8])



if __name__ == '__main__':
    main()