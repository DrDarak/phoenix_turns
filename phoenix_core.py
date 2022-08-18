import os
import sys
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as et
import sqlite3 as sql
import tree
from PyQt5 import QtWidgets, QtCore
from distutils.dir_util import copy_tree
import winreg
import time


version=0.0
last_error=''
data=None
class phoenix_core_wrapper:
    blank_actions= {'info_data': 0,
                    'order_data': 0,
                    'pos_list': 0,
                    'game_status': 0,  # unix time game_status updated
                    'notes': 0,
                    'items': 0,
                    'systems': 0,
                    'upload_time': 0}# unix time when site updated

    def __init__(self):
        self.install_path=None
        try:
            registry_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, 'SOFTWARE\Skeletal\PhoenixTurns')
            (self.install_path, k) = winreg.QueryValueEx(registry_key, 'Path')
            winreg.CloseKey(registry_key)
        except:
            if not getattr(sys, "frozen", False):
                self.install_path =os.path.dirname(__file__)
        if self.install_path and len(self.install_path)>10: # add slash if there is a signican path - don't create route path
            self.install_path+="/"
        self.target_path = os.path.expanduser('~/AppData/Local/phoenix_turns/')
        if not os.path.exists(self.target_path):
            os.makedirs(self.target_path)
        self.position_path = self.target_path + 'positions/'
        if not os.path.exists(self.position_path):
            os.makedirs(self.position_path)
        self.config_name = self.target_path + 'config.json'
        self.db_name = self.target_path + 'phoenix.db'
        self.db_con=sql.connect(self.db_name,isolation_level='EXCLUSIVE')
        self.use_qt=False
        # setup data held by core
        self.load()
        self.create_db()  # after load()
        self.update_data()
        self.set_colour()

    def set_colour(self):
        global data
        out=tree.Output('images/',data['colour'],self.install_path)
        out.convert_file(self.install_path+'turns.css',self.target_path+'turns.css')
        out.convert_file(self.install_path + 'tree.css', self.target_path + 'tree.css')
        out.convert_file(self.install_path + 'main.css', self.target_path + 'main.css')

        # create image directory
        src=self.install_path+'/images'
        dest=self.target_path+'/images'
        if not os.path.exists(dest):
            copy_tree(src,dest)

    def create_db(self):
        global data
        cur = self.db_con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name text)')
        cur.execute('CREATE TABLE IF NOT EXISTS positions (id INTEGER, user_id INTEGER,name Text, last_turn INTEGER,type Text,system Text,data TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS turns (pos_id INTEGER,file_name TEXT, user_id INTEGER,day INTEGER,downloaded INTEGER)')
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

    def update_data(self):
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

            if 'year_start' not in data:
                data['year_start'] = [0, 265, 525, 785, 1045, 1305, 1565, 1830, 2090, 2350, 2615, 2875, 3135, 3395,
                                      3655, 3920, 4180, 4440, 4700, 4965, 5225]
            if 'users' not in data:
                data['users'] = {}
            if 'current_user' not in data:
                data['current_user'] = 'None'
            if 'version' not in data:
                data['version'] = version
            if 'colour' not in data:
                data['colour'] = 'blue'
            if 'last_actions' not in data:
                data['last_actions']=phoenix_core_wrapper.blank_actions
            # reload game status on every restart
            data['last_actions']['game_status'] =0

    def save(self):
        global data
        # backup file when it changes and only allow none zero configs
        if len(data) > 0:
            if os.path.exists(self.config_name):
                os.replace(self.config_name, self.target_path + 'config.bak')
            f = open(self.config_name, 'w')
            f.write(json.dumps(data))
            f.close()

    def __del__(self):
        self.db_con.close()

    def update_qt(self):
        if self.use_qt:
            QtWidgets.qApp.processEvents(QtCore.QEventLoop.AllEvents,50)  # process events for app so it does not freeze in the loop
    def log_request(self,request_type):
        with open(self.target_path +"log.txt", 'a') as f:
            s=time.strftime("%d/%m/%y %H:%M:%S")+" - "+request_type+"\n"
            f.write(s)
            f.close()


pcw=phoenix_core_wrapper()

## functions that use wrapper class
def save():
    pcw.save()
def db():
    return pcw.db_con
def db_name():
    return pcw.db_name
def update_qt():
    pcw.update_qt()
def use_qt():
    pcw.use_qt=True
def install_path():
    return pcw.install_path
def set_colour(colour):
    data['colour']=colour
    pcw.set_colour()
    pcw.save()

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

def turn_path(name,pos_id,turn_day,relative=False):
    file_name= sanitize_string(name + ' (' + str(pos_id) + ')'+'.html')
    if relative:
        return './positions/'+data['current_user'] + '/' + str(turn_day) + '/'+ file_name
    day_path = user_position_path() + str(turn_day) + '/'
    if not os.path.exists(day_path):
        os.makedirs(day_path)
    return day_path + file_name

def set_current_user(user):
    global data
    if user != data['current_user']:
        if user in data['users']:
            data['current_user']=user
            data['last_actions'] = phoenix_core_wrapper.blank_actions # reset actions for user
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
        pcw.log_request(request_type)
        return urllib.request.Request('https://www.phoenixbse.com/index.php?a=xml&sa=' +request_type+'&uid=' + str(site_id()) + '&code=' + user_code())


    return None

def year(day):
    for i,year_start in enumerate(reversed(data['year_start'])):
        if day>=year_start:
            y=len(data['year_start'])-i+201
            return y

def date(day,add_year=False):
    global data
    year_start=0
    for i in reversed(data['year_start']):
        if day>=i:
            year_start=i
            break

    d=day-year_start
    week=d
    week=int(week/5)
    d-=week*5
    week+=1
    d+=1
    s=str(week) +"."+str(d)
    if add_year:
        return str(year(day)) + '.' +s
    return

def sanitize_string(value):
    import re
    value = value.encode('ascii', 'ignore').decode('ascii', 'ignore')
    value =re.sub("[^\\w\\s.()-]", "", value).strip()
    return value



if __name__ == '__main__':
    print(pcw.target_path)
    print(pcw.install_path)