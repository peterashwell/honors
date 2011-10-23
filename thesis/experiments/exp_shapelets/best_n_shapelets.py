import random
import sys
import os
import math
from operator import itemgetter
import distances
import lightcurve
import matplotlib.pyplot as plt

NUM_CROSSFOLDS = 10 # todo config this

shapelet_dir = sys.argv[1]
threshold = float(sys.argv[2]) # min-link threshold
force = False # recompute directories
if len(sys.argv) > 3: # extra args
	if sys.argv[3] == "-force" or sys.argv[3] == "-f":
		force = True
		print "forcing recomputation of best shapelets"

distance_function = distances.mindist

SHAPELET_SOURCE_DIR = "lightcurves/norm_n0.0_a100_m0_s400" # TODO unhack this
NUM_CLUSTERS_PER_CLASS = 40
MAX_SHAPELETS_CLUSTERED = 2000
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
	sh_data_clusters = [] # store data about the clusters
	sh_ts_clusters = [] # for us to work on
	num_shapelets = len(class_shapelet_scores[sh_class])
	print num_shapelets, "total to potentially process"
	best_shapelet_set = [] # keep track of maximum number of clusters
	shapelet_info = {}
	for sh_num, shapelet_data in enumerate(class_shapelet_scores[sh_class]):
		if sh_num > MAX_SHAPELETS_CLUSTERED:
			break
		if sh_num % 200 == 0:
			print "{0}/{1}".format(sh_num, num_shapelets),"done"
		#print "information gain:", shapelet_data[4]
		jointo = set() # cluster numbers to join to
		#print shapelet_data
		#print shapelet_data[1]
		#print shapelet_data[1].split('/')[-1]
		filename = shapelet_data[1].split('/')[-1] # grab the filename
		#print filename
		#print SHAPELET_SOURCE_DIR + "/" + filename
		source_ts = lightcurve.file_to_lc(SHAPELET_SOURCE_DIR + "/" + filename)
		shapelet_flux = source_ts.flux[int(shapelet_data[2]):int(shapelet_data[2]) + int(shapelet_data[3])]
		shapelet_time = source_ts.time[int(shapelet_data[2]):int(shapelet_data[2]) + int(shapelet_data[3])]
		shapelet_ts = lightcurve.LightCurve(shapelet_time, shapelet_flux)
		shapelet_info[shapelet_ts] = shapelet_data
		for clust_num, clust in enumerate(sh_ts_clusters):
			#print "\tcomparing to cluster", clust
			for elem in clust:
				if len(elem.flux) != len(shapelet_flux): # use different lengths
					continue
				dist = distance_function(elem.flux, shapelet_flux)
				#print "\t\tdistance:", dist, "threshold:", threshold
				#print float(dist) < float(threshold)
				if dist < threshold:
					jointo.add(clust_num)
					break
					#print "distance:", dist, "is less than:", threshold, "see:", dist < threshold 
					#print "joining..."
					#print "joining to:", clust_num, "with value:", 
		new_ts_cluster = [shapelet_ts]
		new_shdata_cluster = [shapelet_data]
		#print "jointo:", jointo
		beforelen = len(sh_ts_clusters)
		for join_cluster_num in jointo:
			#print join_cluster_num 
			new_ts_cluster += sh_ts_clusters[join_cluster_num]
			new_shdata_cluster += sh_data_clusters[join_cluster_num]
		# Remove the old clusters in the correct order
		for remove_index in sorted(jointo, reverse=True):
			sh_ts_clusters.pop(remove_index)
			sh_data_clusters.pop(remove_index)
		# Now add the new ones
		sh_ts_clusters.append(new_ts_cluster)
		sh_data_clusters.append(new_shdata_cluster)
		#print sh_data_clusters
		#print "number of clusters: ", len(sh_ts_clusters)
		#for n, clust in enumerate(sh_data_clusters):
		#	print "cluster", n
		#	for obj in clust:
		#		print "\t",obj
		if len(sh_ts_clusters) != beforelen:
			print "new number of clusters:", len(sh_ts_clusters), "was",beforelen, "before"
			if len(sh_ts_clusters) > beforelen:
				best_shapelet_set = sh_data_clusters[:]
		if len(sh_ts_clusters) >= NUM_CLUSTERS_PER_CLASS:
			break
	for cnum, ts_list in enumerate(best_shapelet_set):
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
