import numpy as np
import matplotlib.pyplot as plt
import os.path
import pickle


def result():
    f = open('/Users/zhangx/git/MIMIC_HPO/src/main/resources/result-archive.txt', 'r')
    d = {}
    for line in f.readlines():
        score = line.split('=')[-1]
        d[line] = float(score)
    f.close()

    print(len(d))

    for e in sorted(d, key=d.get, reverse=True)[1:20]:
        print(e)

    syn = np.array(list(d.values()))
    syn = syn[np.logical_and(syn > -0.01, syn < 1)]

    #print(syn)

    plt.hist(syn, bins=20)
    plt.show()


def read_distribution(dir, disease):
    simulations = []
    for i in np.arange(5000):
        path = os.path.join(dir, '428_' + str(i) + '_distribution.obj')
        if os.path.exists(path):
            with open(path, 'rb') as f:
                simulation = pickle.load(f)
                simulations.append(simulation)

    return np.concatenate(tuple(simulations), axis=-1)

def plot_distribution(path):
    with open(path, 'rb') as f:
        subset = pickle.load(f)

    plt.hist(subset[0,0,:], bins=10)
    plt.show()



def main():
    path = '/Users/zhangx/git/MIMIC_HPO/src/main/resources/428empirical_distribution_subset.obj'
    with open(path, 'rb') as f:
        subset = pickle.load(f)

    fig, axs = plt.subplots(5, 5)
    for i in np.arange(5):
        for j in np.arange(5):
            data = subset[i,j,:] * 10000
            axs[i,j].hist(data, bins=25, color='g')
            #axs[i,j].set_xlabel('x10-5')
            axs[i,j].set_yticklabels([])
    plt.tight_layout()
    plt.show()


    #plot_distribution(path)


if __name__ == '__main__':
    main()