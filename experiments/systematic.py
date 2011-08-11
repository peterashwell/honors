import getopt
def systematic_name(options, plot_variable=None):
	parameter = None
	options = options.strip()
	print "LINE:", options
	# produce systematic name for experiment conditions
	noise = 0
	available_pct = 100
	missing = 0
	max_size = 400
	opts, args = getopt.getopt(options.split(' '), "dun:a:m:")
	print "OPTS:", opts, "ARGS", args
	exp_filename = ''
	for opt, arg in opts:
		if opt == '-u':
			exp_filename += 'norm'
		if opt == '-d':
			exp_filename += 'powlaw'
		if opt == '-n':
			if plot_variable == 'n':
				parameter = arg
			noise = arg
		if opt == '-a':
			available_pct = arg
			if plot_variable == 'a':
				parameter = arg
		if opt == '-m':
			missing = arg		
			if plot_variable == 'm':
				parameter = arg
	exp_filename += '_n' + str(noise)
	exp_filename += '_a' + str(available_pct)
	exp_filename += '_m' + str(missing)
	exp_filename += '_s' + str(max_size)
	return (exp_filename, parameter)

import sys
if __name__ == '__main__':
	print systematic_name(sys.argv[1])[0]
