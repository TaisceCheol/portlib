import json

with open('itma_import.json','r') as f:
	itma_ids = json.load(f)

with open('itma_embeds.json','r') as f:
	embed_codes = json.load(f)

mapped = {}

for item in itma_ids.iteritems():
	mapped[item[0].split('.xml')[0]] = embed_codes[str(item[-1])]

with open('soundslice_data.json','w') as f:
	json.dump(mapped,f,sort_keys=True,indent=4)