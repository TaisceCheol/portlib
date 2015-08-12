# -*- coding: UTF-8 -*-
import os,subprocess,json,glob,re,unicodedata,string
from collections import OrderedDict
from music21 import *
from numpy import diff
from random import *

def make_abc_code(data,timeSig):
	mcount = 0	
	lastDur = False;
	code = ""
	if data.parts[0].getElementsByClass('Measure')[0].barDurationProportion() >= 1:
		mlimit = 2
	else:
		mlimit = 3
	for m in data.parts[0].getElementsByClass('Measure'):
		for nx in m.flat.notes:
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

def get_first_two_measures(data):
	mcount = 0
	s = stream.Stream()
	for m in data.parts[0].getElementsByClass('Measure'):
		# ignore anacrusis
		if float(str(m.barDurationProportion())) >= 1:
			for i,n in enumerate(m.flat.notesAndRests):
				# print n.pitch
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
	else:
		sliceAmt = 1
		sliceIter = 8
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