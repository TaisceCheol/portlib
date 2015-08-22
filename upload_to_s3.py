import os,json,collections,subprocess
import boto
from boto.s3.key import Key

conn = boto.connect_s3()
bucket = conn.get_bucket('itma.port.assets')
root = 'port_collection_assets'

# upload_types = ['mp3','pdf','svg','png']

upload_types = ['svg','png']

for collection in filter(lambda x: not x.startswith('.'),os.listdir(root)):
	# if collection == 'goodman_vol_2':
	for sub_folder in filter(lambda x:not x.startswith('.'),os.listdir(os.path.join(root,collection))):
		if sub_folder.split('_')[-1] in upload_types:
			folder_key = os.path.join(collection,sub_folder)
			file_list = filter(lambda x:not x.startswith('.'),os.listdir(os.path.join(root,folder_key)))
			file_list.sort(key=lambda x: int(x.split('.')[0].split('_')[-1]))
			for item in file_list:
				item_key = os.path.join(folder_key,item)				
				path = os.path.join(root,item_key)				
				if item.endswith('.png'):
					subprocess.check_output(['convert',path,'-resize','300x120','-gravity','center','-extent','320x120',path])
				k = Key(bucket)
				k.key = item_key
				k.set_contents_from_filename(path)
				print item_key