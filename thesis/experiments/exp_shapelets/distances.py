import math
# return the minimum distance of a, against b (ie b moves)
def mindist(ts, shapelet):
	len_ts = len(ts.time)
	len_shapelet = len(shapelet.time)
	if len_ts < len_shapelet:
		return 99999 # okay as a hack, but TODO fix this jesus 
	best_distance = None
	for comp_start in xrange(0, len_ts - len_shapelet):
		cur_distance = 0
		compared_points = 0
		for comp_pos in xrange(0, len_shapelet):
			ts_position = comp_pos + comp_start
			if ts.flux[ts_position] == '-':
				continue # don't do anything here
			cur_distance += (ts.flux[ts_position] - shapelet.flux[comp_pos]) ** 2
			compared_points += 1
			if best_distance is not None:
				if cur_distance > best_distance:
					break # stop computing, already worse from here
		cur_distance /= (1.0 * compared_points)
		if best_distance is None:
			best_distance = cur_distance
		elif cur_distance < best_distance:
			best_distance = cur_distance
	return best_distance
def dtw():
	return 0
