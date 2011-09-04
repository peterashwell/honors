import sys

fname = sys.argv[1]
gf = open(fname)
visited = set()
edges = {} # edge mappings
for line in gf:
	line = line.strip().split()
	start = line[0]
	visited.add(start)
	endpoints = filter(lambda obj: obj not in visited, line[1:])
	edges[start] = endpoints

# now write out .dot format
dotfname = '{0}.dot'.format(fname)
df = open(dotfname, 'w')
df.write('graph {\n')
for node in edges.keys():
	for endpoint in edges[node]:
		df.write('{0} -- {1};\n'.format(node, endpoint))
df.write('}')
df.close()
