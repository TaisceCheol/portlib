# -*- coding: UTF-8 -*-
from lxml import html
import requests,json


lisa_index = "https://s3-eu-west-1.amazonaws.com/itma.dl.printmaterial/goodman/Goodman2_full_index.htm"

page = requests.get(lisa_index)
tree = html.fromstring(page.text)

# print tree
data = tree.xpath('//p/child::text()')

i = 0

numbers = []

for p in data:
	# if i > 100:break
	print [p]
	if p.endswith('}'):
		bb_code = unicode(p).replace("}","").split(u"~\xa0")[-1].split("~")[-1].split(u"\xa0")[0].replace("_","").replace("'","").strip()
		bb_code = " ".join(bb_code.split(" ")[0:2])
		numbers.append(bb_code.split(" ")[0])
		i += 1

print len(numbers)