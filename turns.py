import phoenix_core as core
import urllib.request
import urllib.error
import sqlite3 as sql
import os
from PyQt5.QtWidgets import QProgressBar
import re

last_error=''
def  process_turn(data):
    css="""<header>
        <link href='../../../main.css' rel='stylesheet' type='text/css' media='all'>
        <link href='../../../turns.css' rel='stylesheet' type='text/css' media='all'>\n</header>\n"""
    data=re.sub(r"<style type='text/css'>((.|\n)*?)</style>", css, str(data, 'utf-8', 'ignore'))
    return re.sub("style='border:1px solid #345487;border-radius:8px;'", "class='turn_body'", data)

def download_turn(name,pos_id,turn_day):
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

def load(progress=None,finished=None):
    global last_error
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

if __name__ == '__main__':
    load()