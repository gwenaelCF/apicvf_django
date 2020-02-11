
path = '/media/sf_public/'
orig = 'apic_communes_2020.csv'
nc = 'communes_nc.csv'
dest= 'apic_all_communes.csv'

l_nc = open(path+nc,'r').readlines()[1::]
l_nc = [a.split(',')[0].replace(' ','')+';;;;;nc;'+'\n' for a in l_nc]

with open(path+dest,'w+') as f:
	with open(path+orig,'r') as org :
		for line in org:
			f.write(line)
	for line in l_nc:
		f.write(line)

open(path+dest,'r').readlines()