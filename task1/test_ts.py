import math
import re

frames = 100
id = 154470912
flux = []
dec = []
ra = [] 
for frame_num in xrange(frames):
	frame_file = 'data/skads1_t{}'.format(frame_num)
	data = open(frame_file)
	first = True
	for line in data:
		if first or line[0] == '#':
			first = False
			continue
		line = re.split(' +', line.strip())
		if int(line[0]) == id:
			flux.append(float(line[3]))
			dec.append(float(line[1]))
			ra.append(float(line[2]))

avg_flux = sum(flux) / len(flux)
last = flux[0]
change_flux = []
change_flux_pct = []
for f in flux[1:]:
	change_flux.append(math.fabs(last - f))
	change_flux_pct.append(math.fabs((last - f) / (last * 0.01)))
	last = f
avg_dec = sum(dec) / len(dec)
change_dec = []
change_dec_pct = []
last = dec[0]
for d in dec[1:]:
	change_dec.append(math.fabs(last - d))
	change_dec_pct.append(math.fabs((last - d) / (last * 0.01)))
	last = d
avg_ra = sum(ra) / len(ra)
change_ra = []
last = ra[0]
for r in ra[1:]:
	change_ra.append(math.fabs(last - r))
	last = r
print "flux - avg: {} max change: {} pct: {}".format(avg_flux, max(change_flux), max(change_flux_pct))
print "dec - avg: {} max change: {} avg_dev_pct: {} pct_from_last: {}".format(avg_dec, max(change_dec), max(change_dec) / (avg_dec * 0.01), max(change_dec_pct))
print "ra - avg: {} max change: {} avg_dev_pct: {}".format(avg_ra, max(change_ra), max(change_ra) / (avg_ra * 0.01))
