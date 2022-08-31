import phoenix_core as core
import urllib.request
import urllib.error
import sqlite3 as sql
import os
from PyQt5.QtWidgets import QProgressBar
import re
import html2txt

last_error=''
def  process_turn(data):
    css="""<header>
        <link href='../../../main.css' rel='stylesheet' type='text/css' media='all'>
        <link href='../../../turns.css' rel='stylesheet' type='text/css' media='all'>\n</header>\n"""
    data=re.sub(r"<style type='text/css'>((.|\n)*?)</style>", css, str(data, 'utf-8', 'ignore'))
    return re.sub("style='border:1px solid #345487;border-radius:8px;'", "class='turn_body'", data)

def download_turn(name,pos_id,turn_day):
    global last_error
    req = core.phoenix_request('turn_data&tid=' + str(pos_id))
    if req != None:
        response = None
        data=""
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.URLError as e:
            last_error = e.reason
        if response != None:
            data=response.read()
            data=process_turn(data)
        if data !="":
            # write file to correct location
            f = open(core.turn_path(name,pos_id,turn_day), 'w')
            f.write(data)
            f.close()
            # record as downloaded
            cur = core.db().cursor()
            cur.execute("update turns set downloaded=? where user_id=? and pos_id=? and day=?", (1,core.user_id(),pos_id,turn_day))
            core.db().commit()

def download(progress=None):
    cur = core.db().cursor()
    ## only update if we have not tried already today.
    cur.execute("select file_name,pos_id,day from turns where user_id=? and downloaded=?",(core.user_id(),0))
    turn_list = cur.fetchall()

    ## do download
    if progress:
        progress.setRange(0, len(turn_list))
        progress.setProperty("value", 0) # use set property since it does not call a immediate render (safer)
    cnt = 0
    ## do download
    for turn in turn_list:
        download_turn(turn[0],turn[1],turn[2])
        core.update_qt()
        if progress:
            cnt += 1
            progress.setProperty("value", cnt)
    if progress:
        progress.setProperty("value", cnt)

def update_text_turn(name,pos_id,turn_day):
    file_name=core.turn_path(name, pos_id, turn_day)
    file_data='Failed'
    if os.path.exists(file_name):
        with open(file_name) as f:
            read_data = f.read()
            file_data=html2txt.turn_to_raw_txt(read_data)
            f.close()
    cur = core.db().cursor()
    cur.execute("update turns set data=? where user_id=? and pos_id=? and day=?",
                (file_data, core.user_id(), pos_id, turn_day))
    core.db().commit()

def update_text(progress=None):
    cur = core.db().cursor()
    cur.execute("select file_name,pos_id,day from turns where user_id=? and downloaded=? and data=?", (core.user_id(), 1,''))
    turn_list = cur.fetchall()
    ## do text conversion
    if progress:
        progress.setRange(0, len(turn_list))
        progress.setProperty("value", 0)
    cnt = 0
    ## do conversion
    for turn in turn_list:
        update_text_turn(turn[0],turn[1],turn[2])
        core.update_qt()
        if progress:
            cnt += 1
            progress.setProperty("value", cnt)
    if progress:
        progress.setProperty("value", cnt)

def update():
    global last_error
    cur = core.db().cursor()
    cur.execute("select count(1) from turns where user_id=? and downloaded=?",(core.user_id(),0))
    turn_cnt = cur.fetchone()
    if turn_cnt and turn_cnt[0]>0:
        download()

    cur.execute("select count(1) from turns where user_id=? and downloaded=? and data=?",(core.user_id(),1,''))
    turn_cnt = cur.fetchone()
    if turn_cnt and turn_cnt[0] > 0:
        update_text()

if __name__ == '__main__':
    update()