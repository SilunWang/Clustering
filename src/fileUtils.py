__author__ = 'Allen'

from globalVars import upper_bound, centers
import numpy as np


def read_feature_file(url):
    result = []
    f = open(url)
    line = f.readline()
    i = 0
    while line:
        str = line.split(' ')
        result.append(np.asarray(map(float, str[0:len(str) - 1])))
        line = f.readline()
        if i > upper_bound:
            break
        else:
            i += 1
    f.close()
    return result


def write_center_file(url):
    f = open(url, 'w')
    center_list = []
    i = 0
    for index in xrange(len(centers)):
        if i == 200:
            break
        if centers[index][0] in center_list:
            continue
        else:
            center_list.append(centers[index][0])
            i += 1
            for iteration in xrange(len(centers[index][2])):
                f.write(str(float(centers[index][2][iteration] / centers[index][1])) + " ")
            f.write("\n")
    f.close()
    print i