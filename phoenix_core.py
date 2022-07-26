import os 
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as et
import sqlite3 as sql

version=0.0
last_error=''
data=None
class phoenix_core_wrapper:
    def __init__(self):
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.target_path = self.current_path + '/data/'
        if not os.path.exists(self.target_path):
            os.makedirs(self.target_path)
        self.position_path = self.target_path + 'positions/'
        if not os.path.exists(self.position_path):
            os.makedirs(self.position_path)
        self.config_name = self.target_path + 'config.json'
        self.db_name = self.target_path + 'phoenix.db'
        self.db_con=sql.connect(self.db_name)

        # setup data held by core
        self.load()
        self.create_db() # after load()
        self.update()

    def create_db(self):
        global data
        cur = self.db_con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name text)')
        cur.execute('CREATE TABLE IF NOT EXISTS positions (id INTEGER, user_id INTEGER,name Text, last_turn INTEGER,type Text,system Text,data TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS pos_list (pos_id INTEGER, day INTEGER)')
        self.update_users()

    def update_users(self):
        cur = self.db_con.cursor()
        for user in data['users']:
            cur.execute("SELECT * FROM users WHERE  name= '%s'" % user)
            db_user=cur.fetchall()
            if len(db_user)==0:
                cur.execute("INSERT INTO users (name) VALUES ('%s')" % user)
            self.db_con.commit()

    def find_user_id(self,user):
        cur = self.db_con.cursor()
        cur.execute("SELECT * FROM users WHERE  name= '%s'" % user)
        db_user = cur.fetchone()
        if db_user!=None:
            return db_user[0]
        cur.execute("INSERT INTO users (name) VALUES ('%s')" % user)
        self.db_con.commit()
        return self.find_user_id(user)

    def update(self):
        global version
        if float(data['version'])>=version:
            return
        # do version changes


        # save
        data['version']=version
        self.save()

    def load(self):
        global data,version
        if data == None:
            data = {}
            read_data = ''
            if os.path.exists(self.config_name):
                with open(self.config_name) as f:
                    read_data = f.read()
                    data = json.loads(read_data)
                    f.close()
            if 'positions' not in data:
                data['positions'] = {}
            if 'last_download' not in data:
                data['last_download'] = -1
            if 'year_start' not in data:
                data['year_start'] = [0, 265, 525, 785, 1045, 1305, 1565, 1830, 2090, 2350, 2615, 2875, 3135, 3395,
                                      3655, 3920, 4180, 4440, 4700, 4965, 5225]
            if 'users' not in data:
                data['users'] = {}
            if 'current_user' not in data:
                data['current_user'] = 'None'
            if 'version' not in data:
                data['version'] = version

    def save(self):
        global data
        ##backup file when it changes and only allow none zero configs
        if len(data) > 0:
            if os.path.exists(self.config_name):
                os.replace(self.config_name, self.target_path + 'config.bak')
            f = open(self.config_name, 'w')
            f.write(json.dumps(data))
            f.close()

    def __del__(self):
        self.db_con.close()

pcw=phoenix_core_wrapper()

## functions that use wrapper class
def save():
    pcw.save()
def db():
    return pcw.db_con

## funtion that work on data only
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
        try:
            tree = et.parse(response)
        except:
            return False
        root = tree.getroot()
        uid=0
        code=''
        for child in root:
            if child.tag == 'user_id':
                uid=int(child.text)
            if child.tag == 'code':
                code = child.text
        if uid>0 and code!='':
            id=pcw.find_user_id(user)
            data['users'][user]={'user_id':id,'site_id':uid,'code':code}
            data['current_user']=user
            save()
            return True
    return False
def has_user():
    global data
    if 'current_user' in data:
        if site_id()>0 and user_code()!='':
            return True
    return False

def user_position_path():
    global data
    return pcw.position_path + data['current_user']+'/'
def data_path():
    return pcw.target_path

def set_current_user(user):
    global data
    if user != data['current_user']:
        if user in data['users']:
            data['current_user']=user
            data['last_download'] = -1
            save()
            if not os.path.exists(user_position_path()):
                os.makedirs(user_position_path())
            return True
    return False

def user_id():
    global data
    if 'current_user' in data:
        if data['current_user'] in data['users']:
            user=data['users'][data['current_user']]
            if 'user_id' in user:
                return user['user_id']
    return 0
def site_id():
    global data
    if 'current_user' in data:
        if data['current_user'] in data['users']:
            user=data['users'][data['current_user']]
            if 'site_id' in user:
                return user['site_id']
    return 0
def user_code():
    global data
    if 'current_user' in data:
        if data['current_user'] in data['users']:
            user=data['users'][data['current_user']]
            if 'code' in user:
                return user['code']
    return ''
def phoenix_request(request_type):
    if has_user():
        return urllib.request.Request('https://www.phoenixbse.com/index.php?a=xml&sa=' +request_type+'&uid=' + str(site_id()) + '&code=' + user_code())
    return None
