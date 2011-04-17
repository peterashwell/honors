#!/usr/local/bin/python
import math
file = open("ad.data")
file_data = file.readlines()
filtered_data = []
for line in file_data:
	if '?' not in line:
		filtered_data.append(','.join(line.split(',')[3:])) # filter out first 3 components
split_10 = int(math.ceil(len(filtered_data) / 10.0))
for line_mul in xrange(10):
	out_file = "ad_" + str(line_mul) + ".data"
	start_line = line_mul * split_10
	end_line = (line_mul + 1) * split_10
	if end_line > len(filtered_data) + 1:
		end_line = len(filtered_data) + 1
	out_writer = open(out_file, 'w')
	print start_line, end_line
	out_writer.write(''.join(filtered_data[start_line:end_line]))
	out_writer.close()

