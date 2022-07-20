from html.parser import HTMLParser
import os
import re

current_path = os.path.dirname(os.path.realpath(__file__))
target_path = current_path + '/data/x.html'
read_data=''
with open(target_path) as f:
    read_data = f.read()
    f.close()

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body=False
        self.in_line=False
        self.in_data = False
        self.output=''
        self.lvl=0
        self.cols=[[]]
        self.first_row= False
        self.line_pos = 0
        self.col_pos = -1
        self.row_type=''

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.lvl = 0
        elif tag=='table':
            self.lvl+=1
            if len(self.cols)<=self.lvl:
                self.cols.append([])
            self.first_row = True
        elif tag == 'tr':
            self.in_line = True
            self.col_pos=-1
            self.row_type = ''
        elif tag == 'td':
            self.col_pos+=1
            self.in_data = True
            for a in attrs:
                if a[0]=='style' and self.first_row:
                    res = re.match("width:\s*(\d+)", a[1])
                    if res != None:
                        col = int(int(res.groups(0)[0]) / 1.25 + 0.95) # reverses 100%=>80 lines correctly
                        ## make col pos cumulative
                        col_len=len(self.cols[self.lvl])
                        if col_len>0:
                            col+=self.cols[self.lvl][col_len-1]
                        self.cols[self.lvl].append(col)
                if a[0]=='class':
                    self.row_type = a[1]

    def handle_endtag(self, tag):
        if tag == 'table':
            if self.lvl==2:
                self.output=self.output[:-1] ## Remove trailing \n
            self.lvl -= 1
            if self.lvl>=0:
                print()
                del self.cols[-1]
        elif tag == 'tr':
            self.first_row=False
            self.in_line = False
            self.first_row =False
            self.line_pos=0
            self.output += '\n'
        elif tag == 'td':
            self.in_data = False

    def handle_data(self, data):
        if self.in_data:
            # don't allow any data from html formating to slip in
            data=data.replace("\n", "")

            ## only apply to second columns
            last_col=self.col_pos-1
            add_data=''
            if last_col>=0 and len(self.cols[self.lvl])>last_col:
                last_col_pos=self.cols[self.lvl][last_col]
                if self.line_pos<last_col_pos:
                    for i in range(self.line_pos,last_col_pos):
                        add_data+=' '
            self.output +=add_data
            self.line_pos += len(add_data)

            self.row_type_pre_adjust()

            # add data after columns sorted
            self.output+=data
            self.line_pos+=len(data)

            self.row_type_post_adjust()

    def row_type_pre_adjust(self):
        add_data=''
        if self.line_pos==0:
            if self.row_type=='report_left':
                add_data="|-"
            if self.row_type=='txt_r':
                add_data="| "
        self.output += add_data
        self.line_pos+=len(add_data)

    def row_type_post_adjust(self):
        add_data = ''
        ## if current column is the end column
        if self.col_pos>=0 and len(self.cols[self.lvl])>self.col_pos and \
           self.cols[self.lvl][self.col_pos]>=80:
            if self.row_type=='txt_r':
                add_data=self.complete_report()
        if self.lvl==1:
            if self.row_type == 'report_left':
                if self.line_pos < 80:
                    for i in range(self.line_pos, 79):
                        add_data += "-"
                    add_data += "|"
            ## no columns at lvl 2
            if self.row_type == 'txt_r':
                add_data=self.complete_report()

        self.output += add_data
        self.line_pos += len(add_data)

    def complete_report(self):
        add_data=''
        if self.line_pos < 80:
            for i in range(self.line_pos, 79):
                add_data += " "
            add_data += "|"
        return add_data
#title_center'
#txt_r
#txt
#report_center
#report_left
#page_break
#<b>
#<u>
#align='right'



parser = MyHTMLParser()
parser.feed(read_data)

print(parser.output)


