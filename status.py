import phoenix_core as core
import urllib.request
import urllib.error
import xml.etree.ElementTree as et

data = {'last_upload':0}
last_error=''
def load():
    global last_error
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

if __name__ == '__main__':
    load()