#!/usr/local/bin/python

import time
import math
import re
import blo_tree

sources = []
tree = None # blo tree used to store sources from last generation

FRAMES = 100
IDS = 0
TOLERANCE = 0.0012
FLUX_TOLERANCE = 0.001
tree_time = 0
other_time = 0
search_time = 0

error_file = 'matching_errors'
error_out = open(error_file, 'w')
# now we have something to work with, look at every subsequent frame, match as well as possible
for frameno in xrange(FRAMES):
	filename = 'data/skads1_t{}'.format(frameno)
	print "reading {}".format(filename)
	
	frame = open(filename)
	first = True
	for line in frame:
		if first:
			first = False
			continue # skip first line

		if line[0] == '#': continue #line = line[1:] # remove '#' indicating this as transient
		line = re.split(' +', line.strip())	
		real_id = int(line[0])
		ra = float(line[1])
		dec = float(line[2])
		flux = float(line[3])
	
		if frameno == 0: # 0th frame - just add to sources as a new source
			sources.append([(ra, dec, flux, real_id, IDS)])
			IDS += 1
		else: # otherwise, use tree constructed from last loop (below) to find sources in log time
			bounds = (ra - TOLERANCE, ra + TOLERANCE, dec - TOLERANCE, dec + TOLERANCE)
			MATCHMETHOD = 2 # closest distance
			result = None
			start = time.time()
			if MATCHMETHOD == 1:
				near = tree.find_in_range(bounds)
				sorted_near = sorted(near, key=lambda obj: math.sqrt((obj[0] - ra) ** 2 + (obj[1] - dec) ** 2))
				if len(sorted_near) != 0:
					if result[3] != real_id:
						error_out.write("picked {}, should have picked {}`\n".format(result, (ra, dec, flux, real_id)))
					result = sorted_near[0] # closest result euclidean distance
			elif MATCHMETHOD == 2: # closest flux
				near = tree.find_in_range(bounds)
				
				sorted_near = sorted(near, key=lambda obj: math.fabs(flux - obj[2])) # sort by flux
				sorted_near = filter(lambda obj: math.fabs(obj[2] - flux) < 0.5 * obj[2] or obj[2] == 0, sorted_near)
				if len(sorted_near) != 0:
					result = sorted_near[0]
					if result[3] != real_id:
						correction = tree.start_debug(real_id)
						#error_out.write(str(result[3]) + ' ' + str(real_id) + ' ' + str(result[3] == real_id))
						if correction is not None:
							error_out.write("picked {} to match {}, should have picked {}`\n".format(result, (ra, dec, flux, real_id), correction))
						else:
							error_out.write("picked {} to match {}, no correction found, but wrong (either wrongly filling in for transient or real value stolen)\n".format(result, (ra, dec, flux, real_id)))
			elif MATCHMETHOD == 3: # nearest, but cut off at certain flux tolerance
				near = tree.find_in_range(bounds)
				#sorted_near = filter(lambda obj: math.fabs(obj[2] - flux) < FLUX_TOLERANCE or obj[2] == 0, near)
				sorted_near = sorted(near, key=lambda obj: math.sqrt((obj[0] - ra) ** 2 + (obj[1] - dec) ** 2))
				if len(sorted_near) != 0:
					result = sorted_near[0]
			elif MATCHMETHOD == 4:
				near = tree.find_in_range(bounds)
				if len(near) != 0:
					dist_weight = 0.6
					sorted_on_flux = sorted(near, key=lambda obj: math.fabs(flux - obj[2]), reverse=True)
					sorted_on_dist = sorted(near, key=lambda obj: math.sqrt((obj[0] - ra) ** 2 + (obj[1] - dec) ** 2), reverse=True)
					best_score = sorted_on_flux.index(near[0]) + dist_weight * sorted_on_dist.index(near[0])
					best_res = near[0]
					for src in near[1:]:
						if sorted_on_flux.index(src) + dist_weight * sorted_on_dist.index(src) > best_score:
							best_res = src
							best_score = src
					result = best_res

			search_time += time.time() - start
			# if #there are matches nearby, pick the first one and mark it with the same id as from the prev. frame
			start = time.time()
			if result is None:
				sources.append([(ra, dec, 0.0, real_id, IDS)] * frameno)
				sources[IDS].append((ra, dec, flux, real_id, IDS))
				IDS += 1
			else:
				#if real_id != result[3]:
				#	error_out.write('{} {} {}\n'.format(frameno, real_id, result[3]))
				sources[result[-1]].append((ra, dec, flux, real_id, result[-1]))
				tree.remove(result)
			other_time += (time.time() - start)
			#print "DEBUGGING:"
			#tree.start_debug(154470912)
			#print "DONE"
	# for the sources that couldn't be matched, simply fill them out as "missing"
	start = time.time()
	for source in sources:
		if len(source) <= frameno:
			source.append((source[-1][:2] + tuple([0]) + source[-1][3:]))
	other_time += (time.time() - start)
	tree = blo_tree.BloTree()
	#for source in sources:
	#	if source[frameno][3] == 154470912:
	#		print "ID IN SOURCES"
	tree.insert_all([source[frameno] for source in sources])
	#print "ASSFACE"
	#3tree.start_debug(154470912)
	#print "COCKJISM"
	tree_time += time.time() - start
	frame.close()
error_out.close()

print "tree building: {}".format(tree_time)
print "tree searching: {}".format(search_time)
print "other: {}".format(other_time)

outfilename = 'skads1_ts'
transients = 'skads1_trans'
out = open(outfilename, 'w')
tout = open(transients, 'w')
for sourcenum in xrange(len(sources)):
	ids_for_source = []
	transient = False
	for framenum in xrange(len(sources[sourcenum])):
		if len(sources[sourcenum][framenum]) > 0:
			if sources[sourcenum][framenum][3] not in ids_for_source:
				ids_for_source.append(sources[sourcenum][framenum][3])
			if sources[sourcenum][framenum][2] == 0: # transient
				transient = True
			out.write(str(sources[sourcenum][framenum][2]))
		out.write(',')
	out.write(str(ids_for_source[0]))
	out.write('\n')
	if transient:
		tout.write(str(sources[sourcenum][-1][-2])) # write this real id as a transient
		tout.write('\n')
out.close()
tout.close()
	 
