import os
import sys
import json

class TreeControl:
	def __init__(self,default_open_cat=True,default_open_data=True):
		self.id=0
		self.use_desc=True
		self.t_cat="class='t_cat'"
		self.t_d_s="class='t_d_s'"
		self.t_data_style=""
		self.t_c_x="class='t_c_x'"
		self.t_c_n="class='t_c_n'"
		self.t_d_n_collaspsed="class='t_d_n'"
		self.cat_expander="images/neg.gif"
		self.default_open_data=default_open_data
		self.default_open_cat=default_open_cat

	def setup(self,colour='blue',width=200,id=0,style='std',use_desc=True):

		self.current_colour=colour
		self.id=id
		self.use_desc=use_desc
		self.t_cat="class='t_cat'"
		self.t_d_s="class='t_d_s'"
		self.t_c_n="class='t_c_n'"
		self.t_d_n_collaspsed="class='t_d_n'"
		self.t_d_n = "class='t_d_n'"
		self.t_data_style="margin-left:"+str(width)+"px;"
		self.cat_expander="images/neg.gif"

		if style=='clear':
			self.t_cat="class='t_catc'"
			self.t_d_s="class='t_d_sc'"
			self.t_c_n+=" style='float:right;margin-right:4px;'"
			self.t_d_n_collaspsed="class='t_d_n2'"
			self.t_d_n = "class='t_d_n2'"
		self.t_cat+=" style='width:"+str(width)+"px'"
		self.t_c_x="class='t_d_x'"

	#######################################################
	## uses $list of format
	## n => {'id'		=> unique id,
	##		 'cat_id'	=> references cat_types ,
	##		 'name'		=> name of each data ,
	##		 'html' => html expandable under data
	##       }
	#######################################################

	def create(self,data_list,cat_types,collasped_cats=[],closed_list=[]):
		last_cat=-1
		s=''
		size=len(data_list)
		for k, data in enumerate(data_list):
			## determin next catagory
			next_cat=-2
			if k+1<size:
				next_cat=int(data_list[k+1]['cat_id'])
			cat_id=int(data['cat_id'])
			if last_cat!=cat_id:
				## close last element + data
				if last_cat!=-1:
					s+="	</div>\n</div>\n"
				## set last cast
				last_cat=cat_id
				## open element
				(open,closed,expander)=self.open_state(closed_list,True,cat_id)
				cat_type='Unknown'
				if cat_id in cat_types:
					cat_type=cat_types[cat_id]
				cat_collasped=''
				if cat_id in collasped_cats:
					cat_collasped=collasped_cats[cat_id]

				s+="<div class='t_element'>\n"\
					"	<div "+self.t_cat+">\n"\
					"		<img "+self.t_c_x+" onclick='tree_toggle_cat(this,"+str(cat_id)+","+str(self.id)+")'  src='./"+expander+"'/>\n"\
					"		<div "+self.t_c_n+">"+str(cat_type)+"</div>\n"\
					"	</div> \n"\
					"	<div class='t_data' id='t_"+str(self.id)+"_c_"+str(cat_id)+"' style='"+self.t_data_style+closed+"'>\n"\
					"		<div "+self.t_d_s+"><img class='t_d_t' src='images/tree_3.gif'/><div "+self.t_d_n_collaspsed+">"+cat_collasped+"</div></div>\n"\
					"	</div>\n"\
					"	<div class='t_data' id='t_"+str(self.id)+"_o_"+str(cat_id)+"' style='"+self.t_data_style+open+"'>\n"
				if next_cat==cat_id:
					s+="		<div "+self.t_d_s+"><div class='t_d_vlt'></div><img class='t_d_t' src='images/tree_1.gif'/>\n"
				else:
					s+="		<div "+self.t_d_s+"><img class='t_d_t' src='images/tree_3.gif'/>\n"
			else:
				if next_cat==cat_id:
					s+="		<div "+self.t_d_s+"><div class='t_d_vl'></div><img class='t_d_t2' src='images/tree_0.gif'/>\n"
				else:
					s+="		<div "+self.t_d_s+"><div class='t_d_vlb'></div>" \
					    "		<img class='t_d_t2' src='images/tree_2.gif'/>\n"
			## write name of data - can contain extra info
			(open,closed,expander)=self.open_state(closed_list,False,data['id'])
			# either use name or ext_name if it exists
			name=data['name']
			if 'ext_name' in data:
				name = data['ext_name']
			if self.use_desc:
				s+="			<img class='t_d_xl' onclick='tree_toggle_data(this,"+str(data['id'])+","+str(self.id)+")' src='"+expander+"'/>\n"\
					"			<div "+self.t_d_n+">"+name+"</div>\n"
			else:
				s+="			<div "+self.t_d_n+">"+name+"</div>\n"
			s+="		</div>\n"
			## insert description if used
			if self.use_desc and 'html' in data:
				s+="		<div class='t_xd_s' style='"+open+"' id='t_"+str(self.id)+"_d_"+data['id']+"'>\n";
				## write a vertical line if ther eis another elemnt in catagory
				if next_cat==cat_id:
					s+="		<div class='t_xd_vl'> </div>\n"
				## write data decription
				s+="			<div class='t_xd_n'>"+data['html']+"</div>\n"\
					"		</div>\n"
		## close last element
		if last_cat!=-1:
			s+="	</div>\n</div>\n"
		return s

	def open_state(self,closed_list,cat,id):
		is_open=self.default_open_data
		type='d'
		if cat==True:
			is_open=self.default_open_cat
			type = 'c'

		if self.id in closed_list:
			if type in closed_list[self.id]:
				if id in closed_list[self.id][type]:
					is_open=not is_open

		open =';display:none'
		closed=''
		expander='images/pos.gif'
		if is_open==True:
			open =''
			closed = ';display:none'
			expander='images/neg.gif'

		return (open,closed,expander)


""" may niot need
	## closed list was passed as reference - issue ?
	def update_open(self,closed_list,did,cid,tid,open):
		## if open then we store nothing - otehrwise tehre is an array entry
		## decide if we are using cat or data
		type='c'
		id=cid
		if did!=-1:
			type='d'
			id=did
		elif cid==-1:
			return ## one needs to be set

		## make sure its typed as bool
		if type=='c':
			if open:
				open=self.default_open_cat
			else:
				open = not self.default_open_cat
		else:
			if open:
				open=self.default_open_data
			else:
				open = not self.default_open_data

		## create top if it does nto exist
		if tid not in closed_list:
			if open==True:
				return
			closed_list[tid]=[]  ### going to fail
		## create second levle if needed
		if type not in closed_list[tid]:
			if open==True:
				return
			closed_list[tid][type]=[]
		if id not in closed_list[tid][type]:
			if open==False:
				closed_list[tid][type][id]=1
		else:
			if open==True:
				del closed_list[tid][type][id]
		## clear out lists if empty
		if len(closed_list[tid][type])==0:
			del closed_list[tid][type]
		if len(closed_list[tid])==0:
			del closed_list[tid]
		return
"""
class Output():
	VERSION = "1.0"  # can change later
	def __init__(self,path,colour,config_path):
		self.body=''
		self.style=''
		self.colour_scheme=None
		self.colour=colour
		self.config_path = config_path
		self.load_colours()
		self.script=''
		self.script_file=''
		self.css_file=''
		self.script_file_list=[]
		self.css_file_list=[]
		self.image_path = path+self.colour+"/"
		self.title=''

	def convert_file(self,src,dest):
		read_data=None
		if os.path.exists(src):
			with open(src) as f:
				read_data = f.read()
				f.close()
				read_data =self.colour_replace(read_data)
		if read_data!=None:
			with open(dest,'w') as f:
				f.write(read_data)
				f.close()

	def load_colours(self):
		file = self.config_path+'/colour_scheme.json'
		if os.path.exists(file):
			with open(file) as f:
				read_data = f.read()
				self.colour_scheme = json.loads(read_data)
				f.close()

	def add_css_file(self,file):
		if file not in self.css_file_list:
			self.css_file+="<link href='"+file+"?v="+Output.VERSION+"' rel='stylesheet' type='text/css' media='all'>\n"
			self.css_file_list.append(file)

	def add_script_file(self,file):
		## single add
		if file not in self.script_file_list:
			self.script_file+="<script type='text/javascript' src='"+file+"?v="+Output.VERSION+"'></script>\n"
			self.script_file_list.append(file)

	def colour_replace(self,text):
		cs=self.colour_scheme[self.colour]
		for i,(k,v) in enumerate(cs.items()):
			text = text.replace(k, v)
		return text.replace("images/", self.image_path)

	def add_style(self,style):
		self.style+=self.colour_replace(style)
	def add_script(self,script):
		self.script+=self.colour_replace(script)
	def add(self,body):
		self.body+=self.colour_replace(body)
	def html(self):
		s = "<html>\n<header>\n"
		if self.title!='':
			s+="<title>"+self.title+"</title>\n"
		s +=self.css_file
		s += self.script_file
		s += "<style type='text/css'>\n"+self.style+"</style>\n"
		s += "<script type='text/javascript'>\n" + self.script + "</script>\n"
		s += "</header>\n<body>\n"
		s +=self.body
		s +="</body></html>"
		return s

if __name__ == '__main__':
	out=Output('../images/')
	out.add_script_file('../tree.js')
	out.add_css_file('../tree.css')
	out.title="Phoenix Turns"
	t=TreeControl(True,False)
	t.setup('blue',120,0, 'std', True)
	## n => {'id'		=> unique id,
	##		 'cat_id'	=> references cat_types ,
	##		 'name'		=> name of each data ,
	##		 'html' 	=> html expandable under data
	##       }
	tmp =[]
	cat_types = {0:'One',1:'Two',2:'Three'}
	data_list=[{'id':'1','cat_id':0,'name':'first','html':'o'},
			  {'id': '2', 'cat_id': 0, 'name': 'second', 'html': 'o'},
			 {'id': '3', 'cat_id': 1, 'name': 'third', 'html': 'o'},
			 {'id': '4', 'cat_id': 1, 'name': 'fourth', 'html': 'o'},
			{'id':'5','cat_id':2,'name':'fifth','html':'o'}]
	last_type = -1
	cnt = 0
	collasped_cats = {0:'a',1:'b',2:'c'}

	body=t.create(data_list, cat_types, collasped_cats, closed_list=[])
	out.add_style(t.style)
	out.add(body)
	f = open(os.path.dirname(os.path.realpath(__file__)) + '/data/index.html', 'w')
	f.write(out.html())
	f.close()