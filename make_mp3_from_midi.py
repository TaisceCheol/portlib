import os,subprocess,glob,re


def process(path):
	wav_path = os.path.join(outdir,path.split('/')[-1].replace('.mid','.wav'))
	mid_to_wav = ["fluidsynth","-F",wav_path,'/Users/ITMA/Soundfonts/GU.sf2',path]
	subprocess.call(mid_to_wav)
	wav_to_mp3_with_fade = ['sox',wav_path,'-C','96',wav_path.replace('.wav','.mp3'),'fade','0','25','5']
	subprocess.call(wav_to_mp3_with_fade)
	os.unlink(wav_path)
	return None

def make_mp3_from_midi(source):	
	global outdir
	path = "port_collection_assets/{0}/{0}_midi".format(source)
	outdir = "port_collection_assets/{0}/{0}_mp3".format(source)
	data = glob.glob(path+'/*.mid')
	data.sort(key=lambda x: int(re.split('(\d+).',x)[-2]))
	for p in data:
		process(p)	
	return None

if __name__ == '__main__':
	make_mp3_from_midi('bunting_vol_1')













