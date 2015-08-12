import os,json,re,unicodedata,string

def map_soundslice_urls(tune_id,soundslice_data):
	try:
		return soundslice_data[tune_id+'.xml']
	except:
		return 'none'

def pretty_print(data):
	print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

def sort_names(lst):
	return sorted(lst,key=lambda x: int(x.split('.')[0].split('_')[-1]))

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str.replace("'",''))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def sortBySize(obj):
	if obj.size == None:
		return 0
	else:
		return int(obj.size)