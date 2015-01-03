# Author: Silun Wang
# Hierachy Clustering
from operator import itemgetter
from collections import OrderedDict
import multiprocessing
from Utils import *


def get_P2P_distance(start, end, que):
    # global minClusterDistance
    max_similarity = 0
    p2pDist = {}
    for xIndex in xrange(start, end):
        # print xIndex
        for yIndex in xrange(len(gl.vectors)):
            # avoid  redundant computation
            if xIndex < yIndex:
                cosine = get_numpy_cosine(gl.vectors[xIndex], gl.vectors[yIndex])
                if cosine > 0:
                    p2pDist[str(xIndex) + "-" + str(yIndex)] = cosine
                    p2pDist[str(yIndex) + "-" + str(xIndex)] = cosine
                    if cosine > max_similarity:
                        max_similarity = cosine
    print str(start) + " over"
    return que.put((max_similarity, p2pDist))


def calculate_scores():
    for i in xrange(len(gl.centers)):
        if i == gl.clusters[i]:
            for j in xrange(len(gl.centers[i][2])):
                gl.centers[i][2][j] /= float(gl.centers[i][1])
    for j in xrange(len(gl.vectors)):
        gl.scores.append(get_numpy_cosine(gl.vectors[j], gl.centers[gl.clusters[j]][2]))
    return


def hierachy_clustering(k, num):
    max_cluster_similarity = 0
    gl.vectors = read_vector_file("../input/initial_feature_100.txt", num)
    # multiprocessing pool
    process_num = 6
    p2pDist = {}
    processes = []
    queue = multiprocessing.Queue()
    start = 0
    # start processes
    for i in xrange(process_num):
        if i < process_num - 1:
            end = start + len(gl.vectors) / process_num
        else:
            end = len(gl.vectors)
        p = multiprocessing.Process(target=get_P2P_distance, args=(start, end, queue))
        processes.append(p)
        p.start()
        start = end
    # combine result
    for i in range(process_num):
        tempMaxSimilarity, tempDict = queue.get()
        p2pDist = dict(p2pDist, **tempDict)
        max_cluster_similarity = max(max_cluster_similarity, tempMaxSimilarity)
    # dispose
    for p in processes:
        p.join()
    # sort
    p2pDist = OrderedDict(sorted(p2pDist.iteritems(), key=itemgetter(1), reverse=False))
    gl.clusters = [idx for idx in xrange(len(gl.vectors))]
    # cluster number, points number, center vector
    gl.centers = [(index, 1, gl.vectors[index]) for index in xrange(len(gl.vectors))]
    clusterNum = len(gl.clusters)
    # aggregation
    while max_cluster_similarity > 0.55:
        # get nearest points
        points, max_cluster_similarity = p2pDist.popitem()
        pointA = int(points.split('-')[0])
        pointB = int(points.split('-')[1])
        pointACluster = gl.clusters[pointA]
        pointBCluster = gl.clusters[pointB]
        numA = gl.centers[pointACluster][1]
        numB = gl.centers[pointBCluster][1]
        if pointACluster == pointBCluster:
            continue
        if numA + numB < gl.max_points_number:
            # assign clusterB <-- clusterA
            for idx in xrange(len(gl.clusters)):
                # points in clusterB
                if gl.clusters[idx] == pointBCluster:
                    gl.clusters[idx] = pointACluster
                    # update center of clusterA
                    clusterid, pointNum, vector = gl.centers[pointACluster]
                    # update center vectors
                    gl.centers[idx] = (pointACluster, pointNum + 1, np.add(vector, gl.vectors[idx]))
                    gl.centers[pointACluster] = gl.centers[idx]
            clusterNum -= 1
        else:
            print "cluster overflow"

    print "Cluster number: " + str(clusterNum)
    sorted(gl.centers, key=lambda tup: tup[1], reverse=True)
    write_center_file(center_num=k)
    return




