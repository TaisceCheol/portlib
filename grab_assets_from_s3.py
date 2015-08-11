import os,subprocess

out = 'port_collection_assets/'

col = 'curry_petrie_1882'

file_root = 'https://s3-eu-west-1.amazonaws.com/itma.dl.scores/curry_in_petrie_1882_%02d'

n = 1

for ext in ['pdf','sib']:
	outpath = os.path.join(out,col,col+"_%s"%ext)
	print outpath 
	for i in range(n):
		path = file_root % (i+1) + '.{0}'.format(ext)
		outfile = os.path.join(outpath,path.split('/')[-1])
		subprocess.call(['wget',path,'-O',outfile])
