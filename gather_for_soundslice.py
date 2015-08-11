import os,shutil,glob

output = 'itma_xml_0615'

source = 'port_collection_assets/'

data = glob.glob(source+"*/*_xml/*.xml")

if not os.path.exists(output):
	os.mkdir(output)

for f in data:
	shutil.copy2(f,output)
