# -*- coding: UTF-8 -*-
import os,subprocess,json,glob,re,unicodedata,string
from collections import OrderedDict
from music21 import *
# from portlib.generate_index_codes import *
def get_first_two_measures(data):
	mcount = 0
	s = stream.Stream()
	for m in data.parts[0].getElementsByClass('Measure'):
		# ignore anacrusis
		if m.barDurationProportion() >= 1:
			for i,n in enumerate(m.flat.notesAndRests):
				if not n.isGrace:
					s.append(n)
			mcount +=1
		if mcount == 2:break
	isSong = False
	if len(s.notes) == 0:
		isSong = True 
	return s,isSong

def make_serial_code(data,keySig,timeSig):
	notes = []
	final = check_key_v_last_note(data,keySig,timeSig)
	solfege_map = {'do':1,'re':2,'mi':3,'fa':4,'sol':5,'la':6,'ti':7,'r':""}
	notes,isSong = get_first_two_measures(data)
	if isSong:
		notes = data.parts[0].getElementsByClass('Measure')[0:2].flat.notes
	out = []
	for n in notes:
		if n.isChord:
			p = solfege_map[final.solfeg(n.pitches[-1],direction='descending',chromatic=False)]
		elif n.isRest:
			p = solfege_map["r"]
		else:
			p = solfege_map[final.solfeg(n.pitch,direction='descending',chromatic=False)]
		out.append(str(p))
	return "".join(out)

def get_accent_values(timeSig):
	if timeSig == '6/8':
		sliceAmt = 1.5
		sliceIter = 4
	elif timeSig == '9/8':
		sliceAmt = 1.5
		sliceIter = 6
	elif timeSig == '3/8':
		sliceAmt = 0.5
		sliceIter = 6
	elif timeSig == '12/8' or timeSig == '2/4':
		sliceAmt = 0.5
		sliceIter = 8
	elif timeSig == '3/4':
		sliceAmt = 1
		sliceIter = 6
	elif timeSig == '4/4' or timeSig == '2/2':
		sliceAmt = 1
		sliceIter = 8 
	elif timeSig == '6/4' or timeSig == '3/2':
		sliceAmt = 2
		sliceIter = 6
	return sliceAmt,sliceIter

def check_key_v_last_note(data,keySig,timeSig):
	lastMeasureIndex = -1
	last = data.parts[0].getElementsByClass('Measure')[lastMeasureIndex]
	while len(last.notes) == 0:
		lastMeasureIndex -= 1
		last = data.parts[0].getElementsByClass('Measure')[lastMeasureIndex]
	s = stream.Stream()
	for item in last.notes:
		s.append(item)
	sliceAmt,sliceIter = get_accent_values(timeSig)
	final = s.getElementAtOrBefore(sliceIter*sliceAmt)
	if final.isChord:
		final = final.pitches[-1].pitchClass
	else:
		final = final.pitchClass
	relMajor = keySig.getRelativeMajor()
	relMinor = keySig.getRelativeMinor()
	if final == keySig.tonic.pitchClass:
		return keySig 
	elif final == relMajor.tonic.pitchClass:
		return relMajor 
	elif final == relMinor.tonic.pitchClass:
		return relMinor 
	else:
		return keySig

def make_breathnach_code(data,keySig,timeSig):
	code = []
	final = check_key_v_last_note(data,keySig,timeSig)
	solfege_map = {'do':1,'re':2,'mi':3,'fa':4,'sol':5,'la':6,'ti':7}
	ts = data.parts[0].flat.getElementsByClass('TimeSignature')[0]
	sliceAmt,sliceIter = get_accent_values(timeSig)

	print data.metadata.title,keySig,final,timeSig

	analStream,isSong = get_first_two_measures(data)
	if isSong != True:
		lastP = None
		for i in range(sliceIter):
			n = analStream.getElementAtOrBefore(i*sliceAmt)
			if n.isChord:
				p = n.pitches[-1]
			elif not n.isRest:
				p = n.pitch
			else:
				# if element is rest get element after? what would bb do
				n = analStream.getElementAfterElement(n)
				if n == None:
					p = lastP
				else:
					if n.isChord:
						p = n.pitches[-1]
					elif not n.isRest:
						p = n.pitch
			lastP = p
			code.append(str(solfege_map[final.solfeg(p,chromatic=False)]))
			if (i+1) == sliceIter/2.0:
				code.append(' • ')
	else:
		# bb code for songs? - take first and last notes of first four measures?
		measures = data.parts[0].getElementsByClass('Measure')[0:4]
		for i,m in enumerate(measures):
			notes = [m.notes[0],m.notes[-1]]
			for n in notes:
				if n.isChord:
					p = n.pitches[-1]
				elif not n.isRest:
					p = n.pitch
				else:
					# if element is rest get element after? what would bb do
					n = analStream.getElementAfterElement(n)
					if n == None:
						p = lastP
					else:
						if n.isChord:
							p = n.pitches[-1]
						elif not n.isRest:
							p = n.pitch
				lastP = p
				code.append(str(solfege_map[final.solfeg(p,chromatic=False)]))		
			if i == 1:
				code.append(' • ')		

	display_code = "".join(code)
	code = "".join(code).replace(' • ','')
	print display_code,code
	return code,display_code

def sort_names(lst):
	return sorted(lst,key=lambda x: int(x.split('.')[0].split('_')[-1]))

def iterate_collection_and_make_entries(cid,parent_title):
	global root,sim_data,soundslice_data,counter,completed_tunes,update
	collection_dir_path = root + cid
	xml_data = sort_names(filter(lambda x:x.endswith('.xml'),os.listdir(collection_dir_path+"/{0}_xml/".format(cid))))
	for i,tune_xml in enumerate(xml_data[74:]):
		data = converter.parse(collection_dir_path+"/{0}_xml/{1}".format(cid,tune_xml))
		data.metadata.title = data.metadata.title.replace("\I\\","").replace("\\i\\","")
		if len(data.parts[0].flat.notes) != 0:
			print i
			keySig = analysis.discrete.analyzeStream(data, 'key')
			timeSig = str(data.parts[0].getElementsByClass('Measure')[0].timeSignature.ratioString)
			fe = features.native.MostCommonNoteQuarterLength(data)
			av_note_dur = duration.Duration(fe.extract().vector[0]).type		
			breathnachCode,breathnachCodeDisplay = make_breathnach_code(data,keySig,timeSig)				
			make_serial_code(data,keySig,timeSig)
		# # quit()
root = '/users/itma/documents/port_music_files/port_collection_assets/'

with open('/users/itma/documents/port_music_files/collection_metadata_sorted.json','r') as f:
	collections_metadata = json.load(f)

collections = [x for x  in sorted(collections_metadata,key=lambda x:x['itma_pub_order'])]

flag = False

for item in collections:
	if item['itma_collection_id'] != "bunting_vol_3" and item['itma_collection_id'] == 'freeman':
		iterate_collection_and_make_entries(item['itma_collection_id'],item['short_title'])
		# quit()
