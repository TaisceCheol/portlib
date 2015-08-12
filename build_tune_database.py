# -*- coding: UTF-8 -*-
import os,subprocess,json,glob,re,unicodedata,string
from collections import OrderedDict
from music21 import *
from numpy import diff
from pymongo import MongoClient
from random import *
from portlib.generate_index_codes import *
from portlib.utils import *

ENV = 'production'
UPDATE = True

completed_tunes = []
counter = 1

with open("tune_database_log.txt",'r') as f:
	data = f.readlines()
	if len(data) != 0 and UPDATE != True:
		for item in data:
			datums = item.split('\t')
			completed_tunes.append(datums[0].strip())
			counter = int(datums[-1])
	else:
		counter = 1

print completed_tunes,counter

if ENV == 'production':
	# port production database
	client = MongoClient('port.itma.ie:32768')
	db = client['itma-tune-database-production']
	db.authenticate('port','VEZxYitFTXA4VExWN1pqYjZKK21QYmVzSUVFL20wUWo4YmczRlJBdTd6TT0K')
else:
	client = MongoClient('localhost')
	db = client['itma-tune-database']

collection = db.itma_tunes

def iterate_collection_and_make_entries(cid,parent_title):
	global root,sim_data,soundslice_data,counter,completed_tunes,update
	collection_dir_path = root + cid
	xml_data = sort_names(filter(lambda x:x.endswith('.xml'),os.listdir(collection_dir_path+"/{0}_xml/".format(cid))))
	svg_data = sort_names(filter(lambda x:x.endswith('.svg'),os.listdir(collection_dir_path+"/{0}_svg/".format(cid))))
	ly_data = sort_names(filter(lambda x:x.endswith('.ly'),os.listdir(collection_dir_path+"/{0}_ly/".format(cid))))
	midi_data = sort_names(filter(lambda x:x.endswith('.mid'),os.listdir(collection_dir_path+"/{0}_midi/".format(cid))))
	pdf_data = sort_names(filter(lambda x:x.endswith('.pdf'),os.listdir(collection_dir_path+"/{0}_pdf/".format(cid))))
	mp3_data = sort_names(filter(lambda x:x.endswith('.mp3'),os.listdir(collection_dir_path+"/{0}_mp3/".format(cid))))
	tunes_in_collection = len(xml_data)
	print cid
	for i,tune_xml in enumerate(xml_data):
		if counter < 2225:
			counter += 1
		else:
			if not tune_xml in completed_tunes or UPDATE == True:
				itma_id = counter
				tune_id = tune_xml.split('.')[0]
				data = converter.parse(collection_dir_path+"/{0}_xml/{1}".format(cid,tune_xml))
				# grab text data from files
				title = " / ".join([x.strip('[').strip(']').strip('\\') for x in data.metadata.title.split('\\n')])
				title = title.replace("\I\\","").replace("\\i\\","")
				text_content = []
				search_terms = []
				alt_title = ""
				text_elements = sorted(list(data.getElementsByClass('TextBox')),key=lambda x:sortBySize(x))	
				for item in text_elements:
					if item.content == title:
						title_pos = item.positionHorizontal
					elif title.startswith(item.content) != -1:
						title_pos = item.positionHorizontal
				for item in text_elements:
					if item.content != title:
						if item.positionHorizontal == title_pos:
							alt_title = item.content.replace('Or','').replace('or','').strip().replace("‘","'").replace("’","'").strip("'").strip()					
						else:
							text_content.append(item.content)	
				# remove alt titles that are simply numbers
				try:
					int(alt_title)
					alt_title = ''
				except:
					pass	
				title = re.split('^(\d+\.*\s*)',title.replace("‘","'"))[-1].strip("'").strip().replace("’","'")		
				for itemtext in title.split():
					search_terms.append(remove_accents(unicode(itemtext)).strip())		
				for itemtext in alt_title.split():
					search_terms.append(remove_accents(unicode(itemtext)).strip())		
				search_terms = " ".join(search_terms)
				try:
					with open(os.path.join('analysis_results',tune_xml.replace('.xml','.json')),'r') as f:
						sim_data = json.load(f)
				except:
					sim_data = []
				if len(data.parts[0].flat.notes) == 0:
					tune = {
						'itma_id':itma_id,
						'tune_id':tune_id,
						'title':title,
						'alt_title':alt_title,
						'ed_remarks':text_content,				
						# used to query the collections database
						'itma_collection_id':cid,
						'index_in_collection':i,
						'parent_collection_title':parent_title,
						'tunes_in_parent_collection':tunes_in_collection,
						'similarity_scores':sim_data,
						'urls':{
							'soundslice':"n/a",
							'pdf':"https://d1307vzs6glz9b.cloudfront.net/{0}/{0}_pdf/{1}.pdf".format(cid,tune_id),
							'incipit':"https://d1307vzs6glz9b.cloudfront.net/{0}/{0}_svg/{1}.svg".format(cid,tune_id),
							'mp3':"n/a",
							'png':"https://d1307vzs6glz9b.cloudfront.net/{0}/{0}_png/{1}.png".format(cid,tune_id)
						},
						'search_terms':search_terms,
						'metadata':{	
							"mostCommonInterval":"n/a",
							"amountOfApreggiation":"n/a",
							"averageNoteDuration": "n/a",
							"ambitus":"n/a",
							"pitchClassDist":"n/a",
							"keySig":"n/a",
							"timeSig":"n/a",
							"abcCode":"n/a",
							"lyCode":"n/a",
							"parsonsCode":"n/a",
							"breathnachCode":"n/a",
							"breathnachCodeDisplay":"not available",						
							"serialCode":"n/a",
							"noteDensity":"n/a",
							"chromaticMotion":"n/a",
							"pitchHistogram":"n/a"
						}
					}
				else:
					# Some basic features
					try:
						fe = features.jSymbolic.AmountOfArpeggiationFeature(data)
						arp_amt = fe.extract().vector[0]
					except:
						arp_amt = 0
					# most common melodic interval feature
					try:
						fe = features.jSymbolic.MostCommonMelodicIntervalFeature(data)
						mc_mel_int = interval.Interval(fe.extract().vector[0]).niceName
					except:
						mc_mel_int = 0
					# note density
					try:
						fe = features.jSymbolic.NoteDensityFeature(data)
						note_density = fe.extract().vector[0];
					except:
						note_density = 0
					# chromatic motion
					try:
						fe = features.jSymbolic.ChromaticMotionFeature(data)
						chromatic_motion = fe.extract().vector[0];
					except:
						chromatic_motion = 0
					# average note duration feature
					try:
						fe = features.native.MostCommonNoteQuarterLength(data)
						av_note_dur = duration.Duration(fe.extract().vector[0]).type
					except:
						av_note_dur = 'Unavailable'
					# most common pitch feature
					fe = analysis.discrete.Ambitus()
					ambitus = fe.getPitchSpan(data)
					if ambitus != None:
						ambitus = [x.nameWithOctave for x in ambitus]
					else:
						ambitus = "Unavailable"
					# time sig
					try:
						timeSig = str(data.parts[0].getElementsByClass('Measure')[0].timeSignature.ratioString)
					except:
						timeSig = 'Unavailable'
					# key sig
					# p = analysis.discrete.KrumhanslSchmuckler()
					keySig = analysis.discrete.analyzeStream(data, 'key')
					# data.parts.flat.getElementsByClass('KeySignature')
					# soundslice
					try:
						soundslice_url = soundslice_data[tuid.split('.')[0]]
					except:
						soundslice_url = "none"			
					# pich class distribution
					try:
						fe = features.jSymbolic.PitchClassDistributionFeature(data)
						pc_dist = fe.extract().vector
					except:
						pc_dist = [0]
					# parsonsCode
					parsonsCode = make_parsons_code(data)
					# serialCode
					serialCode = make_serial_code(data,keySig,timeSig)		
					# breathnachCode
					breathnachCode,breathnachCodeDisplay = make_breathnach_code(data,keySig,timeSig)				
					# lilyCode
					lilyCode = make_ly_code(data)	
					# abcCode
					abcCode = make_abc_code(data,timeSig)
					tune = {
						'itma_id':itma_id,
						'tune_id':tune_id,
						'title':title,
						'alt_title':alt_title,
						'ed_remarks':text_content,					
						# used to query the collections database
						'itma_collection_id':cid,
						'index_in_collection':i,
						'parent_collection_title':parent_title,
						'tunes_in_parent_collection':tunes_in_collection,				
						'similarity_scores':sim_data,
						'urls':{
							'soundslice':map_soundslice_urls(tune_id,soundslice_data),
							'pdf':"https://d1307vzs6glz9b.cloudfront.net/{0}/{0}_pdf/{1}.pdf".format(cid,tune_id),
							'incipit':"https://d1307vzs6glz9b.cloudfront.net/{0}/{0}_svg/{1}.svg".format(cid,tune_id),
							'mp3':"https://d1307vzs6glz9b.cloudfront.net/{0}/{0}_mp3/{1}.mp3".format(cid,tune_id),
							'png':"https://d1307vzs6glz9b.cloudfront.net/{0}/{0}_png/{1}.png".format(cid,tune_id)
						},
						"search_terms":search_terms,
						'metadata':{	
							"mostCommonInterval":mc_mel_int,
							"amountOfApreggiation":arp_amt,
							"averageNoteDuration": av_note_dur,
							"ambitus":ambitus,
							"pitchClassDist":pc_dist,
							"key":keySig.name,
							"tonalCertainty":keySig.tonalCertainty(),
							"timeSig":timeSig,
							"lyCode":lilyCode,
							"abcCode":abcCode,
							"parsonsCode":parsonsCode,
							"breathnachCode":breathnachCode,
							"breathnachCodeDisplay":breathnachCodeDisplay,
							"serialCode":serialCode,
							"noteDensity":note_density,
							"chromaticMotion":chromatic_motion,
						}
					}
				# pretty_print(tune)
				counter += 1
				collection.update({'itma_id':itma_id},{"$set": {"metadata":tune['metadata'],"title":tune["title"],"urls":tune['urls']}})
				# collection.insert(tune)
				if UPDATE != True:
					with open("tune_database_log.txt",'a') as f:
						f.write("%s \t %s\n" % (tune_xml,itma_id))
	return None

# read collection assets paths
root = '/users/itma/documents/port_music_files/port_collection_assets/'

with open('/users/itma/documents/port_music_files/collection_metadata_sorted.json','r') as f:
	collections_metadata = json.load(f)

collections = [x for x  in sorted(collections_metadata,key=lambda x:x['itma_pub_order'])]

#soundslice data
with open('soundslice_data.json','r') as f:
	soundslice_data = json.load(f)

flag = False

for item in collections:
	if item['itma_collection_id'] != "bunting_vol_3":
		iterate_collection_and_make_entries(item['itma_collection_id'],item['short_title'])

