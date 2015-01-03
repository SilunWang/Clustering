__author__ = 'Allen'

from fileUtils import *
from hclustering import get_cosine_Numpy


def main():
    cluster_centers = read_feature_file('../output/centers_250.txt')
    vectors = read_feature_file('../file/initial_feature_100.txt')
    rounds = 0
    # start
    while rounds < 20:
        print "round " + str(rounds)
        rounds += 1
        nearest_center_map = {}
        points_num_map = {}
        for vector_index in xrange(len(vectors)):
            max_similarity = 0
            # find nearest center
            for center_index in xrange(len(cluster_centers)):
                # similarity
                cosine = get_cosine_Numpy(vectors[vector_index], cluster_centers[center_index])
                if cosine > max_similarity:
                    max_similarity = cosine
                    nearest_center_map[vector_index] = center_index
                    if center_index in points_num_map:
                        points_num_map[center_index] += 1
                    else:
                        points_num_map[center_index] = 1
        # update centers
        for (vector_index, center_index) in nearest_center_map.items():
            np.add(cluster_centers[center_index], vectors[vector_index])
        for index in xrange(len(cluster_centers)):
            cluster_centers[index] /= (points_num_map[index] + 1)
    # end while
    f = open('../output/kmeans_250.txt', 'w')
    for index in xrange(len(vectors)):
        cosine = get_cosine_Numpy(vectors[index], cluster_centers[nearest_center_map[index]])
        f.write(str(index) + '\t' + str(nearest_center_map[index]) + '\t' + str(cosine) + '\n')
    f.close()


main()
