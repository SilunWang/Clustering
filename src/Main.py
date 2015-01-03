__author__ = 'Allen'
from KMeans import KMeans_clustering
from HierachyClustering import hierachy_clustering

k = 250
hierachy_clustering(k, 4000)
KMeans_clustering(k)