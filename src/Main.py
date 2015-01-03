__author__ = 'Allen'

from KMeans import KMeans_clustering
from HierachyClustering import hierachy_clustering
from Utils import judge

# cluster number
k = 120
# find initial centers
hierachy_clustering(k, 4000)
# update
KMeans_clustering(k, 20000)
print "average similarity for " + str(k) + " is: " + str(judge(k))