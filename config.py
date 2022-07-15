import os 
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as et

## global data that just need to be stored in module for later use
last_error=''
data=None
current_path = os.path.dirname(os.path.realpath(__file__))
target_path=current_path+'/data/'
if not os.path.exists(target_path):
    os.makedirs(target_path)
position_path=target_path+'positions/'
if not os.path.exists(position_path):
    os.makedirs(position_path)
config_name=target_path+'config.json'

## load data from config
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
        if 'last_download' not in data:
            data['last_download'] = -1
        if 'year_start' not in data:
            data['year_start'] = [0, 265, 525, 785, 1045, 1305, 1565, 1830, 2090, 2350, 2615, 2875, 3135, 3395, 3655, 3920, 4180, 4440, 4700, 4965, 5225]
        if 'users' not in data:
            data['users']={}

## Automatically run load as first action so config is present
load()

## saving state to file
def save():
    global data
    ##backup file when it changes and only allow none zero configs
    if len(data)>0:
        if os.path.getsize(config_name)>0:
            os.replace(config_name,target_path+'config.bak')
        f = open(config_name, 'w')
        f.write(json.dumps(data))
        f.close()

def login(user,password):
    global data,last_error
    payload = {
        'Action': 'login',
        'UserName': user,
        'PassWord': password
    }
    url='https://www.phoenixbse.com/index.php?a=xml_login'
    payload_data = urllib.parse.urlencode(payload).encode()
    req  = urllib.request.Request(url, payload_data)
    response = None
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        last_error = e.reason
    if response != None:
        tree = et.parse(response)
        root = tree.getroot()
        uid=0
        code=''
        for child in root:
            if child.tag == 'user_id':
                uid=int(child.text)
            if child.tag == 'code':
                code = child.text
        if uid>0 and code!='':
            data['users'][user]={'user_id':uid,'code':code}
            save()

def has_user():
    global data
    if 'current_user' in data:
        if user_id()>0 and user_code()!='':
            return True
    return False

def user_id():
    if 'current_user' in data:
        if data['current_user'] in data['users']:
            user=data['users'][data['current_user']]
            if 'user_id' in user:
                return user['user_id']
def user_code():
    if 'current_user' in data:
        if data['current_user'] in data['users']:
            user=data['users'][data['current_user']]
            if 'code' in user:
                return user['code']

def phoenix_request(request_type):
    if has_user():
        return urllib.request.Request('https://www.phoenixbse.com/index.php?a=xml&sa=' +request_type+'&uid=' + str(user_id()) + '&code=' + user_code())
    return None