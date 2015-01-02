# Author: Silun Wang
# Clustering method
import math
from operator import itemgetter
from collections import OrderedDict
import multiprocessing

# last min distances
upbound = 200
vectors = []


def read_file(url):
    result = []
    f = open(url)
    line = f.readline()
    i = 0
    while line:
        str = line.split(' ')
        result.append(map(float, str[0:len(str) - 1]))
        line = f.readline()
        if i > upbound:
            break
        else:
            i += 1
    f.close()
    return result


def getCosineSimilarity(arr1, arr2):
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


def get_P2P_distance(start, end, que):
    # global minClusterDistance
    global vectors
    maxClusterSimilarity = 0
    p2pDist = {}
    for xIndex in xrange(start, end):
        # print xIndex
        for yIndex in xrange(len(vectors)):
            # avoid  redundant computation
            if xIndex < yIndex:
                # calculate cosine similarity
                '''
                up = np.dot(vectors[xIndex], vectors[yIndex])
                down = np.linalg.norm(np.array(vectors[xIndex]), ord=2) * np.linalg.norm(np.array(vectors[yIndex]),
                                                                                         ord=2)
                if up == 0 or down == 0:
                    continue
                cosine = up / down
                '''
                cosine = getCosineSimilarity(vectors[xIndex], vectors[yIndex])
                if cosine > 0:
                    p2pDist[str(xIndex) + "-" + str(yIndex)] = cosine
                    p2pDist[str(yIndex) + "-" + str(xIndex)] = cosine
                    if cosine > maxClusterSimilarity:
                        maxClusterSimilarity = cosine
    print str(start) + " over"
    return que.put((maxClusterSimilarity, p2pDist))


centers = []
scores = []
clusters = []


def calculateScores(clusterNum):
    global centers, vectors, scores
    for i in xrange(len(centers)):
        if i == clusters[i]:
            for j in xrange(len(centers[i][2])):
                centers[i][2][j] /= float(centers[i][1])
    for j in xrange(len(vectors)):
        '''
        up = np.dot(vectors[j], centers[clusters[j]][2])
        down = np.linalg.norm(np.array(vectors[j]), ord=2) * np.linalg.norm(np.array(centers[clusters[j]][2]),
                                                                            ord=2)
        if up == 0 or down == 0:
            scores.append(0.0)
        else:
            cosine = up / down
            scores.append(cosine)
        '''
        scores.append(getCosineSimilarity(vectors[j], centers[clusters[j]][2]))
    return


def main():
    maxClusterSimilarity = 0
    global vectors, centers, clusters
    vectors = read_file("../file/initial_feature_100.txt")
    # multiprocessing pool
    processNum = 8
    p2pDist = {}
    procs = []
    queue = multiprocessing.Queue()
    start = 0
    # start processes
    for i in xrange(processNum):
        if i < processNum - 1:
            end = start + len(vectors) / processNum
        else:
            end = len(vectors)
        p = multiprocessing.Process(target=get_P2P_distance, args=(start, end, queue))
        procs.append(p)
        p.start()
        start = end
    # combine result
    for i in range(processNum):
        tempMaxSimilarity, tempDict = queue.get()
        p2pDist = dict(p2pDist, **tempDict)
        maxClusterSimilarity = max(maxClusterSimilarity, tempMaxSimilarity)
    # dispose
    for p in procs:
        p.join()

    # sort
    p2pDist = OrderedDict(sorted(p2pDist.iteritems(), key=itemgetter(1), reverse=False))
    clusters = [idx for idx in xrange(len(vectors))]
    # cluster number, points number, center vector
    centers = [(index, 1, vectors[index]) for index in xrange(len(vectors))]
    clusterNum = len(clusters)
    # aggregation
    while maxClusterSimilarity > 0.5:
        # get nearest points
        points, maxClusterSimilarity = p2pDist.popitem()
        pointA = int(points.split('-')[0])
        pointB = int(points.split('-')[1])
        pointACluster = clusters[pointA]
        pointBCluster = clusters[pointB]
        # not the same cluster
        if pointACluster != pointBCluster:
            for idx in xrange(len(clusters)):
                # A, B cluster combine
                if clusters[idx] == pointBCluster:
                    clusters[idx] = pointACluster
                    clusterid, pointNum, vector = centers[pointACluster]
                    # update center vectors
                    centers[idx] = (pointA, pointNum + 1, [x + y for x, y in zip(vector, vectors[idx])])
                    centers[pointACluster] = centers[idx]
            clusterNum -= 1

    print "Cluster number: " + str(clusterNum)
    calculateScores(clusterNum)
    writeFile('../output/result.txt')
    return


def writeFile(url):
    global vectors, clusters, scores
    f = open(url, 'w')
    for index in xrange(len(vectors)):
        f.write(str(index) + '\t' + str(clusters[index]) + '\t' + str(scores[index]) + '\n')
    f.close()


main()


