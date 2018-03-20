from pymongo import MongoClient
import subprocess

client = MongoClient('localhost:3131')
db = client['tune_database']

collection = db.itma_collections

for item in collection.find():
	print item['title']

# db.authenticate('port','VEZxYitFTXA4VExWN1pqYjZKK21QYmVzSUVFL20wUWo4YmczRlJBdTd6TT0K')

# host = 'port.itma.ie'
# port = '32768'
# db = 'itma-tune-database-production'
# username = 'port'
# password = 'VEZxYitFTXA4VExWN1pqYjZKK21QYmVzSUVFL20wUWo4YmczRlJBdTd6TT0K'
# output_dir = 'port-backups/'

# # host = 'localhost'
# # port = "27017"
# # db = 'itma-tune-database'

# collections = ['itma_collections','itma_tunes','users']

# for cc in collections:

# 	cmd = [
# 	    'mongodump',
# 	    '-host', host,
# 	    '-u', username,
# 	    '-p', password,
# 	    '-d', db,
# 	    '-c',cc,
# 	    '--port', port,
# 	    '-o', output_dir
# 	]

# 	subprocess.check_output(cmd)
#         