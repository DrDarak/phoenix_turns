import phoenix_core as core
import xml.etree.ElementTree as et
import urllib.request
import urllib.error
import json
import sqlite3 as sql

class position:
    def __init__(self,data):
        self.data={'type':'none','system':'none'}
        if data.tag=='position':
            if len(data.items())>0:
                for attrib,val in data.items():
                    self.data[attrib]=val
        for pos_data in data:
            if pos_data.tag=='ship_info':
                self.data['ship_info']={}
                if len(pos_data.items())>0:
                    for attrib,val in pos_data.items():
                        self.data['ship_info'][attrib.lower()]=val
            elif pos_data.tag=='cargo_space':
                self.data['cargo_space']={}
                for cargo in pos_data:  
                    if len(cargo.items())>0:
                        cargo_type='_'
                        for attrib,val in cargo.items():
                            if attrib=='type':
                                cargo_type=val.replace(' ','_').lower()
                        self.data['cargo_space'][cargo_type]={}
                        for attrib,val in cargo.items():
                            if attrib!='type':
                                self.data['cargo_space'][cargo_type][attrib.lower()]=val
            elif pos_data.tag=='turns':
                self.data['turns']=[]
                for turn in pos_data:  
                    if len(turn.items())>0:
                        for attrib,val in turn.items():
                            if attrib=='day':
                                self.data['turns'].append(int(val))
            elif pos_data.tag == 'system_text':
                self.data['system'] = pos_data.text
            else:
                self.data[pos_data.tag]=pos_data.text
        self.update()

    def last_turn(self):
        if 'turns' in self.data and 0 in self.data['turns']:
            return self.data['turns'][0]
        return 0

    def find(self):
        cur = core.db().cursor()
        cur.execute("select * from positions where id=? and user_id=?",(self.data['num'], core.user_id()))
        return cur.fetchone()

    def update(self):
        cur = core.db().cursor()
        if self.find() == None:
            query = (self.data['num'], core.user_id(), self.data['name'],self.last_turn(), self.data['type'], self.data['system'],json.dumps(self.data))
            cur.execute("insert into positions values (?,?,?,?,?,?,?)", query)
        else:
            query = (self.last_turn(), self.data['type'], self.data['name'], self.data['system'], json.dumps(self.data),self.data['num'], core.user_id())
            cur.execute("update positions SET name=?,last_turn=?,type=?,system=?,data=? where id=? and user_id=?",query)
        core.db().commit()
pos_list=[]
last_error=''

def load():
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

def process_data(xml_data):
    global pos_list
    tree = et.parse(xml_data)
    root = tree.getroot()
    for child in root:
        for data in child:
            pos=position(data)
            pos_list.append(pos)

def create_index_page():
    body=''
    output='<html><header><title>Phoenix Turns</title></header><body>'+body+'</body></html>'
    f = open(core.data_path() + 'index.html', 'w')
    f.write(output)
    f.close()

if __name__ == '__main__':
    load()