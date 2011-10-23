import random
import sys
import os
import math
from operator import itemgetter
import distances
import lightcurve
import matplotlib.pyplot as plt
import scipy.cluster
import cluster

NUM_CROSSFOLDS = 10 # todo config this


def shapelet_distance(sh_a, sh_b):
	if len(sh_a[0]) != len(sh_b[0]):
		return 1e10
	else:
		return distances.md(sh_a[1], sh_b[1])

shapelet_dir = sys.argv[1]
threshold = float(sys.argv[2]) # min-link threshold
force = False # recompute directories
if len(sys.argv) > 3: # extra args
	if sys.argv[3] == "-force" or sys.argv[3] == "-f":
		force = True
		print "forcing recomputation of best shapelets"

distance_function = distances.mindist

SHAPELET_SOURCE_DIR = "lightcurves/norm_n0.0_a100_m0_s400" # TODO unhack this
NUM_CLUSTERS_PER_CLASS = 20
NUM_CLUSTERS_PER_FILE = 20
MAX_SHAPELETS_CLUSTERED = 1000
# Read in shapelet_id file and do min link clustering, stopping at 20 
print "ranking shapelets"
for cfnum in xrange(1):
	shfile = "{0}/cf{1}/shapelet_ids".format(shapelet_dir,cfnum)
	class_shapelet_scores = {} # Information gain score
	for line in open(shfile):
		line = line.strip().split(',')
		sh_class = line[1].split('/')[-1].split('_')[0]
		if sh_class not in class_shapelet_scores.keys():
			class_shapelet_scores[sh_class] = [line]
		else:
			class_shapelet_scores[sh_class].append(line)
# make directory to store best shapelets
best_shapelet_dir = "{0}/cf0/bestshapelets".format(shapelet_dir)
if not os.path.isdir(best_shapelet_dir):
	os.mkdir(best_shapelet_dir)
for sh_class in class_shapelet_scores.keys():
	print "finding clusters for class:", sh_class
	class_shapelet_scores[sh_class].sort(key=lambda o: float(o[4]), reverse=False)
	# compute distances between all shapelets
	shapelets = []
	shapelet_info = {}
	for sh_num, shapelet_data in enumerate(class_shapelet_scores[sh_class][:MAX_SHAPELETS_CLUSTERED]):
		filename = shapelet_data[1].split('/')[-1] # grab the filename
		source_ts = lightcurve.file_to_lc(SHAPELET_SOURCE_DIR + "/" + filename)
		shapelet_flux = source_ts.flux[int(shapelet_data[2]):int(shapelet_data[2]) + int(shapelet_data[3])]
		shapelet_time = source_ts.time[int(shapelet_data[2]):int(shapelet_data[2]) + int(shapelet_data[3])]
		shapelet_ts = lightcurve.LightCurve(shapelet_time, shapelet_flux)
		shapelet_info[shapelet_ts] = shapelet_data
		shapelets.append(shapelet_ts)
	distances = scipy.zeros((len(shapelets), len(shapelets)))
	#for i in xrange(len(shapelets)):
	#	if i % 20 == 0:
	#		print "done", i
	#	for j in xrange(i + 1, len(shapelets)):
	#		if i == j:
	#			continue
	#		else:
	#			distances[i, j] = distance_function(shapelets[i].flux,shapelets[j].flux)
	#print distances
	#clustering = scipy.cluster.hierarchy.average(distances)
	#unmerged = [True for i in xrange(len(shapelets))] # keeps track of what's merged and what isn't
	#clusters = [[shapelet_info[shapelets[i]]] for i in xrange(len(shapelets))] # starting clusters
	#print "merging clusters from 0 to", len(shapelets) - NUM_CLUSTERS_PER_CLASS
	#for i in xrange(len(shapelets) - NUM_CLUSTERS_PER_CLASS): # start merging until we have NCPC clusters
	#	join_a = int(clustering[i,0])
	#	join_b = int(clustering[i,1])
	#	print "joining",join_a, "to", join_b
		#print "clusters:", clusters[join_a], clusters[join_b]
	#	clusters.append(clusters[join_a] + clusters[join_b])
	#	unmerged[join_a] = False
	#	unmerged[join_b] = False
	#	unmerged.append(True) # to represent this cluster
	print len(shapelets), "ASDASDASDFSDf"
	print "AS:DFASL:HAJERH:AJEH:"
	for i in xrange(len(shapelets)):
		print "i:",i
		for j in xrange(len(shapelets)):
			sys.stdout.write(str(shapelet_distance(shapelets[i], shapelets[j])) + '\t')
		print
	clust_obj = KMeansClustering(shapelets, lambda s1, s2: shapelet_distance(s1, s2))
	clust_obj.setLinkageMethod('average')
	final_clustering = clust_obj.getClusters(NUM_CLUSTERS_PER_FILE)
	for clusternum, cluster in enumerate(final_clustering):
		print "cluster number:", clusternum, "size:", len(cluster)
		for obj in cluster:
			print obj
	for cnum, ts_list in enumerate(final_clustering):
	for i in xrange(len(clusters)): # find unmerged clusters
		if unmerged[i]:
			final_clustering.append(clusters[i])
	print final_clustering
	print len(final_clustering), "clusters"
		candidate = random.choice(sorted(ts_list, key=lambda o: float(o[5]), reverse=True))
		#print sh_info
		source_filename = candidate[1].split('/')[-1]
		#print source_filename
		print "source filename:", source_filename
		source = lightcurve.file_to_lc(SHAPELET_SOURCE_DIR + "/" +  source_filename)
		sh_start = int(candidate[2])
		sh_end = int(candidate[3]) + sh_start
		#print sh_start, sh_end	
		#print source
		#print source.time
		plt.plot(source.time[:sh_start], source.flux[:sh_start], 'k', source.time[sh_end:], source.flux[sh_end:], 'k', source.time[sh_start:sh_end], source.flux[sh_start:sh_end], 'r')
		plt.xlabel('Time (days)')
		plt.ylabel('Flux (mJy, normalised)')
		plt.savefig(best_shapelet_dir + "/" + sh_class + "_shapelet" + str(cnum) + ".pdf", format="pdf")
		plt.close()
	#print sh_data_clusters
	#print "number of clusters: ", len(sh_ts_clusters)
	#for n, clust in enumerate(sh_data_clusters):
	#	print "cluster", n
	#	for obj in clust:
	#		print "\t",obj
