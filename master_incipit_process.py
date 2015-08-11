import os,shutil,re
from make_ly_from_mxml import make_incipit_ly
from make_incipits import make_incipit_svg
from make_midi_analysis import make_midi_analysis
from make_mp3_from_midi import make_mp3_from_midi
from make_pngs import make_incipit_png

def rename_files(folder):
	global root
	for fl in filter(lambda x:not x.startswith('.'),os.listdir(os.path.join(root,folder))):
		if os.path.isdir(os.path.join(root,folder,fl)):
			data = filter(lambda x:not x.startswith('.'),os.listdir(os.path.join(root,folder,fl)))
			data.sort(key=lambda x: int(re.split('(\d+).',x)[1]))
			for i,f in enumerate(data):
				# if f.find('pdf') != -1:
				if not "_".join(f.split('.')[0].split('_')[:-1]) == folder:
					new_name = folder+'_'+str(i+1)+'.'+f.split('.')[-1]
					new_path = os.path.join(root,folder,fl,new_name)
					old_path = os.path.join(root,folder,fl,f)
					os.rename(old_path,new_path)
					print new_path

root = 'port_collection_assets/'

collections = filter(lambda x:not x.startswith('.'),os.listdir(root))

for item in collections:
	if item == 'goodman_vol_2':
		# make_incipit_ly(item)
		# make_incipit_png(item)
		# make_incipit_svg(item)
		# make_midi_analysis(item)
		# make_mp3_from_midi(item)
		rename_files(item)
	