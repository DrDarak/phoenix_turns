import phoenix_core as core
import positions
import urllib.request
import urllib.error
import xml.etree.ElementTree as et
import time
from datetime import datetime

data = {'last_upload':0}
last_error=''
# use overide to make download turns work now
def load(override=False):
    global last_error
    # only refresh every hr until 20 hrs has passed from upload and on weekdays
    update_time = 3600
    if core.data['last_actions']['upload_time']+3600*20< time.time() and datetime.today().weekday()<5:
        update_time=600

    # Always loads first time in as game_status is zeroed on init
    if core.data['last_actions']['game_status']+update_time < time.time() or override==True:
        core.data['last_actions']['game_status'] = int(time.time())
        core.save()
        req= core.phoenix_request('game_status')
        if req!=None:
            xml_data=None
            try:
                xml_data=urllib.request.urlopen(req)
            except urllib.error.URLError as e:
                last_error=e.reason
            if xml_data!=None:
                process_data(xml_data)

def process_data(xml_data):
    global data
    tree = et.parse(xml_data)
    root = tree.getroot()
    has_data=False
    for child in root:
        if child.tag == 'game_status':
            has_data=True
            for status in child:
                data[status.tag] = status.text
            break
    if has_data:
        if 'current_day' in data:
            data['current_day']=int(data['current_day'])
        if 'turns_uploaded' in data:
            turns_uploaded=int(data['turns_uploaded'])
            if  turns_uploaded>0:
                data['last_upload']=data['current_day']
            else:
                data['last_upload'] =data['current_day']-1
        if 'year_start' in data:
            year_start=int(data['year_start'])
            if year_start not in core.data['year_start']:
                core.data['year_start'].append(year_start)
                core.save()
        if data['last_upload'] > core.data['last_actions']['pos_list']:
            if positions.load_from_site():
                core.data['last_actions']['pos_list'] = data['current_day']
                core.data['last_actions']['upload_time']=int(time.time())
                core.save()

def current_day():
    if check_loaded():
        return data['current_day']
    return 0
def check_loaded():
    global data
    if 'year_start' not in data:
        load()
    if 'year_start' not in data:
        return False
    return True
if __name__ == '__main__':
    load()