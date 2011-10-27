import math
# return the minimum distance of a, against b (ie b moves)
def mindist(ts_flux, shapelet_flux, OFFSET_PCT=0):
	len_ts = len(ts_flux)
	len_shapelet = len(shapelet_flux)
	# If the time series is shorter than the shapelet, compute in reverse
	if len_ts < len_shapelet:
		swap_call =  mindist(shapelet_flux, ts_flux, OFFSET_PCT)
		return (swap_call[0], -1 * swap_call[1]) # Position of time series giving min dist is negative!
	best_distance = None # the best distance found so far	
	
	# Check if there is any missing data. If there is, do not use early abandon
	early_abandon = True
	if '-' in ts_flux or '-' in shapelet_flux:
		early_abandon = False
	offset = int(OFFSET_PCT * len_shapelet) # works with overlapping subsequences # TODO move down
	if offset != 0:
		early_abandon = False
	# Now we've got through the distortions, compute minimum distance for contiguous subsequences
	# If the data is gappy, we store the best average of compared points and use a weaker early abandon condition
	for comp_start in xrange(0, len_ts - len_shapelet + 1):
		compared_points = 0
		cur_distance = 0
		for comp_pos in xrange(0, len_shapelet):
			ts_position = comp_pos + comp_start
			if not early_abandon:
				if ts_flux[ts_position] == '-' or shapelet_flux[comp_pos] == '-':
					continue # skip missing data
				if ts_position < 0 or ts_position >= len_ts:
					continue
			cur_distance += (ts_flux[ts_position] - shapelet_flux[comp_pos]) ** 2 # the actual distance
			compared_points += 1
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

	# Now check that there wasn't a better distance on the boundaries
	assert best_distance is not None # This should no langer happen
	best_distance /= (len_shapelet) # normalise for shapelet length
	return best_distance, best_position 

def dtw():
	return 0
