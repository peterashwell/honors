import lightcurve
import features
import utils

LC_PATH = 'lightcurves/norm_n1.5_a100_m0_s400/'
lc = lightcurve.file_to_lc(LC_PATH + 'SNe_wide_25.data')
print "SNe"
print ['{0}'.format(obj) for obj in features.time_flux(lc)]
#print [round(obj, 3) for obj in features.time_flux(lc)]
print "ESE"
lc = lightcurve.file_to_lc(LC_PATH + 'ESE_wide_25.data')
print [round(obj, 3) for obj in features.time_flux(lc)]

print "IDV"
lc = lightcurve.file_to_lc(LC_PATH + 'IDV_wide_25.data')
print [round(obj, 3) for obj in features.time_flux(lc)]
print "Novae"
lc = lightcurve.file_to_lc(LC_PATH + 'Novae_wide_25.data')
print [round(obj, 3) for obj in features.time_flux(lc)]
