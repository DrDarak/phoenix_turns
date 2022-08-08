import phoenix_core as core
import status
import positions as pos
import urllib.request
import urllib.error
import os
from PyQt5.QtWidgets import QProgressBar

last_error=''

def download_turn(pos_id,turn_day):
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
            f = open(core.turn_path(pos_id,turn_day), 'w')
            f.write(str(data, 'utf-8', 'ignore'))
            f.close()
            # record as downloaded
            cur = core.db().cursor()
            cur.execute("update turns set downloaded=? where user_id=? and pos_id=? and day=?", (1,core.user_id(),pos_id,turn_day))
            core.db().commit()

def load(progress=None,finished=None):
    global last_error
    cur = core.db().cursor()
    ## only update if we have not tried already today.
    cur.execute("select pos_id,day from turns where user_id=? and downloaded=?",(core.user_id(),0))
    turn_list = cur.fetchall()

    ## do download
    if progress:
        progress.setRange(0, len(turn_list))
        progress.setProperty("value", 0)
    cnt = 0
    ## do download
    for turn in turn_list:
        download_turn(turn[0],turn[1])
        if progress:
            progress.setProperty("value", cnt)
            cnt+=1
    # after turns downloaded update index
    pos.update_index()
    if finished:
        finished()

if __name__ == '__main__':
    load()