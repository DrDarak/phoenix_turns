import html2txt
import re
import os
import json
import phoenix_core as core

def strip_officers(turn_data,pos_id):
    raw_txt=html2txt.turn_to_raw_txt(turn_data)
    res = re.search(r"OFFICERS(.*?)(CREW|Cargo Report|Inventory|SCIENTISTS)", raw_txt, re.MULTILINE)
    if res != None:
        data = res.groups(0)[0]
        print(res.groups(0))
        officers = re.findall(r"1 ([^{]*){([^}]*)", data)
        for entry in officers:
            officer=Officer(entry,pos_id)

def Officer():
    def __init__(self,entry,pos_id):
        if type == 'raw':
            self.create_from_raw(entry,pos_id)
            self.update()
        else:
            self.set_data(data)
        self.sort = ''

    def __getitem__(self, index):
        return self.data[index]
    def __setitem__(self, index, item):
        self.data[index] = item
    def __contains__(self, item):
        return item in self.data

    def create_from_raw(self,entry,pos_id):
        self.data['name']=entry[0].strip()
        skills = entry[1].strip().split(",")
        free_pts = 0
        remove_index = -1
        for i, skill in enumerate(skills):
            skill = skill.strip()
            skills[i] = skill
            find_pts = re.match(r"(\d+) Pts", skill)
            if find_pts:
                free_pts = int(find_pts.group(1))
                remove_index = i
        if remove_index >= 0:
            del skills[remove_index]
        self.data['id']=0
        self.data['xp']=free_pts
        self.data['skills']=skills
        self.data['pos_id']=pos_id
        self.update()

    def update(self):
        cur = core.db().cursor()
        # write officer to db
        if self.find() == None:
            query = (self.data['pos_id'], core.user_id(), self.data['xp'], self.data['data'])
            cur.execute("insert into positions SET id=0, pos_id=?, user_id=?, xp=?, data=?", query)
        else:
            query = (self.data['xp'], self.data['data'],self.data['id'])
            cur.execute("update positions SET xp=?,data=? where id=?",query)
        core.db().commit()

if __name__ == '__main__':
    current_path = os.path.dirname(os.path.realpath(__file__))
    target_path = current_path + '/data/12345.html'
    read_data = ''
    with open(target_path) as f:
        read_data = f.read()
        f.close()
    data = strip_officers(read_data)
