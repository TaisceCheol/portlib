import os

def make_folders(col):
	global root
	folders = ['ly','midi','midi_analysis','mp3','pdf','sib','svg','xml','png']
	if not os.path.exists(os.path.join(root,col,col+'_png')):
		os.mkdir(os.path.join(root,col,col+'_png'))
	# if os.path.exists(os.path.join(root,col)):
	# 	print 'Exists Already: %s'%col
	# else:
	# 	os.mkdir(os.path.join(root,col))
	# 	for item in folders:
	# 		os.mkdir(os.path.join(root,col,col+'_'+item))
	return None

collections = [
	"freeman",
	"allans_irish_fiddler",
	"amhrain_mhuighe_seola",
	"bunting_vol_1",
	"bunting_vol_2",
	"claisceadal",
	"clark_oconnell_ms",
	"curtin_ms",
	"curry_petrie_1882",
	"galwey_in_graves",
	"galwey_croonauns",
	"ganly",
	"hardebeck_ceol_na_ng",
	"hardebeck_port_cor_pt_1",
	"hardebeck_port_cor_pt_2",
	"hime",
	"morrison_tutor",
	"obrien_tutor",
	"obrien_ifdm",
	"neal",
	"padraig_okeeffe_ms_bk_1",
	"padraig_okeeffe_ms_bk_2",
	"padraig_okeeffe_ms_bk_3",
	"padraig_okeeffe_ms_bk_4",
	"pw_joyce_petrie_1855",
	"pw_joyce_petrie_1882",
	"pw_joyce_stanford",
	"pw_joyce_ancient_irish_music",
	"pw_joyce_irish_music_song",
	"pw_joyce_irish_peasant_songs",
	"pw_joyce_old_irish_folk_music",
	"pw_joyce_nli_1912",
	"pw_joyce_msj25",
	"roche_vol_1",
	"roche_vol_2",
	"roche_vol_3",
	"roche_vol_4",
	"ryans",
	"goodman_vol_1",
	"goodman_vol_2"
]

root = 'port_collection_assets/'

print len(collections)

[make_folders(x) for x in collections]
