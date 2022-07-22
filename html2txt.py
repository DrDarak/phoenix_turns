from html.parser import HTMLParser
import os
import re

current_path = os.path.dirname(os.path.realpath(__file__))
target_path = current_path + '/data/12345.html'
read_data=''
with open(target_path) as f:
    read_data = f.read()
    f.close()
max_line_length=80

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
        self.col_data=[]
        self.row_cols = [] # current columns in row

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
            self.col_data=[]
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
                        ##if col_len>0:
                        ##    col+=self.cols[self.lvl][col_len-1]
                        self.cols[self.lvl].append(col)
                if a[0]=='class':
                    self.row_type = a[1]

    def handle_endtag(self, tag):
        if tag == 'table':
            self.lvl -= 1
            if self.lvl>=0:
                print()
                del self.cols[-1]
        elif tag == 'tr':
            self.first_row=False
            self.in_line = False
            self.first_row =False
            self.render_row()
        elif tag == 'td':
            self.in_data = False

    def handle_data(self, data):
        if self.in_data:
            # don't allow any data from html formating to slip in
            data=data.replace("\n", "")
            if data!='':
                self.col_data.append(data)

    def render_row(self):
        self.correct_columns()

        self.line_pos = 0
        for i in range(0, len(self.col_data)):
            data=self.col_data[i]
            add_data=''
            if i>0 and len(self.row_cols)>i-1:
                last_col_pos=self.row_cols[i-1]
                if self.line_pos<last_col_pos:
                    for j in range(self.line_pos,last_col_pos):
                        add_data+=' '
            self.output +=add_data
            self.line_pos += len(add_data)

            data_size = len(data)
            self.row_type_pre_adjust(data_size)

            # add data after columns sorted
            self.output+=data
            self.line_pos+=data_size

            self.row_type_post_adjust(data_size,i)
        if len(self.col_data)>0:
            self.output+='\n'
        self.col_data=[]

    def correct_columns(self):
        if  len(self.cols[self.lvl])<=0:
            self.row_cols=[]
            return

        ## correct lines that can be
        self.row_cols= self.cols[self.lvl].copy()
        if self.row_type=='txt_r':
            size=len(self.col_data)
            widths=[]
            for i in range(0, size):
                widths.append(len(self.col_data[i]) + 1 + (i == 0) * 3 + (i == (size - 1)))
                if i>0 and widths[i]>self.row_cols[i]:
                    c=self.col_data[i-1].find(':')
                    if widths[i-1]<self.row_cols[i-1] and c>0:
                        diff=widths[i]-self.row_cols[i]
                        if diff>(self.row_cols[i-1]-widths[i-1]):
                            diff=self.row_cols[i-1]-widths[i-1] ## failed
                        ## modify columns
                        self.row_cols[i - 1]-=diff
                        self.row_cols[i] += diff

        # convert to cumlative
        for i in range(1,len(self.row_cols)):
            self.row_cols[i]+=self.row_cols[i-1]

    def row_type_pre_adjust(self,data_size):
        add_data=''
        if self.line_pos==0:
            if self.row_type=='report_left':
                add_data="|-"
            if self.row_type=='report_center':
                add_data="|"
                fsize = int((max_line_length-1 - data_size) / 2)
                for i in range(0,fsize):
                    add_data+='-'
            if self.row_type=='txt_r':
                add_data="| "
            if self.row_type == 'title_center' or self.row_type == 'page_break':
                fsize=int((max_line_length-data_size)/2)
                ins=' '
                if self.row_type == 'page_break':
                    ins='-'
                for i in range(0,fsize):
                    add_data+=ins
        self.output += add_data
        self.line_pos+=len(add_data)

    def row_type_post_adjust(self,data_size,col):
        add_data = ''
        ## if current column is the end column
        if col>=0 and len(self.row_cols)>col and \
           self.row_cols[col]>=max_line_length:
            if self.row_type=='txt_r':
                add_data=self.complete_report()
        if self.lvl==1:
            if self.row_type == 'report_left' or self.row_type=='report_center':
                if self.line_pos < max_line_length:
                    for i in range(self.line_pos, max_line_length-1):
                        add_data += "-"
                    add_data += "|"
            ## no columns at lvl 2
            if self.row_type == 'txt_r':
                add_data=self.complete_report()
        if self.row_type == 'title_center' or self.row_type == 'page_break':
                fsize=max_line_length-data_size-int((max_line_length-data_size)/2)
                ins=' '
                if self.row_type == 'page_break':
                    ins='-'
                for i in range(0,fsize):
                    add_data+=ins
        self.output += add_data
        self.line_pos += len(add_data)

    def complete_report(self):
        add_data=''
        if self.line_pos < max_line_length:
            for i in range(self.line_pos, max_line_length-1):
                add_data += " "
        add_data += "|"
        return add_data

    def process(self,data):
        self.feed(data)
        lines = re.split(r"\r\n|\r|\n",self.output)
        self.output=''
        for line in lines:
            if len(line)>max_line_length:
                line=break_line(line)
            self.output+=line+'\n'

def break_line(line):
    output=''
    pos=0
    while len(line)>max_line_length:
        for i in range(max_line_length,0,-1):
            if line[i]== ':' or line[i] == ';' or line[i] == '.' or line[i] == ',' or line[i] == ' ':
                i+=1
                output+=line[:i]+'\n' ## output line
                line=line[i:] ## remove start
                break
    output += line
    return output

#<b>
#<u>

parser = MyHTMLParser()
parser.process(read_data)
print(parser.output)

