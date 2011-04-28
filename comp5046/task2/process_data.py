#!/usr/local/bin/python

import math
import sys
import re

# get raw data filename and split percentage
args = sys.argv[1:]
filename = args[0]
split_pct = float(args[1])

# options
_normalise = True
_fixquestions = True
_split = True

# scan file, find max and sum for each column, count for rows
max_for_col = []
sum_for_col = []

file_data = open(filename)
num_rows = 0 # count rows
first = True
for line in file_data:
	colnum = 0
	for colval in re.split(',', line.strip())[:-1]: # exclude class
		colval = colval.strip()
		if colval == "?":
			continue # do not contribute to max or average
		fcolval = float(colval)
		if first:
			max_for_col.append(fcolval)
			sum_for_col.append(fcolval)
		
		else:
			if fcolval > max_for_col[colnum]:
				max_for_col[colnum] = fcolval
			sum_for_col[colnum] += fcolval
		colnum += 1	
	first = False
	num_rows += 1
avg_for_col = []
print "finished scanning"
for colkey in xrange(len(sum_for_col)):
	if max_for_col[colkey] > 1e-5:
		avg_for_col.append(sum_for_col[colkey] * 1.0 / (num_rows * max_for_col[colkey]))
file_data.seek(0) # get ready for another scan

sf_needed = int(math.ceil(100.0 / split_pct)) # number of split files
sf_size = int(math.ceil(num_rows / sf_needed)) # number of lines in a split file

sf_root = filename.split('.')[0].strip() + "_split"
split_files = [] # array of split files
for sf_num in xrange(sf_needed):
	split_files.append(open(sf_root + str(sf_num) + ".data", 'w'))
curfile = 0 # which file we are currently writing to

for line in file_data:
	#print curfile
	skiprow = False
	row = re.split(',', line.strip())
	for colnum in xrange(len(row)):
		if colnum == len(row) - 1:
			continue # skip editing class value
		colval = row[colnum].strip()
		if colval == '?':
			if _fixquestions:
				row[colnum] = avg_for_col[colnum]
			else:
				skiprow = True
		else:
			if _normalise:
				if max_for_col[colnum] > 1e-5: # won't cause catastrophic division error
					row[colnum] = float(colval) / max_for_col[colnum]
	if skiprow:
		continue # do not add row, it has a '?'
	else: # write to files
		split_files[curfile].write(','.join([str(obj) for obj in row]) + '\n')
		curfile = (curfile + 1) % len(split_files)
for sf in split_files: # close up all the files
	sf.close()
