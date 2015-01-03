__author__ = 'Allen'
# utils

from GlobalVars import centers
import numpy as np
import numpy.linalg as LA
import math


def get_numpy_cosine(v1, v2):
    up = np.dot(v1, v2)
    down = LA.norm(v1, ord=2) * LA.norm(v2, ord=2)
    if up == 0 or down == 0:
        return 0
    else:
        return up / down


def get_cosine(arr1, arr2):
    up = 0.0
    a_sq = 0.0
    b_sq = 0.0
    for a1, b1 in zip(arr1, arr2):
        up += a1 * b1
        a_sq += a1 * a1
        b_sq += b1 * b1
    down = math.sqrt(a_sq * b_sq)
    if up == 0 or down == 0:
        return 0
    else:
        return up / down


def read_vector_file(url, bound=20000):
    result = []
    f = open(url)
    line = f.readline()
    i = 0
    while line:
        str = line.split(' ')
        result.append(np.asarray(map(float, str[0:len(str) - 1])))
        line = f.readline()
        if i == bound:
            break
        else:
            i += 1
    f.close()
    return result


def write_center_file(center_num):
    f = open('../output/centers_' + str(center_num) + '.txt', 'w')
    center_list = []
    i = 0
    for index in xrange(len(centers)):
        if i == center_num:
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