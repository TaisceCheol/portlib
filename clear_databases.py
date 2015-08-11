from pymongo import MongoClient

ENV = 'production'

if ENV == 'production':
	# port production database
	client = MongoClient('port.itma.ie:32768')
	db = client['itma-tune-database-production']
	db.authenticate('port','VEZxYitFTXA4VExWN1pqYjZKK21QYmVzSUVFL20wUWo4YmczRlJBdTd6TT0K')
else:
	client = MongoClient('localhost')
	db = client['itma-tune-database']

db.itma_collections.remove()
# db.itma_tunes.remove()
