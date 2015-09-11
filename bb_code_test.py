# -*- coding: UTF-8 -*-
import os,subprocess,json,glob,re,unicodedata,string
from collections import OrderedDict
from music21 import *
from portlib.generate_index_codes import *
from portlib.levenshtein import levenshtein
import difflib	

def sort_names(lst):
	return sorted(lst,key=lambda x: int(x.split('.')[0].split('_')[-1]))

def iterate_collection_and_make_entries(cid,parent_title):
	global root,sim_data,soundslice_data,counter,completed_tunes,update,lisa_codes
	collection_dir_path = root + cid
	c = 0
	xml_data = sort_names(filter(lambda x:x.endswith('.xml'),os.listdir(collection_dir_path+"/{0}_xml/".format(cid))))
	for i,tune_xml in enumerate(xml_data[0:200]):
		# i += 38
	# for i in [52,58,59,71,73,74,75,76,79,82,84,86,88,94,96,97,98]:
		# tune_xml = xml_data[i] 
		data = converter.parse(collection_dir_path+"/{0}_xml/{1}".format(cid,tune_xml))
		data.metadata.title = data.metadata.title.replace("\I\\","").replace("\\i\\","")
		# print i,data.metadata.title.replace("\n\\"," | ")
		if len(data.parts[0].flat.notes) != 0:
			# print i
			keySig = analysis.discrete.analyzeStream(data, 'key')
			timeSig = str(data.parts[0].getElementsByClass('Measure')[0].timeSignature.ratioString)
			try:
				fe = features.native.MostCommonNoteQuarterLength(data)
				av_note_dur = duration.Duration(fe.extract().vector[0]).type		
		 	except:
				av_note_dur = 'eighth'
			breathnachCode,breathnachCodeDisplay = make_breathnach_code(data,keySig,timeSig)			
			# print breathnachCode,lisa_codes[i]
			if lisa_codes[i] != None and len(lisa_codes[i]) > 0:
				if breathnachCode[0] != lisa_codes[i][0]:
					c += 1
					print i,data.metadata.title.replace("\n\\"," | ")
					print breathnachCode,lisa_codes[i]				
				# quit()	
			# make_serial_code(data,keySig,timeSig)
	print c
root = '/users/itma/documents/port_music_files/port_collection_assets/'

with open('/users/itma/documents/port_music_files/collection_metadata_sorted.json','r') as f:
	collections_metadata = json.load(f)

collections = [x for x  in sorted(collections_metadata,key=lambda x:x['itma_pub_order'])]

flag = False

with open('shields_bb_codes_tmp1.json','r') as f:
	lisa_codes = [x['bb-code'] for x in json.load(f)]

for i,item in enumerate(collections):
	if item['itma_collection_id'] == 'goodman_vol_1':
		# print i
		# print item['itma_collection_id'],i
		iterate_collection_and_make_entries(item['itma_collection_id'],item['short_title'])
		