import os,subprocess,glob,re

def process(path):
	global outdir
	outpath = os.path.join(outdir,path.split('/')[-1].replace('.ly','.png'))
	cmd = ["lilypond",'--png','-dpreview','-o',outpath,path]
	errors = subprocess.check_output(cmd,stderr=subprocess.STDOUT)
	for ln in errors.split('\n'):
		if ln.find('warning') != -1:
			print ln
	os.remove(outpath+'.png')
	os.remove(outpath+'.preview.eps')
	outpath_preview = outpath + '.preview.png'
	os.rename(outpath_preview,outpath)
	return None

def make_incipit_png(source):	
	global outdir 
	path = "port_collection_assets/{0}/{0}_ly".format(source)
	outdir = "port_collection_assets/{0}/{0}_png".format(source)
	data = glob.glob(path+'/*.ly')
	data.sort(key=lambda x: int(re.split('(\d+).',x)[-2]))
	for p in data:
		print p
		process(p)
	return None

if __name__ == '__main__':
	make_incipit_png('bunting_vol_2')