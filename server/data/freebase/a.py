f = open('meta.dat', 'r')
nf = open('_meta.dat', 'w')
for line in f:
    line = line.split('\t')
    a = []
    if line[0] == 'l':
    	a.append(line[0])
    	a.append(line[1])
    	a.append(line[3])
    	a.append(line[4])
    	a.append(line[5])
    nf.write('\t'.join(a))
