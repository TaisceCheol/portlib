import json,os
from pymongo import MongoClient

def count_tunes(id):
	path = '/users/itma/documents/port_music_files/port_collection_assets/{0}/{0}_xml/'.format(id)
	if os.path.exists(path):
		return len(filter(lambda x:x.endswith('.xml'),os.listdir(path)))
	else:
		return 0

ENV = 'production'

# port production database
if ENV == 'production':
	client = MongoClient('port.itma.ie:32768')
	db = client['itma-tune-database-production']
	db.authenticate('port','VEZxYitFTXA4VExWN1pqYjZKK21QYmVzSUVFL20wUWo4YmczRlJBdTd6TT0K')
else:
	client = MongoClient('localhost')
	db = client['itma-tune-database']


collection = db.itma_collections

# # # read collection assets paths
root = 'port_collection_assets/'

with open('collection_metadata_sorted.json','r') as f:
	collections_metadata = json.load(f)
	for entry in collections_metadata:
		# print [entry['itma_collection_id']],count_tunes(entry['itma_collection_id'])
		entry['selected'] = True
		entry['tunes_in_collection'] = count_tunes(entry['itma_collection_id'])
		collection.insert(entry)