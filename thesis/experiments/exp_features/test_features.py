import features
import lightcurve
import sys
classtype = sys.argv[1]
num = sys.argv[2]
lc_path = 'lightcurves/norm_n1.5_a100_m0_s400/{0}_wide_{1}.data'.format(classtype, num)
hc = features.time_flux(lightcurve.file_to_lc(lc_path))[-22:] 
print hc[:12]
print hc[12:]
hc = features.flux_only(lightcurve.file_to_lc(lc_path))[-22:] 
print hc[:12]
print hc[12:]
