import numpy as np
import pandas as pd
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
    for i in np.arange(500):
        path = os.path.join(dir, '428_' + str(i) + '_distribution.obj')
        if os.path.exists(path):
            with open(path, 'rb') as f:
                simulation = pickle.load(f)
                simulations.append(simulation)

    return np.concatenate(tuple(simulations), axis=-1)



def main():
    path = '/Users/zhangx/git/MIMIC_HPO/src/main/resources/simulation_output'
    m = read_distribution(path, '428')
    print(m.shape)


if __name__ == '__main__':
    main()