import random
from itertools import izip
import sys
import os
import math
from operator import itemgetter
import distances
import lightcurve
import matplotlib.pyplot as plt
import scipy.cluster
#import psyco
#psyco.full()

NUM_CROSSFOLDS = 10 # todo config this

shapelet_dir = sys.argv[1]
best_amt = int(sys.argv[2]) # number of shapelets to find (for each class)

SHAPELET_SOURCE_DIR = "lightcurves/norm_n0.0_a100_m0_s400" # TODO unhack this
shapelet_feature_name = shapelet_dir.split('/')[1]
SHAPELET_FEATURE_DIR = "shapelet_features/{0}-b{1}".format(shapelet_feature_name, best_amt)
SHAPELET_DEBUG_DIR = "shapelet_debug/{0}-b{1}".format(shapelet_feature_name, best_amt)
if not os.path.isdir(SHAPELET_FEATURE_DIR):
	os.mkdir(SHAPELET_FEATURE_DIR)
if not os.path.isdir(SHAPELET_DEBUG_DIR):
	os.mkdir(SHAPELET_DEBUG_DIR)

# If we only need the very single best for each class, skip the clustering
if best_amt == 1:
	
	for cfnum in xrange(NUM_CROSSFOLDS):
		print "crossfold:", cfnum
		debug_index = open(SHAPELET_DEBUG_DIR + '/cf{0}'.format(cfnum) + "_debug", 'w')
		shapelet_id_file = open("{0}/cf{1}/{2}".format(shapelet_dir, cfnum, "shapelet_ids"))
		best_shapelets = {}
		best = {}
		best_line = {}
		best_SD = {}
		#SH_INDEX = "shapelet_ids"
		#sh_file = open('{0}/{1}'.format(FOUND_DIR, SH_INDEX))
	
		for ln, line in enumerate(shapelet_id_file):
			#if ln % 1000 == 0:
			#	print "{0}/{1}".format(ln,"total")
			line = line.strip().split(',')
			sh_class = line[1].split('/')[-1].split('_')[0]
			update = False
			if sh_class not in best.keys():
				update = True
			elif line[-2] < best[sh_class]:
				update = True
			elif line[-2] == best[sh_class]:
				pass
				#if line[-1] < best_SD[sh_class]: # largest possible SD
				#	update = True
			if update:
				best_line[sh_class] = line
				best[sh_class] = line[-2]
				best_SD[sh_class] = line[-1]

		# Write these out to the appropriate directory
		out_dir = "{0}/cf{1}".format(SHAPELET_FEATURE_DIR, cfnum)
		if not os.path.isdir(out_dir):
			os.mkdir(out_dir)
		debug_dir = "{0}/cf{1}".format(SHAPELET_DEBUG_DIR, cfnum)
		if not os.path.isdir(debug_dir):
			os.mkdir(debug_dir)
		for sh_class in best_line.keys():
			print "class:", sh_class, "id:", best_line[sh_class][0]
			source_filename = best_line[sh_class][1].split('/')[-1]
			source = lightcurve.file_to_lc('{0}/{1}'.format(SHAPELET_SOURCE_DIR, source_filename))
			sh_start = int(best_line[sh_class][2])
			sh_end = int(best_line[sh_class][3]) + sh_start
			debug_index.write('{0},{1}\n'.format(sh_class, best_line[sh_class][0]))
			out_file = open("{0}/{1}_shapelet_{2}.data".format(out_dir, sh_class, cfnum), 'w') # c is the class
			print "writing to file:", out_file
			for t, f in izip(source.time[sh_start:sh_end], source.flux[sh_start:sh_end]):
				out_file.write('{0}\t{1}\n'.format(t,f))
			out_file.close()
			plt.plot(source.time[:sh_start], source.flux[:sh_start], 'k', source.time[sh_end:], source.flux[sh_end:], 'k', source.time[sh_start:sh_end], source.flux[sh_start:sh_end], 'r')
			plt.xlabel('Time (days)')
			plt.ylabel('Flux (mJy, normalised)')

			plt.savefig("{0}/{1}".format(debug_dir,\
				'{0}_shapelet{1}.pdf'.format(sh_class, 1), format="pdf"))
			plt.close()
		debug_index.close() # done with this crossfold
	exit()	
	
distance_function = distances.mindist # Use minimum distance function

def shapelet_distance(sh_a, sh_b):
	#if len(sh_a[0]) != len(sh_b[0]):
	#	return 1e10
	#else:
	return distance_function(sh_a[1], sh_b[1])[0]



FILE_INFGAIN_FRAC = 0.075 # Fraction of top information gain shapelets to take from a file
NUM_CLUSTERS_PER_FILE = 10 # Number of shapelets to attempt to extract from a file
NUM_CLUSTERS_PER_CLASS = best_amt
# Use scipy and distance measure to find a clustering up to num_clusters of the shapelets
def cluster_shapelets(shapelets, num_clusters):
	distances = scipy.zeros((len(shapelets),len(shapelets)))#(len(shapelets), len(shapelets)))
	print "computing distances for", len(shapelets), "shapelets"
	for i in xrange(len(shapelets)): #len(shapelets)):
		for j in xrange(i + 1, len(shapelets)): #len(shapelets)):
			if i == j:
				pass
			else:
				distances[i, j] = distance_function(shapelets[i][1], shapelets[j][1])[0]
	# Call scipy clustering code and utilise the output
	clustering = scipy.cluster.hierarchy.average(distances)
	
	unmerged = [True for i in xrange(len(shapelets))] # keeps track of what's merged and what isn't
	data_clusters = [[shapelets[i]] for i in xrange(len(shapelets))]
	for i in xrange(len(shapelets) - num_clusters):	
		join_a = int(clustering[i,0])
		join_b = int(clustering[i,1])
		#print "joining", join_a, join_b
		#print "clusters:", clusters[join_a], clusters[join_b]
		data_clusters.append(data_clusters[join_a] + data_clusters[join_b])
		unmerged[join_a], unmerged[join_b] = (False, False)
		unmerged.append(True) # to represent this cluster
	final_data_clusters = []
	for i in xrange(len(data_clusters)): # find unmerged clusters
		if unmerged[i]:
			final_data_clusters.append(data_clusters[i])
	print len(final_data_clusters), "clusters"
	#for clusternum, cluster in enumerate(final_data_clusters):
	#	print "cluster number:", clusternum, "size:", len(cluster)
	if len(final_data_clusters) == 0:
		raise Error("not enough clusters")
	return final_data_clusters




# Read in shapelet_id file and do min link clustering, stopping at 20 
print "ranking shapelets"
for cfnum in xrange(NUM_CROSSFOLDS): # Use more than one shapelet file
	# Nested dictionary: class -> file in class -> shapelets in file
	class_files = {}
	# Read in shapelet summary file and produce mapping above
	shapelet_summary = "{0}/cf{1}/shapelet_ids".format(shapelet_dir, cfnum)
	print "processing shapelets for cf:", cfnum
	for line in open(shapelet_summary):	
		# line: (id, source_path, start_position, length, inf_gain, sep_dist)
		line = line.strip().split(',')
		line[2] = int(line[2])
		line[3] = int(line[3])
		line[4] = float(line[4]) # important for sorting
		line[5] = float(line[5]) # important for sorting
		# only interested in the filename and class for now TODO fix this up
		shapelet_source = line[1].split('/')[-1] # the source filename
		class_type = shapelet_source.split('_')[0] # e.g. ESE_wide_100.data
		# Work out the nested dictionary keys
		if class_type not in class_files.keys():
			class_files[class_type] = {shapelet_source : [line] }
		else: # Now check the keys of the nested dictionary
			if shapelet_source not in class_files[class_type].keys():
				class_files[class_type][shapelet_source] = [line]
			else: # There exist dicts at both levels already
				class_files[class_type][shapelet_source].append(line)
	# Now, for each class, extract the best shapelets through clustering
	shapelets_info = {} # maps shapelet data to its information
	for c in class_files.keys():
		class_candidates = [] # top shapelets from each class
		# For each file, do an initial clustering to find candidates
		for filename in class_files[c].keys():
			print "processing:", filename
			source_path = SHAPELET_SOURCE_DIR + '/' + filename
			source_lc = lightcurve.file_to_lc(source_path) # load for splitting later
			file_time, file_flux = (tuple(source_lc.time), tuple(source_lc.flux))
			# Take the top FILE_INFGAIN_FRAC fraction of shapelets by entropy
			# LOWER ENTROPY IS BETTER, So don't reverse the sort
			class_files[c][filename].sort(key=itemgetter(4))
			num_to_use = int(len(class_files[c][filename]) * FILE_INFGAIN_FRAC)
			# Load all of the shapelets as time series to begin clustering
			shapelets_data = [] # Shapelets as lightcurve objects
			for shapelet_info in class_files[c][filename][:num_to_use]:
				start = shapelet_info[2] # 2 is start position
				end = shapelet_info[2] + shapelet_info[3] # 3 is length
				shapelet_as_ts = tuple([file_time[start:end], file_flux[start:end]])
				#print shapelet_as_ts
				shapelets_data.append(shapelet_as_ts)
				shapelets_info[shapelet_as_ts] = shapelet_info
			# Finally, time to cluster. Compute the distance matrix
			cluster_data = cluster_shapelets(shapelets_data, NUM_CLUSTERS_PER_FILE) # See method above
			# Get highest infgain member of each cluster
			file_sample = [sorted(cluster, key=lambda o: shapelets_info[o][4])[0] for cluster in cluster_data]
			class_candidates += file_sample
		final_clustering = cluster_shapelets(class_candidates, NUM_CLUSTERS_PER_CLASS) # Cluster these again
		final_cluster_data = []
		for cluster in final_clustering:
			final_cluster_data.append([shapelets_info[o] for o in cluster])
		# Take the final clusters and write out to the shapelet_feature directory
		for cnum, ts_list in enumerate(final_cluster_data):
			print "crossfold:", cnum
			candidate = sorted(ts_list, key=lambda o: float(o[4]))[0]
			source_filename = candidate[1].split('/')[-1]
			source = lightcurve.file_to_lc(SHAPELET_SOURCE_DIR + "/" +  source_filename)
			sh_class = source_filename.split('_')[0]
			sh_start = int(candidate[2])
			sh_end = int(candidate[3]) + sh_start
			# Write out to crossfold directory in shapelet feature directory
			out_dir = "{0}/cf{1}".format(SHAPELET_FEATURE_DIR, cfnum)
			if not os.path.isdir(out_dir):
				os.mkdir(out_dir)
			debug_dir = "{0}/cf{1}".format(SHAPELET_DEBUG_DIR, cfnum)
			if not os.path.isdir(debug_dir):
				os.mkdir(debug_dir)	
			out_file = open("{0}/{1}_shapelet_{2}.data".format(out_dir, c, cnum), 'w') # c is the class
			print "writing to file:", out_file
			for t, f in izip(source.time[sh_start:sh_end], source.flux[sh_start:sh_end]):
				out_file.write('{0}\t{1}\n'.format(t,f))
			out_file.close()
			plt.plot(source.time[:sh_start], source.flux[:sh_start], 'k', source.time[sh_end:], source.flux[sh_end:], 'k', source.time[sh_start:sh_end], source.flux[sh_start:sh_end], 'r')
			plt.xlabel('Time (days)')
			plt.ylabel('Flux (mJy, normalised)')
			plt.savefig("{0}/{1}".format(debug_dir,\
				'id{0}_{1}_shapelet{2}.pdf'.format(candidate[0], sh_class, cnum), format="pdf"))
			plt.close()
	#print sh_data_clusters
	#print "number of clusters: ", len(sh_ts_clusters)
	#for n, clust in enumerate(sh_data_clusters):
	#	print "cluster", n
	#	for obj in clust:
	#		print "\t",obj
