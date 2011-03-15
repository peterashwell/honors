import re
import operator

# 1) read the data and pick out the annotated transients and how long they are off for
frames = 100
transients = {}
for frame_num in xrange(frames):
	frame_file = 'data/skads1_t{}'.format(frame_num)
	frame_data = open(frame_file)
	for line in frame_data:
		if line[0] == '#':
			id = re.split(' +', line[1:].strip())[0]
			if id != "id":
				if int(id) in transients.keys():
					transients[int(id)] += 1
				else:
					transients[int(id)] = 1
	frame_data.close()

# 2) now organise the transients by how long they are transient for
transient_amts = {}
for pair in transients.items():
	if pair[1] not in transient_amts.keys():
		transient_amts[pair[1]] = [pair[0]]
	else:
		transient_amts[pair[1]].append(pair[0])

# 3) write out data to file by time_transient, id, id, id ...
output_file = 'true_transients'
output = open(output_file, 'w')
output.write(str(len(transients.keys())) + '\n')
for pair in sorted(transient_amts.items(), key=operator.itemgetter(0)):
	str_transients = [str(obj) for obj in pair[1]] # need this as list of strings
	output.write(str(pair[0]) + ',' + str(len(str_transients)) + ':' + ','.join(str_transients))
	output.write('\n')
output.close()
