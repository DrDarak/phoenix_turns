import phoenix_core as core
import status
import positions as pos
import urllib.request
import urllib.error
import sqlite3 as sql
import os
from PyQt5.QtWidgets import QProgressBar

last_error=''

def download_turn(name,pos_id,turn_day):
    global db_con
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
        if data !="":
            # write file to correct location
            f = open(core.turn_path(name,pos_id,turn_day), 'w')
            f.write(str(data, 'utf-8', 'ignore'))
            f.close()
            # record as downloaded
            cur = db_con.cursor()
            cur.execute("update turns set downloaded=? where user_id=? and pos_id=? and day=?", (1,core.user_id(),pos_id,turn_day))
            db_con.commit()
db_con=None
def load(progress=None,finished=None):
    global last_error,db_con
    db_con = sql.connect(core.db_name())
    cur = db_con.cursor()
    ## only update if we have not tried already today.
    cur.execute("select file_name,pos_id,day from turns where user_id=? and downloaded=?",(core.user_id(),0))
    turn_list = cur.fetchall()

    ## do download
    if progress:
        progress.setRange(0, len(turn_list)+1)
        progress.setProperty("value", 0)
    cnt = 0
    ## do download
    for turn in turn_list:
        download_turn(turn[0],turn[1],turn[2])
        if progress:
            progress.setProperty("value", cnt)
            cnt+=1
    if progress:
        progress.setProperty("value", cnt)
    db_con.close()
    db_con = None
    if finished:
        finished()

if __name__ == '__main__':
    load()