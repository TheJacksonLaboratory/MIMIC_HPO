import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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


def main():
    result()


if __name__ == '__main__':
    main()