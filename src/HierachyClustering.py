# Author: Silun Wang
# Hierachy Clustering
from operator import itemgetter
from collections import OrderedDict
import multiprocessing
from GlobalVars import max_points_number, vectors, scores, clusters
from Utils import *


def get_P2P_distance(start, end, que):
    # global minClusterDistance
    max_similarity = 0
    p2pDist = {}
    for xIndex in xrange(start, end):
        # print xIndex
        for yIndex in xrange(len(vectors)):
            # avoid  redundant computation
            if xIndex < yIndex:
                cosine = get_numpy_cosine(vectors[xIndex], vectors[yIndex])
                if cosine > 0:
                    p2pDist[str(xIndex) + "-" + str(yIndex)] = cosine
                    p2pDist[str(yIndex) + "-" + str(xIndex)] = cosine
                    if cosine > max_similarity:
                        max_similarity = cosine
    print str(start) + " over"
    return que.put((max_similarity, p2pDist))


def calculate_scores():
    for i in xrange(len(centers)):
        if i == clusters[i]:
            for j in xrange(len(centers[i][2])):
                centers[i][2][j] /= float(centers[i][1])
    for j in xrange(len(vectors)):
        scores.append(get_numpy_cosine(vectors[j], centers[clusters[j]][2]))
    return


def hierachy_clustering(k, num):
    max_cluster_similarity = 0
    global vectors, centers, clusters
    vectors = read_vector_file("../input/initial_feature_100.txt", num)
    # multiprocessing pool
    process_num = 6
    p2pDist = {}
    processes = []
    queue = multiprocessing.Queue()
    start = 0
    # start processes
    for i in xrange(process_num):
        if i < process_num - 1:
            end = start + len(vectors) / process_num
        else:
            end = len(vectors)
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
    clusters = [idx for idx in xrange(len(vectors))]
    # cluster number, points number, center vector
    centers = [(index, 1, vectors[index]) for index in xrange(len(vectors))]
    clusterNum = len(clusters)
    # aggregation
    while max_cluster_similarity > 0.55:
        # get nearest points
        points, max_cluster_similarity = p2pDist.popitem()
        pointA = int(points.split('-')[0])
        pointB = int(points.split('-')[1])
        pointACluster = clusters[pointA]
        pointBCluster = clusters[pointB]
        numA = centers[pointACluster][1]
        numB = centers[pointBCluster][1]
        if pointACluster == pointBCluster:
            continue
        if numA + numB < max_points_number:
            # assign clusterB <-- clusterA
            for idx in xrange(len(clusters)):
                # points in clusterB
                if clusters[idx] == pointBCluster:
                    clusters[idx] = pointACluster
                    # update center of clusterA
                    clusterid, pointNum, vector = centers[pointACluster]
                    # update center vectors
                    centers[idx] = (pointACluster, pointNum + 1, np.add(vector, vectors[idx]))
                    centers[pointACluster] = centers[idx]
            clusterNum -= 1
        else:
            print "cluster overflow"

    print "Cluster number: " + str(clusterNum)
    sorted(centers, key=lambda tup: tup[1], reverse=True)
    write_center_file(center_num=k)
    return




