import os,json,collections

def clean_value(item):
	if len(item) > 1:
		if item[1].find('-Infinity') == -1:
			return {'id':item[0].strip('.mid'),'value':float(item[1].strip('\n'))}

data = 'analysis_results'

for item in filter(lambda x:not x.startswith('.') and x.endswith('.txt'),os.listdir(data)):
	with open(os.path.join(data,item),'r') as f:
		results = [x.split('\t') for x in f.readlines()]
		results = filter(lambda x:x!=None,[clean_value(x) for x in results][1:])
		with open(os.path.join(data,item.replace('.txt','.json').replace('results_','')),'w') as js_file:
			json.dump(results,js_file,indent=2)
