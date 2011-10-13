import math
def minimum_distance(ts, shapelet):
	smallest = None
	# Shapelet structure is <TS, shape_start, length>
	sh_time = shapelet[0][0]
	sh_flux = shapelet[0][1]
	sh_start = shapelet[1]
	sh_len = shapelet[2]
	ts_flux = ts[1]
	# Iterate over all start points, keeping track of smallest
	for start_point in xrange(0, len(ts_flux) - sh_len + 1):
		distance = 0 # Distance as sum is produced
		# Iterate over shapelet
		for comp_pos in xrange(min(sh_len, len(ts_flux))):
			distance += math.fabs(ts_flux[comp_pos + start_point] - \
			  sh_flux[sh_start + comp_pos]) # Shapelet position in master ts 
			if smallest is None:
				pass # If no smallest found yet, can't skip
			elif distance > smallest:
				break # Cannot beat best so far, look at another comparison spot
		if smallest is None:
			smallest = distance
	return (1.0 * smallest) / sh_len

def binary_entropy(class_a, class_b):
	num_labels = class_a + class_b
	frac_a = (class_a * 1.0) / num_labels
	frac_b = (class_b * 1.0) / num_labels
	#print frac_a, frac_b
	if frac_a <= 0:
		log_a = 0
	else:
		log_a = math.log(frac_a)
	if frac_b <= 0:
		log_b = 0
	else:
		log_b = math.log(frac_b)
	return -1 * (frac_a * log_a + frac_b * log_b)

# Compute multi_class entropy for the label set
def entropy(label_collection, label_set):
	label_counts = {}
	for label in label_collection:
		if label in label_counts.keys():
			label_counts[label] += 1
		else:
			label_counts[label] = 1
	entropy_sum = 0
	for label in label_counts.keys():
		if label_counts[label] == 0:
			continue # entropy addition is 0
		frac = (label_counts[label] * 1.0) / len(label_collection)
		print frac, math.log(frac)
		entropy_sum += frac * math.log(frac)
	return -1 * entropy_sum

def entropy_sort(label_collection, label_set):
	entropy_sum = 0
	if len(label_collection) == 0 or (label_collection) == 1:
		return 0.0
	label_collection.sort()
	cur = label_collection[1]
	cur_count = 1
	num_labels = len(label_collection)
	for label in label_collection[1:]:
		if label != cur:
			frac = (cur_count * 1.0 / num_labels)
			entropy_sum += frac * math.log(frac)
	# Finish off last one
	frac = (cur_count * 1.0 / num_labels)
	entropy_sum += frac * math.log(frac)
	return -1 * entropy_sum

def entropy_search(label_collection, label_set):
	if len(label_collection) == 0 or (label_collection) == 1:
		return 0.0
	entropy_sum = 0
	num_labels = len(label_set)
	for label_type in label_set:
		count = 0
		for label in label_collection:
			if label_type == label:
				count += 1
		if count == 0:
			continue
		frac = (count * 1.0) / num_labels
		entropy_sum += frac * math.log(frac)
	return -1 * entropy_sum
		
def information_gain(eval_dataset, shapelet, ts_classes, shapelet_class, NUM_SHAPELET_CLASS, DATASET_ENTROPY, ts_filenames):
	split_line = []
	for ts in eval_dataset:
		md = minimum_distance(ts, shapelet)
		split_line.append((md, ts_classes[ts]))
		#print "distance:", md
		#if shapelet_class == ts_classes[ts]:
		#	split_line.append((md, shapelet_cla)) # Binary class information gain
		#else:
		#	split_line.append((md, 1))
	split_line.sort() # = sorted(split_line, key = lambda p: p[0])
	#print "test file", ts_classes[ts], ts_filenames[ts], shapelet_class#, split_line
	# Iterate over split line to find optimal split point using BINARY information gain
	ones_seen = 0
	zeros_seen = 0
	# When 1s seen exceeds 0s seen, break and compute information gain (best value there)
	total_ones = len(eval_dataset) - NUM_SHAPELET_CLASS
	for sp, p in enumerate(split_line):
		# TODO the lines below choose a threshold which is good only for
		# finding shapelets that distinguish ONLY the source class from others
		# A proper threshold needs to be chosen to define a good split to get
		# Shapelets that might give good entropy even when the split is clean
		# but involves more than one class (ie, all of two classes close to one
		# end)
		if p[1] == shapelet_class: # TODO is this right
			ones_seen += 1 # marks the right class being found on the right side
		else:
			zeros_seen += 1 # marks another class being closer
		if NUM_SHAPELET_CLASS - ones_seen < zeros_seen + 1: # Moving threshold right reduces information gain
			# backtrack as many zeros as possible
			while sp > 0:
				if split_line[sp][1] == shapelet_class:
					sp += 1 # include sp point in split line slice
					break # done backtracking
				sp -= 1
			break # No improvement can be made from this point
	#print "ones seen (out of 30):", ones_seen
	#print "zeros seen (out of 210):", zeros_seen
	D_left = [o[1] for o in split_line[:sp]]
	D_right = [o[1] for o in split_line[sp:]]
	#print D_left
	#print D_right
	frac1 = len(D_left) / (1.0 * len(eval_dataset))
	frac2 = len(D_right) / (1.0 * len(eval_dataset))
	return DATASET_ENTROPY - frac1 * entropy(D_left, ts_classes) \
	  - frac2 * entropy(D_right, ts_classes)
