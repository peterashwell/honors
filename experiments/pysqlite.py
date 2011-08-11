import sqlite3
conn = sqlite3.connect('testdb.db')

FEATNAME_FNAME = 'exp_features/features.desc'

c = conn.cursor()
featname_file = open(FEATNAME_FNAME)
features = []
for line in featname_file:
	if line[0] != '#':
		line = line.strip().split('\t')
		featname = line[0]
		featamt = int(line[1])
		if featamt > 1:
			for featnum in xrange(featamt):
				features.append('{0}{1}'.format(featname, featnum))
		else:
			features.append(featname)
print features		
# vulnerable to injections apparently but who gives a fuck
query = '''create table featcache \
(key TEXT PRIMARY_KEY, {0})'''.format(\
','.join('{0} float'.format(f) for f in features))
print query
#c.execute(query)

#FEATCACHE_FNAME = 'exp_features/features.cache'
#featcache = open(FEATCACHE_FNAME)
#lastkey = None
#for line in featcache:
#	line = line.strip().split(',')
#	entry = [line[0].replace('.', ',')] + [float(f) for f in line[1:]]
#	lastkey = entry[0]
#	query = '''insert into featcache values {0}'''.format(tuple(entry))
#	print query 
#	c.execute(query)
#featcache.close()

#c.execute('''select * from featcache where key=lightcurves/powlaw_n1.5_a100_m0_s400/Nova_99.data''')
#print c.fetchall()
c.execute('''select * from featcache''')
print c.fetchone()
c.execute('''select * from featcache where key=?''', ('lightcurves/powlaw_n1-5_a100_m0_s400/ESE_66-data',))
print c.fetchone()

conn.commit()
conn.close()
