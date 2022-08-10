import phoenix_core as core
import status
import xml.etree.ElementTree as et
import urllib.request
import urllib.error
import json
import tree
import re
import time
import sqlite3 as sql

class Position:
	# Position Types
	POSITIONTYPE_NONE = 0x00
	POSITIONTYPE_GP = 0x01
	POSITIONTYPE_SHIP = 0x02
	POSITIONTYPE_STARBASE = 0x03
	POSITIONTYPE_DEBRIS = 0x04
	POSITIONTYPE_POLITICAL = 0x05
	POSITIONTYPE_PLATFORM = 0x06
	POSITIONTYPE_AGENT = 0x07
	POSITIONTYPE_OUTPOST = 0x08
	POSITIONTYPE_CARGODUMP = 0x09
	pos_types={	POSITIONTYPE_NONE:		'None',
				POSITIONTYPE_GP:		'Gp',
				POSITIONTYPE_SHIP:		'Ship',
				POSITIONTYPE_STARBASE:	'StarBase',
				POSITIONTYPE_DEBRIS:	'Debris',
				POSITIONTYPE_POLITICAL:	'Political',
				POSITIONTYPE_PLATFORM:	'Platform',
				POSITIONTYPE_AGENT:		'Agent',
				POSITIONTYPE_OUTPOST:	'Output',
				POSITIONTYPE_CARGODUMP:	'Cagro Dump'}
	reverse_pos_types={	'None':		POSITIONTYPE_NONE,
						'Gp':		POSITIONTYPE_GP,
						'Ship':		POSITIONTYPE_SHIP,
						'Starbase':	POSITIONTYPE_STARBASE,
						'Debris':	POSITIONTYPE_DEBRIS,
						'Political':POSITIONTYPE_POLITICAL,
						'Platform':	POSITIONTYPE_PLATFORM,
						'Agent':	POSITIONTYPE_AGENT,
						'Output' :	POSITIONTYPE_OUTPOST,
						'Cagro Dump':POSITIONTYPE_CARGODUMP}
	# Positions search types
	PST_POSITION = 0
	PST_SYSTEM = 1
	PST_NAME = 2
	PST_NUMBER = 3
	PST_LAST = 4
	PST_TUS = 5
	PST_INTEGRITY = 6
	PST_RECREATION = 7
	PST_SQUADRON = 8
	PST_TUS_NO_ORDERS = 9
	PST_DMG = 10
	PST_TUS_ORDERS = 11
	PST_DEAD_TURNS = 12

	search_names={	PST_POSITION:"Positions",
					PST_SYSTEM:"Systems",
					PST_NAME:"Names",
					PST_NUMBER:"Number",
					PST_LAST:"Last Update",
					PST_TUS:"Tus",
					PST_INTEGRITY:"Integrity",
					PST_RECREATION:"Recreation",
					PST_SQUADRON:"Squadron",
					PST_TUS_NO_ORDERS:"Tus/No Orders",
					PST_DMG:"Damage",
					PST_TUS_ORDERS:"Tus/Orders",
					PST_DEAD_TURNS:"Not Implemented"}
	## names

	def __getitem__(self, index):
		return self.data[index]
	def __setitem__(self, index, item):
		self.data[index]=item
	def __contains__(self, item):
		return item in self.data

	search_types = {PST_POSITION: 'Position Type',
					PST_SYSTEM: 'System / Planet',
					PST_NAME: 'Name',
					PST_NUMBER: 'Number',
					PST_LAST: 'Last Accessed',
					PST_TUS: 'Tus',
					PST_TUS_NO_ORDERS: 'Tus and No Orders',
					PST_TUS_ORDERS: 'Tus and Orders',
					PST_INTEGRITY: 'Integrity',
					PST_RECREATION: 'Recreation',
					PST_SQUADRON: 'Squadron',
					PST_DMG: 'Damage',
					PST_DEAD_TURNS: 'Blocked with Error'}

	def __init__(self,data,type='xml'):
		if type=='xml':
			self.create_from_xml(data)
			self.update()
		elif type=='json':
			data = json.loads(data)
			self.set_data(data)
		else:
			self.set_data(data)
		self.sort=''
	def set_data(self,data):
		if data:
			self.data=data
	def create_from_xml(self,data):
		self.data = {'type': 'none', 'system': 'none'}
		if data.tag == 'position':
			if len(data.items()) > 0:
				for attrib, val in data.items():
					self.data[attrib] = val
		for pos_data in data:
			if pos_data.tag == 'ship_info':
				self.data['ship_info'] = {}
				if len(pos_data.items()) > 0:
					for attrib, val in pos_data.items():
						self.data['ship_info'][attrib.lower()] = val
			elif pos_data.tag == 'loc_info':
				self.data['loc_info'] = {}
				if len(pos_data.items()) > 0:
					for attrib, val in pos_data.items():
						self.data['loc_info'][attrib.lower()] = val
			elif pos_data.tag == 'cargo_space':
				self.data['cargo_space'] = {}
				for cargo in pos_data:
					if len(cargo.items()) > 0:
						cargo_type = '_'
						for attrib, val in cargo.items():
							if attrib == 'type':
								cargo_type = val.replace(' ', '_').lower()
						self.data['cargo_space'][cargo_type] = {}
						for attrib, val in cargo.items():
							if attrib != 'type':
								self.data['cargo_space'][cargo_type][attrib.lower()] = val
			elif pos_data.tag == 'turns':
				self.data['turns'] = []
				for turn in pos_data:
					if len(turn.items()) > 0:
						for attrib, val in turn.items():
							if attrib == 'day':
								self.data['turns'].append(int(val))
			elif pos_data.tag == 'system_text':
				self.data['system'] = pos_data.text
			else:
				self.data[pos_data.tag] = pos_data.text
		# swap around type
		self.data['type_name']=self.data['type']
		if self.data['type'] in Position.reverse_pos_types:
			self.data['type']=Position.reverse_pos_types[self.data['type']]
		else:
			self.data['type']=0
		# move num to id
		self.data['id']=self.data['num']
		del self.data['num']

	def last_turn(self):
		if 'turns' in self.data and 0 in self.data['turns']:
			return self.data['turns'][0]
		return 0

	def find(self):
		cur = core.db().cursor()
		cur.execute("select * from positions where id=? and user_id=?",(self.data['id'], core.user_id()))
		return cur.fetchone()

	def update(self):
		if 'ext_name' in self.data:
			del self.data['ext_name']
		cur = core.db().cursor()
		#write position to db
		if self.find() == None:
			query = (self.data['id'], core.user_id(), self.data['name'],self.last_turn(), self.data['type_name'], self.data['system'],json.dumps(self.data))
			cur.execute("insert into positions values (?,?,?,?,?,?,?)", query)
		else:
			query = (self.last_turn(), self.data['type_name'], self.data['name'], self.data['system'], json.dumps(self.data),self.data['id'], core.user_id())
			cur.execute("update positions SET name=?,last_turn=?,type=?,system=?,data=? where id=? and user_id=?",query)

		#write positons turn to database if they are not already present
		if 'turns' in self.data:
			self.data['turns'].sort() # places oldest turn in first array pos
			# search for turns in turns younger than oldest turn on nexus - should always find duplicates in db
			cur.execute("select day from  turns where pos_id=? and user_id=? and day>=?", (self.data['id'], core.user_id(),self.data['turns'][0]))
			turn_list = cur.fetchall()
			turns={}
			for turn in turn_list:
				turns[turn[0]]=1
			for turn_day in self.data['turns']:
				if turn_day not in turns:
					cur.execute("insert into turns values (?,?,?,?,?)", (self.data['id'],self.data['name'],core.user_id(),turn_day,0))
		core.db().commit()

	def current_tus(self):
		game_day = status.current_day()
		if 'tus' not in self.data['loc_info'] or game_day==0:
			return 0
		tus= int(self.data['loc_info']['tus'])
		last_update_day= int(self.data['loc_info']['day'])
		diff = 0
		if game_day > 0:
			diff = game_day - last_update_day
		# we have 60TU extra because it's for tommorrow
		if diff >= 0:
			tus = tus + (diff + 1) * 60
		# limit to 300
		if tus > 300:
			tus = 300
		return tus

	def create_html_data(self):
		self.data['html']=""
		cur = core.db().cursor()
		cur.execute("select day,file_name from turns where pos_id=? and user_id=? order by day desc limit 10",(self.data['id'], core.user_id()))
		turn_list = cur.fetchall()
		for turn in turn_list:
			turn_file=core.turn_path(turn[1],self.data['id'],turn[0],True)
			date=core.date(turn[0],True)
			self.data['html']+="<a class='turn_files' href='"+turn_file+"' target='_blank'>"+date+"</a>"

	def sort_data(self,user_search):
		day=status.current_day()
		tus=self.current_tus()
		if self['type']!=Position.POSITIONTYPE_GP and self['type']!=Position.POSITIONTYPE_SHIP:
			tus=-300
		integrity=200.0
		if 'int' in self['loc_info']:
			integrity=float(self['loc_info']['int'])
		rec =-10
		if 'rec' in self['loc_info']:
			rec =(day-int(self['loc_info']['rec']))/5
		orders=False
		if 'orders' in self and self['orders']!='false':
			orders=True
		# set sort
		self.sort = ''
		self['cat_id']=0
		# simple convertions
		if user_search==Position.PST_POSITION:
			self.sort = self['type_name']
			self['cat_id']=self['type']
		elif user_search == Position.PST_SYSTEM:
			self.sort=self['system']
			res = re.match(".*\\((\\d+)\\)",self['system'])
			if res != None:
				self['cat_id'] =int(res.groups(0)[0])
		elif user_search == Position.PST_NAME:
			self.sort=self['name']
		elif user_search == Position.PST_NUMBER:
			self.sort=self['id']
		elif user_search == Position.PST_SQUADRON:
			self.sort = 'No Squadron'
			if 'squadron' in self:
				self.sort=self['squadron']
				res = re.match(".*\\((\\d+)\\)", self['squadron'])
				if res != None:
					self['cat_id'] = int(res.groups(0)[0])
		elif user_search == Position.PST_DEAD_TURNS:
			self.sort='Not implemented'
		cat_name=self.sort

		# differnt cat names + quantisation of sort
		if user_search == Position.PST_LAST:
			last=0
			if 'day' in self['loc_info']:
				last = int(self['loc_info']['day'])
			self.sort=last
			self['cat_id'] = last
			cat_name =core.date(last,True)
		if user_search == Position.PST_NAME or user_search == Position.PST_NUMBER:
			cat_name='Positions'
		if user_search == Position.PST_TUS or user_search == Position.PST_TUS_ORDERS or user_search == Position.PST_TUS_NO_ORDERS:
			if (user_search == Position.PST_TUS_ORDERS or user_search == Position.PST_TUS_NO_ORDERS) and orders==(user_search == Position.PST_TUS_NO_ORDERS):
				tus = -300
			if tus<=-300:
				self.sort = -300
				cat_name='Tus not used'
				if 	user_search == Position.PST_TUS_NO_ORDERS:
					cat_name+=' or has orders'
				if user_search == Position.PST_TUS_ORDERS:
					cat_name+=' or has no orders'
			elif tus >= 300:
				self.sort = 300
				cat_name = '300 Tus'
			else:
				self.sort = 30 * int(tus / 30)
				cat_name =str(self.sort)+" <img src='images/r_arr.gif'/> "
				if (tus+30 > 300):
					cat_name+='300 Tus'
				else:
					cat_name+=str(self.sort+30)+' Tus'
			self['cat_id'] = self.sort
		if user_search == Position.PST_DMG:
			dmg =0.0
			if 'ship_info' in self and 'dmg' in self['ship_info']:
				res = re.match("(\\d+\\.?\\d+)%", self['ship_info']['dmg'])
				if res != None:
					dmg  = float(res.groups(0)[0])
			if dmg == 0.0:
				cat_name = '0%'
			elif dmg >= 100.0:
				cat_name = '100%'
			else:
				dmg = float(10 * int(dmg / 10))
				cat_name = str(dmg)+"% <img src='images/r_arr.gif'/> "
				if dmg+10 >= 100:
					cat_name+='100%'
				else:
					cat_name+=str(dmg+10)+'%'
				cat_name+= " Damage"
			self.sort=dmg
			self['cat_id'] = int(dmg)
		if user_search == Position.PST_INTEGRITY:
			if integrity == 0.0:
				cat_name = '0%'
			elif integrity >= 100.0:
				cat_name = '100%'
			else:
				integrity = float(10 * int(integrity / 10))
				cat_name = str(integrity) + "% <img src='images/r_arr.gif'/> "
				if integrity + 10 >= 100:
					cat_name += '100%'
				else:
					cat_name += str(integrity + 10) + '%'
				cat_name += " Integrity"
			self.sort=integrity
			self['cat_id'] = int(integrity)
		if user_search == Position.PST_RECREATION:
			if rec == -10:
				cat_name = 'Recreation not used'
			else:
				rec = 10 * (int)(rec / 10)
				cat_name =str(rec)+" <img src='images/r_arr.gif'/> "+str(rec+10)+' Weeks'
			self.sort=int(rec)
			self['cat_id'] = int(rec)
		self['ext_name']=self['name']+" ("+str(self['id'])+")"
		return cat_name


collasped_cats={}
cat_list={}
def sort_list(user_search,pos_flag=-1,filter_op=False):
	global cat_list
	type_cnt = {}
	cat_list = {}
	for pos in pos_list:
		# ignore certain position types
		if pos_flag!=-1:
			flag=0 #ss_position_type_to_flag($pos['type']);
			if ((flag & pos_flag)==0):
				continue
			if filter_op and pos.data['type_name']=='Outpost':
				continue
		cat_name=pos.sort_data(user_search)
		if pos['cat_id'] not in cat_list:
			cat_list[pos['cat_id']]=cat_name
		if pos['cat_id'] not in type_cnt:
			type_cnt[pos['cat_id']]=0
		type_cnt[pos['cat_id']]+=1

	if len(cat_list)==0:
		cat_list={0:"Positions"}
	# create collasped list
	global collasped_cats
	collasped_cats={}
	for i, (k,v) in enumerate(type_cnt.items()):
		collasped_cats[k]=str(v) + ' Positions'
	reverse = False
	if 	user_search==Position.PST_RECREATION or user_search==Position.PST_TUS_NO_ORDERS or \
		user_search==Position.PST_LAST or user_search==Position.PST_TUS_ORDERS or \
		user_search==Position.PST_TUS or user_search==Position.PST_DMG:
		reverse=True
	pos_list.sort(key=lambda x: (x.sort,x.data['type_name'],x.data['name']), reverse=reverse)

pos_list=[]
last_error=''

def load_from_site():
	core.data['last_actions']['pos_list'] = status.data['current_day']
	core.data['last_actions']['upload_time'] = int(time.time())
	core.save()

	global last_error
	req=core.phoenix_request('pos_list')
	if req!=None:
		xml_data=None
		try:
			xml_data=urllib.request.urlopen(req)
		except urllib.error.URLError as e:
			last_error=e.reason
		if xml_data!=None:
			process_data(xml_data)
			return True
	return False

def process_data(xml_data):
	global pos_list
	pos_list=[]
	tree = et.parse(xml_data)
	root = tree.getroot()
	for child in root:
		for data in child:
			core.update_qt()
			pos=Position(data,'xml')
			pos_list.append(pos)

def load_from_db():
	global pos_list
	cur = core.db().cursor()
	cur.execute("select data from positions where user_id=? ORDER BY name", (core.user_id(),))
	data_list = cur.fetchall()
	pos_list = []
	for data in data_list:
		pos = Position(data[0], 'json')
		pos_list.append(pos)

def create_html_data():
	for pos in pos_list:
		pos.create_html_data()

def create_index_page():
	global pos_list,collasped_list
	if status.reload_positions():
		load_from_site()

	# setup output class
	out = tree.Output('../images/',core.data['colour'])
	out.add_script_file('../tree.js')
	out.add_script_file('../phoenix.js')
	out.add_css_file('./tree.css')
	out.add_css_file('./main.css')
	out.add_css_file('./turns.css')
	out.title = "Phoenix Turns"

	# add tabs
	out.add("<div class='main'>\n")
	out.add("<div class='search_tabs'>\n")
	on = ' on'
	for i, (k, v) in enumerate(Position.search_types.items()):
		out.add("<div id='search_tab_"+str(k)+"' class='search_tab"+on+"' onmouseup='activate_tab("+str(k)+")'>"+v+"</div>\n")
		if i == 0:
			on=''
	out.add("</div><div style='height:5px;'></div>\n")

	# render trees
	create_html_data() # create html sections for postions in list
	on = ''
	for i,(k,v) in enumerate(Position.search_types.items()):
		out.add("<div id='data_"+str(k)+"' style='display:"+on+"' class='search_data'>\n")
		construct_tree(out,int(k))
		out.add("</div>\n")
		if i == 0:
			on='none'
	out.add("</div>\n")
	f = open(core.data_path() + 'index.html', 'w')
	f.write(out.html())
	f.close()

def construct_tree(out,user_search=Position.PST_POSITION):
	sort_list(user_search)
	t = tree.TreeControl(True, False)
	t.setup(core.data['colour'], 160, user_search, 'std', True)
	body = t.create(pos_list,cat_list, collasped_cats, closed_list=[])
	out.add(body)

if __name__ == '__main__':
	load_from_site()
	create_index_page()
else:
	load_from_db()

