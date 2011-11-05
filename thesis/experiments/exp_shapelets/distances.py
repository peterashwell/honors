import numpy
import math
# return the minimum distance of a, against b (ie b moves)

def basic_mindist(ts_flux, shapelet_flux):
	len_ts = len(ts_flux)
	len_shapelet = len(shapelet_flux)
	best_distance = None
	for comp_start in xrange(0, len_ts - len_shapelet + 1):
		cur_distance = 0
		for comp_pos in xrange(0, len_shapelet):
			ts_position = comp_pos + comp_start
			cur_distance += (ts_flux[ts_position] - shapelet_flux[comp_pos]) ** 2
			if best_distance is not None:
				if cur_distance > best_distance:
					break
		if best_distance is None:
			best_distance = cur_distance
		elif cur_distance < best_distance:
			cur_distance = best_distance
	return math.sqrt(best_distance) / len(shapelet_flux)

def gappy_mindist(ts_flux, shapelet_flux, OFFSET_PCT=0):
	THRESHOLD = 0.9
	len_ts = len(ts_flux)
	len_shapelet = len(shapelet_flux)
	# If the time series is shorter than the shapelet, compute in reverse
	if len_ts < len_shapelet:
		swap_call =  mindist(shapelet_flux, ts_flux, OFFSET_PCT)
		return (swap_call[0], -1 * swap_call[1]) # Position of time series giving min dist is negative!
	best_distance = None # the best distance found so far	
	best_matched_positions = None
	best_sh_region = None
	# Check if there is any missing data. If there is, do not use early abandon
	early_abandon = True
	if '-' in ts_flux or '-' in shapelet_flux:
		early_abandon = False
	offset = int(OFFSET_PCT * len_shapelet) # works with overlapping subsequences # TODO move down
	if offset != 0:
		early_abandon = False
	#print "early abandon:", early_abandon
	# Now we've got through the distortions, compute minimum distance for contiguous subsequences
	# If the data is gappy, we store the best average of compared points and use a weaker early abandon condition
	shapelet_mean = numpy.mean(shapelet_flux)
	shapelet_deviation = numpy.sum([math.fabs(shapelet_mean - f) for f in shapelet_flux])
	for comp_start in xrange(0, len_ts - len_shapelet + 1):
		compared_points = 0
		cur_distance = 0
		matched_ts_region = []
		matched_sh_region = []
		matched_positions = []
		match_deviation = 0
		for comp_pos in xrange(0, len_shapelet):
			ts_position = comp_pos + comp_start
			if not early_abandon:
				if ts_flux[ts_position] == '-' or shapelet_flux[comp_pos] == '-':
					print "skipping"
					continue # skip missing data
				if ts_position < 0 or ts_position >= len_ts:
					continue
			match_deviation += math.fabs(shapelet_mean - shapelet_flux[comp_pos])
			cur_distance += (ts_flux[ts_position] - shapelet_flux[comp_pos]) ** 2 # the actual distance
			compared_points += 1
			matched_positions.append(comp_pos)
			if early_abandon: # Check early abandon condition
				if best_distance is not None: # Early abandon
					if cur_distance > best_distance:
						break # Cannot get better from here
			else: # Check weaker but still useful early abandon
				if best_distance is not None:
					if cur_distance / len_shapelet > best_distance: # Weaker early abandon, average safe
						break
		print "md:", match_deviation, "sd:", shapelet_deviation
		print "ratio:", match_deviation /shapelet_deviation
		print matched_positions
		print shapelet_deviation
		print match_deviation
		if match_deviation / shapelet_deviation < THRESHOLD:
			continue # skip this match
		update = False
		if compared_points <= 5:
			cur_distance = 1e10 # No idea what it is
		elif not early_abandon: # Use weaker version
			cur_distance /= compared_points # use only the number of points we've seen
		# Now our distance is adjusted for non-early abandon properly
		# Check to see if it beats the best so far
		if best_distance is None:
			update = True
		elif cur_distance < best_distance: # if gappy, average, otherwise, full distance sum
			update = True
		if update:
			best_distance = cur_distance
			best_position = comp_start
			best_matched_positions = matched_positions
			best_sh_region = matched_sh_region
	# Now check that there wasn't a better distance on the boundaries
	if best_distance is None:
		return (100, 0)
	
	print "best matched positions", best_matched_positions
	for p in best_matched_positions:
		print ts_flux[p]
	assert best_distance is not None # This should no langer happen
	best_distance = math.sqrt(best_distance) / (len_shapelet) # normalise for shapelet length
	return best_distance, best_position, best_matched_positions, best_sh_region




def mindist(ts_flux, shapelet_flux, OFFSET_PCT=0):
	len_ts = len(ts_flux)
	len_shapelet = len(shapelet_flux)
	# If the time series is shorter than the shapelet, compute in reverse
	if len_ts < len_shapelet:
		swap_call =  mindist(shapelet_flux, ts_flux, OFFSET_PCT)
		return (swap_call[0], -1 * swap_call[1]) # Position of time series giving min dist is negative!
	best_distance = None # the best distance found so far	
	best_matched_positions = None
	best_sh_region = None
	# Check if there is any missing data. If there is, do not use early abandon
	early_abandon = True
	if '-' in ts_flux or '-' in shapelet_flux:
		early_abandon = False
	offset = int(OFFSET_PCT * len_shapelet) # works with overlapping subsequences # TODO move down
	if offset != 0:
		early_abandon = False
	#print "early abandon:", early_abandon
	# Now we've got through the distortions, compute minimum distance for contiguous subsequences
	# If the data is gappy, we store the best average of compared points and use a weaker early abandon condition
	for comp_start in xrange(0, len_ts - len_shapelet + 1):
		compared_points = 0
		cur_distance = 0
		matched_ts_region = []
		matched_sh_region = []
		matched_positions = []
		for comp_pos in xrange(0, len_shapelet):
			ts_position = comp_pos + comp_start
			matched_ts_region.append(ts_flux[ts_position])
			matched_sh_region.append(shapelet_flux[comp_pos])
			if not early_abandon:
				if ts_flux[ts_position] == '-' or shapelet_flux[comp_pos] == '-':
					continue # skip missing data
				if ts_position < 0 or ts_position >= len_ts:
					continue
			cur_distance += (ts_flux[ts_position] - shapelet_flux[comp_pos]) ** 2 # the actual distance
			compared_points += 1
			matched_positions.append(comp_pos)
			if early_abandon: # Check early abandon condition
				if best_distance is not None: # Early abandon
					if cur_distance > best_distance:
						break # Cannot get better from here
			else: # Check weaker but still useful early abandon
				if best_distance is not None:
					if cur_distance / len_shapelet > best_distance: # Weaker early abandon, average safe
						break
		update = False
		if compared_points <= 5:
			cur_distance = 1e10 # No idea what it is
		elif not early_abandon: # Use weaker version
			cur_distance /= compared_points # use only the number of points we've seen
		# Now our distance is adjusted for non-early abandon properly
		# Check to see if it beats the best so far
		if best_distance is None:
			update = True
		elif cur_distance < best_distance: # if gappy, average, otherwise, full distance sum
			update = True
		if update:
			best_distance = cur_distance
			best_position = comp_start
			best_matched_positions = matched_positions
			best_sh_region = matched_sh_region
	# Now check that there wasn't a better distance on the boundaries
	assert best_distance is not None # This should no langer happen
	best_distance = math.sqrt(best_distance) / (len_shapelet) # normalise for shapelet length
	return best_distance, best_position, best_matched_positions, best_sh_region

def dtw():
	return 0
