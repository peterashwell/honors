# Little wrapper for time series data being used
class LightCurve:
	def __init__(self, t=list(), f=list()):
		self.time = t[:]
		self.flux = f[:]

	# one way operation, removes datapoints with '-' denoting gaps
	def remove_gaps(self):
		new_time = []
		new_flux = []
		for index in range(len(self.time)):
			if self.flux[index] != '-':
				new_time.append(self.time[index])
				new_flux.append(self.flux[index])
		self.time = new_time
		self.flux = new_flux
	
	def copy(self):
		return LightCurve(self.time[:], self.flux[:])	
	
def file_to_lc(filename):
	print "converting file", filename, "to lc"
	time = []
	flux = []
	lc_file = open(filename)
	for line in	lc_file:
		line = line.strip().split('\t')
		time.append(float(line[0]))
		if line[1] == '-':
			flux.append('-')
		else:
			flux.append(float(line[1]))
	return LightCurve(time, flux)
