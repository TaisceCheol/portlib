# -*- coding: UTF-8 -*-
import os,subprocess,json,glob,re,unicodedata,string
from collections import OrderedDict
from music21 import *
from numpy import diff
from random import *
from itertools import tee,izip

def make_abc_code(data,timeSig):
	mcount = 0	
	lastDur = False;
	code = ""
	mlimit = 2
	for m in data.parts[0].getElementsByClass('Measure'):
		if m.barDurationProportion() >= 1:
			for nx in m.flat.notes:
				if not nx.isGrace:
					try:
						x = note.Note(nx.pitches[-1],quarterLength=nx.duration.quarterLength)		
						octave = x.octave
						if x.accidental != None:
							alt = x.accidental.name[0]
							if alt == 'n':
								alt = ''
							elif alt == 's':
								alt = '^'
							elif alt == 'f':
								alt = '_'
						else:
							alt = ''
						note_name = x.pitch.name[0]
						dur = duration.convertTypeToNumber(x.duration.type)	
						note_str = alt+note_name 
						if octave == 4:
							note_str = note_str.upper()
						elif octave == 5:
							note_str = note_str.lower()
						elif octave > 5:
							note_str = note_str.lower() + "".join(["'" for x in range(octave - 4)])
						elif octave < 4:
							note_str = note_str.upper() + "".join(["," for x in range(4 - octave)])
						if dur != lastDur:
							note_str += str(dur)
						lastDur = dur 
						code += note_str + ' '
					except:
						print 'something awry with this item',data.metadata.title,nx
			mcount +=1
			if mcount == mlimit:break
			code += '  |  '
	return code

def make_ly_code(data):
	out = ""
	tupletOn = False
	try:
		for m in data.parts[0].getElementsByClass('Measure'):
			if m.barDurationProportion() >= 1:
				notes = []
				for nx in m.flat.notes:
					if not nx.isGrace:
						x = note.Note(nx.pitches[-1],quarterLength=nx.duration.quarterLength)		
						octave = lily.translate.LilypondConverter().octaveCharactersFromPitch(x.pitch)
						if x.accidental != None:
							alt = x.accidental.name[0]
							if alt == 'n':
								alt = ''
						else:
							alt = ''
						note_name = x.pitch.name[0].lower()
						dur = duration.convertTypeToNumber(x.duration.type)	
						if len(x.duration.tuplets) > 0:
							tuplet = x.duration.tuplets[0]
							n = tuplet.numberNotesActual
							d = tuplet.numberNotesNormal
							tupletString = '\tuplet %d/%d { ' % (n,d)
							if tupletOn == False:
								out += tupletString
								tupletOn = True
						else:
							if tupletOn == True:
								out += " } "
								tupletOn = False
						out += "{0}{1}{3} ".format(note_name,alt,octave,dur)
			if tupletOn == True:
				out += "} "
				tupletOn = False			
			# out += "| "
		return out
	except:
		return ""

def make_parsons_code(data):
	try:
		pc_code = []
		notes = []
		for m in data.parts[0].getElementsByClass('Measure'):
			# ignore anacrusis
			if m.barDurationProportion() >= 1:
				for i,n in enumerate(m.flat.notes):
					if not n.isGrace:
						notes.append(n.midi)
		notes = list(diff([x for x in notes]))
		for i,x in enumerate(notes):
			if x !=0:
				notes[i] /= abs(x)
		for i,n in enumerate(notes):
			if n == 1:
				pc_code.append('u')
			elif n == -1:
				pc_code.append('d')
			else:
				pc_code.append('r')
		return "".join(pc_code)
	except:
		return ""

def not_rest_anacrusis(measure,number):
	if number == 0:
		if len(measure.flat.getElementsByClass('Rest')) > 0:
			x = stream.Measure(measure.flat.getElementsByClass(['Note','Chord'])).quantize([4], processOffsets=True, processDurations=True)
			# if notes are less than 0.25 of bar then it is a rest anacrusis
			if len(measure.flat.getElementsByClass(['Note','Chord'])) == 0:
				return False
			elif x.bestTimeSignature().barDuration.quarterLength < (measure.flat.barDuration.quarterLength * 0.35):
				return False
	return True

def get_all_measures(data):
	mcount = 0
	s = stream.Stream()
	remove_dodgy_spacer_rests(data.parts)
	if len(data.parts[-1].flat.notes) != 0:
		parts = sorted(data.parts,key=lambda x:float(x.flat.notes[0].offset))
		parts = sorted(parts,key=lambda y: max([x.midi for x in y.flat.notes[0].pitches]),reverse=True)
	else:
		parts = data.parts
	for mn,m in enumerate(parts[0].getElementsByClass('Measure')):
		# ignore anacrusis
		if float(str(m.barDurationProportion())) >= 1 and not_rest_anacrusis(m,mn):
			if len(m.voices) == 0:
				for i,n in enumerate(m.flat.notesAndRests):
					if not n.isGrace:
						s.append(n)
			else:
				for i,n in enumerate(m.voices[0].flat.notesAndRests):
					if not n.isGrace:
						s.append(n)
	isSong = False
	if len(s.notes) == 0:
		isSong = True 
	return s,isSong

def get_all_as_measures(data):
	mcount = 0
	measures = []
	remove_dodgy_spacer_rests(data.parts)
	if len(data.parts[-1].flat.notes) != 0:
		parts = sorted(data.parts,key=lambda x:float(x.flat.notes[0].offset))
		parts = sorted(parts,key=lambda y: max([x.midi for x in y.flat.notes[0].pitches]),reverse=True)
	else:
		parts = data.parts
	for mn,m in enumerate(parts[0].getElementsByClass('Measure')):
		measures.append(m)
	return measures

def get_first_two_measures(data):
	mcount = 0
	s = stream.Stream()
	remove_dodgy_spacer_rests(data.parts)
	if len(data.parts[-1].flat.notes) != 0:
		parts = sorted(data.parts,key=lambda x:float(x.flat.notes[0].offset))
		parts = sorted(parts,key=lambda y: max([x.midi for x in y.flat.notes[0].pitches]),reverse=True)
	else:
		parts = data.parts
	for mn,m in enumerate(parts[0].getElementsByClass('Measure')):
		# ignore anacrusis
		if float(str(m.barDurationProportion())) >= 1 and not_rest_anacrusis(m,mn):
			if len(m.voices) == 0:
				for i,n in enumerate(m.flat.notesAndRests):
					if not n.isGrace:
						s.append(n)
			else:
				for i,n in enumerate(m.voices[0].flat.notesAndRests):
					if not n.isGrace:
						s.append(n)
			mcount +=1
		if mcount == 2:break

	isSong = False
	if len(s.notes) == 0:
		isSong = True 
	return s,isSong

def remove_dodgy_spacer_rests(partlist):
	for part in partlist:
		timeSig =  part.flat.getElementsByClass('TimeSignature')[0]
		for m in part.getElementsByClass('Measure'):
			n = stream.Stream()
			r = stream.Stream()
			for note in m.flat.notesAndRests:
				if note.isNote:
					n.append(note)		
				else:
					r.append(note)
			if n.notes.duration == timeSig.barDuration:
				if len(r) > 0:
					if r[0].offset == 0 and len(r) == 1:
						m.remove(r[0],shiftOffsets=True)
			elif r.duration == timeSig.barDuration and n.notes.duration > 0:
				if r[0].offset == 0 and len(r) == 1:
					m.remove(r[0],shiftOffsets=True)

def make_serial_code(data,keySig,timeSig):
	notes = []
	final = ascertain_tonic(data,keySig,timeSig)
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
	else:
		sliceAmt = 1
		sliceIter = 8
	return sliceAmt,sliceIter

def pc_at_first_beat(data):
	pcs = []
	for m in data.parts[0].getElementsByClass('Measure'):
		notes = [x.pitches[-1].pitchClass for x in m.notes if not x.isGrace]
		if len(notes):
			pcs.append(notes[0])
	return pcs 

def most_common_el(lst):
	return max(set(lst), key=lst.count)

def most_common_downbeat(data,timeSig):
	pcs = pc_at_first_beat(data)
	return most_common_el(pcs)

def get_dc_repeat(stream):
	last = stream.getElementsByClass('Measure')[0]
	lastMeasureIndex = 0
	if len(last.voices) != 0:
		last = last.voices[0]
	while len(last.notes) == 0:
		lastMeasureIndex -= 1
		if len(stream.getElementsByClass('Measure')[lastMeasureIndex].voices) != 0:
			last = stream.getElementsByClass('Measure')[lastMeasureIndex].voices[0]
		else:
			last = stream.getElementsByClass('Measure')[lastMeasureIndex]
	return last.notes[-1] 

def get_last_note(data,timeSig):
	repeats = {}
	for item in data.flat.getElementsByClass('RepeatMark'):
		text = item.getTextExpression().content
		note = data.flat.notes.getElementAtOrBefore(item.offset)
		repeats[text] = note 

	if 'Fine' in repeats.keys():
		last = repeats['Fine']
		end_type = 'fine'
	# elif 'D.C.' in repeats.keys():
		# last = get_dc_repeat(data)
		# end_type = 'dc'
	else:
		sliceAmt,sliceIter = get_accent_values(timeSig)
		last = data.flat.notes[-1]
		while last.isGrace == True:
			last = data.flat.notes.getElementAfterElement(last)
		end_type = 'generic'
	return last,end_type


def chordal_analysis(st,timeSig):
	keys = []
	sliceAmt,sliceIter = get_accent_values(timeSig)
	for item in st.getElementsByClass('Measure'):
		if int(item.barDurationProportion()) == 1:
			try:
				half_measures = item.splitAtQuarterLength(sliceAmt,False,False)
			except:
				half_measures = item
			for half in half_measures:
				if half.isMeasure:
					measure_notes = [x.pitches[-1].pitchClass for x in half.flat.notes]
				elif half.isChord or half.isNote:
					measure_notes = half.pitches[-1].pitchClass					
				if len(measure_notes) > 0:
					keyx = chord.Chord(measure_notes)
					if keyx.quality != 'other':
						keys.append(keyx.pitchedCommonName.split('-')[0])
	try:
		mc = most_common_el(keys)
		wt = float(keys.count(mc)) / len(keys)
		return mc,wt
	except:
		return None

def ascertain_tonic(data,keySig,timeSig):
	lastMeasureIndex = -1	
	last = data.parts[0].getElementsByClass('Measure')[lastMeasureIndex]

	return keySig

def get_resting_note(data,final):
	measures = get_all_as_measures(data)
	notes = [m.flat.notesAndRests for m in measures]
	note_dur_store = {}
	avg_dur = features.native.MostCommonNoteQuarterLength(data).extract().vector[0]
	for m in notes:
		for i,n in enumerate(m):
			if not n.isRest and n.duration.quarterLength > avg_dur:
				weight = 1
				if i+1 < len(m) and m[i+1].isRest:
					weight += 1
				if len(set(m.pitches)) == 1:
					weight += 2
				if m == notes[-1] and n == m.notes[-1]:
					weight += 3
				if n.pitches[-1].name in note_dur_store.keys():
					note_dur_store[n.pitches[-1].name] += weight
				else:
					note_dur_store[n.pitches[-1].name] = weight		
	
	sorted_values = [note_dur_store.values().index(i) for i in sorted(note_dur_store.values(),reverse=True)]
	sorted_keys = [note_dur_store.keys()[i] for i in sorted_values]
	# print note_dur_store
	# if note.Note(final).name in sorted_keys[0:2]:
		# return note.Note(final).name 
	# else:
	if len(sorted_keys) != 0:
		return sorted_keys[0]
	else:
		return None
	
def pairwise(iterable):
    out = []
    for i,x in enumerate(iterable):
    	if i+1 != len(iterable):
    		out.append((x,iterable[i+1]))
    return out

def most_common_leading_note(data,timeSig):
	leading_notes = {'C':(11,12),'D':(1,2),'E':(3,4),'F':(4,5),'G':(6,7),'A':(8,9),'B':(10,11)}
	found_leading_notes = []
	measures = get_all_as_measures(data)
	notes = [m.flat.notes for m in measures]
	pcs = []
	for m in notes:
		for n in m:
			pcs.append(n)
	for pair in pairwise(pcs):
		pcs = (pair[0].pitches[-1].pitchClass,pair[-1].pitches[-1].pitchClass)
		
		if pcs in leading_notes.values() and pair[-1].offset == 0:
			found_leading_notes.append(leading_notes.keys()[leading_notes.values().index(pcs)])
	if len(found_leading_notes) > 0:
		most_common = most_common_el(found_leading_notes)
		return most_common,found_leading_notes.count(most_common)
	else:
		return None,None

def cardinality(lst):
	store = []
	count = 0
	for i in lst:
		if i not in store:
			count += 1
			store.append(i)
	return count

def parse_bb_pitches(final,most_common_note,most_common_note_beat,lastBarKey):
	weights = [2,7,4,9]
	cleaned = []
	for i in [final,most_common_note,most_common_note_beat]:
		if i == 11:
			cleaned.append(4)
		else:
			cleaned.append(i)
	card = cardinality(cleaned)
	result = cleaned[0]
	if card == 1:
		result = cleaned[0] 
	elif card == 2:
		if lastBarKey.mode == 'major':
			result = most_common_el(cleaned)
		else:
			result = cleaned[0]
	elif card == 3:
		for i in weights:
			if i in cleaned:
				result = i 
				break


	return note.Note(result).name,card

def make_breathnach_code(data,keySig,timeSig):
	code = []
	final = ascertain_tonic(data,keySig,timeSig)
	# return "",""
	solfege_map = {'do':1,'re':2,'mi':3,'fa':4,'sol':5,'la':6,'ti':7}
	ts = data.parts[0].flat.getElementsByClass('TimeSignature')[0]
	sliceAmt,sliceIter = get_accent_values(timeSig)

	# print data.metadata.title,keySig,final,timeSig

	analStream,isSong = get_first_two_measures(data)

	lastP = None

	if isSong != True:
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
			if 'p' in locals():
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
	# print display_code
	return code,display_code