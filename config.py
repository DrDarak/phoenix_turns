import os 
import json
import sys

data=None
current_path = os.path.dirname(os.path.realpath(__file__))
target_path=current_path+'/data/'
if not os.path.exists(target_path):
    os.makedirs(target_path)
position_path=target_path+'positions/'
if not os.path.exists(position_path):
    os.makedirs(position_path)
config_name=target_path+'config.json'

def load():
    global data
    if data==None:
        data={}
        read_data=''
        if os.path.exists(config_name):
            with open(config_name) as f:
                read_data = f.read()
                data=json.loads(read_data)
                f.close()
        if 'positions' not in data:
            data['positions']={}
        if 'user_id' not in data:
            data['user_id']=''
        if 'user_code' not in data:
            data['user_code']=''
        if 'last_download' not in data:
            data['last_download'] = -1
        if 'year_start' not in data:
            data['year_start'] = [0, 265, 525, 785, 1045, 1305, 1565, 1830, 2090, 2350, 2615, 2875, 3135, 3395, 3655, 3920, 4180, 4440, 4700, 4965, 5225]
def save():
    global data
    ##backup file when it changes and only allow none zero configs
    if len(data)>0:
        if os.path.getsize(config_name)>0:
            os.replace(config_name,target_path+'config.bak')
        f = open(config_name, 'w')
        f.write(json.dumps(data))
        f.close()
load()
