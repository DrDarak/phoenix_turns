import phoenix_core as core
import status
import positions as pos
import urllib.request
import urllib.error
import os
from PyQt5.QtWidgets import QProgressBar

last_error=''
def load(progress=None,finished=None):
    global last_error
    ## only update if we have not tried already today.
    status.load()
    if status.data['last_upload']>core.data['last_download']:
        core.data['last_download']=status.data['current_day']
        ## do download
        pos.load()
        if progress:
            progress.setRange(0,len(pos.pos_list))
            progress.setProperty("value", 0)
        cnt=0
        for p in pos.pos_list:
            last_turn=0
            if p.data['num'] in core.data['positions']:
                last_turn=int(core.data['positions'][p.data['num']])
            turn_day=0
            if 'turns' in p.data and p.data['turns'][0]:
                turn_day=p.data['turns'][0]
            # download file if there is a new one
            if turn_day>last_turn:
                req = core.phoenix_request('turn_data&tid='+p.data['num'])
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
                        # create directory tree
                        day_path=core.user_position_path()+str(turn_day)+'/'
                        if not os.path.exists(day_path):
                            os.makedirs(day_path)
                        f = open(day_path+p.data['num']+'.html', 'w')
                        # save downloaded file info
                        core.data['positions'].update({p.data['num']:turn_day})
                        f.write(str(data, 'utf-8', 'ignore'))
                        f.close()
            if progress:
                progress.setProperty("value", cnt)
                cnt+=1
        core.save()
    if finished:
        finished()


if __name__ == '__main__':
    load()