import os,subprocess,glob,re
from music21 import converter,stream,note,midi

def getHighestPitchInChord(pitches):
	return sorted(pitches,key=lambda x:x.ps)[-1]

def reduce_part(music,part_stream):
	ss = stream.Stream()
	# remove all grace notes as they really disturb analysis
	for item in music.flat:
		if not item.isGrace:
			ss.append(item)
	tree = ss.chordify()
	for chordx in tree.flat.getElementsByClass('Chord'):
		p = getHighestPitchInChord(chordx.pitches)
		# only allow notes greater than F below middle C
		if p.ps > 53:
			x = note.Note(p,quarterLength=chordx.duration.quarterLength)			
			part_stream.append(x)


def process(path):
	try:
		music = converter.parse(path)
		part_stream = stream.Stream()
		part_stream.metadata = music.metadata
		reduce_part(music,part_stream)
		mf = midi.translate.streamToMidiFile(part_stream)
		mf.open(path.replace('_xml','_midi_analysis').replace('.xml','.mid'),'wb')
		mf.write()
		mf.close()
	except:
		print 'Unable to read file'
	return None

def make_midi_analysis(source):	
	global outdir 
	path = "port_collection_assets/{0}/{0}_xml".format(source)
	outdir = "port_collection_assets/{0}/{0}_midi_analysis".format(source)
	data = glob.glob(path+'/*.xml')
	data.sort(key=lambda x: int(re.split('(\d+).',x)[-2]))
	for p in data:
		print p
		process(p)
	return None

if __name__ == '__main__':
	make_midi_analysis('goodman_vol_2')













