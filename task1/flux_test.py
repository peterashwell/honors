import re

import math
import time

frames = 100
id_flux = {}

dict_time = 0
total_time = 0
start_total = time.time()
for frame_num in xrange(frames):
	frame_file = 'data/skads1_t{}'.format(frame_num)
	print "reading: {}".format(frame_file)
	data = open(frame_file)
	first = True
	for line in data:
		if first or line[0] == '#':
			first = False
			continue
		line = re.split(' +', line.strip())
		id = int(line[0])
		start = time.time()
		if id in id_flux.keys():
			id_flux[id].append(float(line[2]))
		else:
			id_flux[id] = [float(line[2])]
		dict_time += time.time() - start
	data.close()
total_time += time.time() - start_total

print "total: {} dict: {} file: {}".format(total_time, dict_time, total_time - dict_time)
max_fluxes = []
max_flux_pcts = []
for id_key in id_flux.keys():
	max_flux_change = math.fabs(id_flux[id][0] - id_flux[id][1])
	max_flux_change_pct = max_flux_change / (id_flux[id][0] * 0.01)
	last_flux = id_flux[id][1]
	for frame_num in xrange(1, frames):
		if math.fabs(id_flux[id][frame_num] - last_flux) > max_flux_change:
			max_flux_change = math.fabs(id_flux[id][frame_num] - last_flux)
			max_flux_change_pct = max_flux_change / (id_flux[id][0] * 0.01)
		last_flux = math.fabs(id_flux[id][frame_num])
	max_fluxes.append(max_flux_change)
	max_flux_pcts.append(max_flux_change_pct)
print "max change: {} as pct: {}".format(max(max_fluxes), max(max_flux_pcts))
