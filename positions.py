import config as cfg
import xml.etree.ElementTree as et
import urllib.request
import urllib.error

class position:
    def __init__(self,data):
        self.data={}
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
            else:
                self.data[pos_data.tag]=pos_data.text

pos_list=[]
last_error=''

def load():
    global last_error
    req=cfg.phoenix_request('pos_list')
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

if __name__ == '__main__':
    load()