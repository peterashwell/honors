# open the time series file and read row by row
frames = 100

# 1) Get the data holding correct transients from the correct_transients file
transients_file = 'true_transients' 
transients_data = open(transients_file)
correct_transients = set()
first = True
for line in transients_data:
	if first:
		first = False
		continue
	ids = [int(obj) for obj in line.strip().split(':')[1].split(',')]
	for id in ids:
		correct_transients.add(id)

# 2) Find our transients by simply looking for zeros in flux
found_transients = set()
ts_file = 'skads1_ts'
ts_data = open(ts_file)
transient_file = 'found_transients'
transient_out = open(transient_file,'w')
over_reported = set()
for line in ts_data:
	line = line.split(',')
	for frame_no in xrange(frames):
		#print line
		if float(line[frame_no]) == 0: # transient
			# to do this line split is no good (splits screw up the list at the end)
			if int(line[-1]) in found_transients:
				over_reported.add(int(line[-1]))
			else:
				found_transients.add(int(line[-1]))

# 3) use set difference to find the incorrectly, over reported and missed transients
missed_transients = correct_transients - found_transients
incorrect_transients = found_transients - correct_transients
correct = (correct_transients & found_transients)
miss_file = 'results/missed'
incorrect_file = 'results/incorrect'
overreport_file = 'results/overreported'
correct_file = 'results/correct'
analysis_out = open(miss_file, 'w')
for t in missed_transients:
	analysis_out.write(str(t) + '\n')
analysis_out.close()
analysis_out = open(incorrect_file, 'w')
for t in incorrect_transients:
	analysis_out.write(str(t) + '\n')
analysis_out.close()
analysis_out = open(overreport_file, 'w')
for t in over_reported:
	analysis_out.write(str(t) + '\n')
analysis_out.close()
analysis_out = open(correct_file, 'w')
for t in correct:
	analysis_out.write(str(t) + '\n')
analysis_out.close()
