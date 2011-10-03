import features
import lightcurve
import sys
classtype = sys.argv[1]
num = sys.argv[2]
lc_path = 'lightcurves/norm_n0.0_a100_m0_s400/{0}_wide_{1}.data'.format(classtype, num)
hc = features.time_flux(lightcurve.file_to_lc(lc_path))[-11:] 
print hc
