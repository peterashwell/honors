from distortions import *
from lightcurve import LightCurve
testfile = "raw_lightcurves/IDV_59.data"
testdata = open(testfile)
time = []
flux = []
for line in testdata:
	line = line.split('\t')
	time.append(float(line[0]))
	flux.append(float(line[1]))
lc = LightCurve(time, flux)
all_distortions(lc, 0, 100, 50, False)
