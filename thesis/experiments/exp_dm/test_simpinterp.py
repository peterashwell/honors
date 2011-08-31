from utils import simple_interpolate

lc_a = [range(10) + range(15, 20), range(15)]
print lc_a, len(lc_a[0]), len(lc_a[1])
lc_b = [range(10, 20), range(10, 20)]
print simple_interpolate(lc_a)
print simple_interpolate(lc_b)
