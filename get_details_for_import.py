# -*- coding: UTF-8 -*-
import os,subprocess,json,glob,re,unicodedata,string
from collections import OrderedDict
from music21 import *
from numpy import diff
from pymongo import MongoClient
from random import *
from portlib.generate_index_codes import *
from portlib.utils import *
import csv
from lxml import etree
from HTMLParser import HTMLParser

completed_tunes = []
counter = 1744

html = HTMLParser()

def iterate_collection_and_make_entries(cid,parent_title,text,creator,pub_date,pub_details):
	global root,sim_data,soundslice_data,counter,completed_tunes,update
	collection_dir_path = root + cid
	xml_data = sort_names(filter(lambda x:x.endswith('.xml'),os.listdir(collection_dir_path+"/{0}_xml/".format(cid))))
	tunes = []
	for i,tune_xml in enumerate(xml_data):
		itma_id = counter
		tune_id = tune_xml.split('.')[0]
		data = converter.parse(collection_dir_path+"/{0}_xml/{1}".format(cid,tune_xml))
		# grab text data from files
		title = " / ".join([x.strip('[').strip(']').strip('\\') for x in data.metadata.title.split('\\n')])
		title = title.replace("\I\\","").replace("\\i\\","")
		title = re.split('^(\d+\.*\s*)',title.replace("‘","'"))[-1].strip("'").strip().replace("’","'")		
		soundslice_url = "https://www.soundslice.com%s" % map_soundslice_urls(tune_id,soundslice_data)
		port_url = "http://port.itma.ie/score/ITMA_%s" % counter
		tune_el = etree.Element('tune')
		refno = etree.SubElement(tune_el,'identifier')
		refno.text = tune_id.replace('_','-')
		col_title = etree.SubElement(tune_el,'parent_collection')
		col_title.text = parent_title.decode('UTF-8')
		creator_el = etree.SubElement(tune_el,'creator')
		if type(creator) == list:
			creator_el.text = "; ".join([unicode(x) for x in creator])
		else:
			creator_el.text = unicode(creator)
		pubdate_el = etree.SubElement(tune_el,'publication_date')
		pubdate_el.text = pub_date		
		tune_title_el = etree.SubElement(tune_el,'title')
		tune_title_el.text = title.decode('utf-8').replace(" / s96\  / s136\\"," ").replace("\\s12\\ \\s136\\","").replace("I\\","")
		soundslice_el = etree.SubElement(tune_el,'soundslice_url')
		soundslice_el.text = soundslice_url.decode('utf-8')
		port_el = etree.SubElement(tune_el,'port_url')
		port_el.text = port_url.decode('utf-8')
		pdf_el = etree.SubElement(tune_el,'pdf_url')
		pdf_el.text = "https://scores.itma.ie/{0}/{0}_pdf/{1}.pdf".format(cid,tune_id)		
		port_index = etree.SubElement(tune_el,'port_index')
		port_index.text = str(counter).decode('utf-8')
		counter += 1
		print counter
		tunes.append(tune_el)
	return tunes

# read collection assets paths
root = '/users/itma/documents/port_music_files/port_collection_assets/'

with open('/users/itma/documents/port_music_files/collection_metadata_sorted.json','r') as f:
	collections_metadata = json.load(f)

collections = [x for x  in sorted(collections_metadata,key=lambda x:x['itma_pub_order'])]

#soundslice data
with open('soundslice_data.json','r') as f:
	soundslice_data = json.load(f)

records = etree.Element('scores')

for item in collections:
	if item['itma_collection_id']=='bunting_vol_3':
		continue
	record = iterate_collection_and_make_entries(item['itma_collection_id'],item['short_title'],item['text'],item['collector'],item['publication_date'],item['publication_details'])
	for tune in record:
		records.append(tune)

tree = etree.ElementTree(records)
tree.write("tune_collections.xml",pretty_print=True,encoding="utf-8")

