import sys, os, pango, linuxcnc, hashlib
KEYWORDS = ['','T', 'P', 'X', 'Y', 'Z', 'A', 'B', 'C', 'U', 'V', 'W', 'D', 'I', 'J', 'Q', ';']
import locale
locale.setlocale(locale.LC_ALL, '')

class ToolTable(object):
    def __init__(self,toolfile=None, *a, **kw):
        self.emcstat = linuxcnc.stat()
        self.hash_check = None 
        self.toolfile = toolfile
        self.toolinfo_num = 0
        self.toolinfo = []
        if toolfile:
            self.reload()

        # create a hash code
    def md5sum(self,filename):
        try:
            f = open(filename, "rb")
        except IOError:
            return None
        else:
            return hashlib.md5(f.read()).hexdigest()
    
    def reload(self):
        self.hash_code = self.md5sum(self.toolfile)
        # clear the current liststore, search the tool file, and add each tool
        if self.toolfile == None:return
        self.toolinfo = []
        # print "toolfile:",self.toolfile
        if not os.path.exists(self.toolfile):
            print "Toolfile does not exist"
            return
        logfile = open(self.toolfile, "r").readlines()
        self.toolinfo = []
        for rawline in logfile:
            # strip the comments from line and add directly to array
            index = rawline.find(";")
            comment = (rawline[index+1:])
            comment = comment.rstrip("\n")
            line = rawline.rstrip(comment)
            #array = [0,0,0,'0','0','0','0','0','0','0','0','0','0','0','0','0',comment]
            array = [0,0,0,None,None,None,None,None,None,None,None,None,None,None,None,None,comment]
            toolinfo_flag = False
            # search beginning of each word for keyword letters
            # offset 0 is the checkbutton so ignore it
            # if i = ';' that is the comment and we have already added it
            # offset 1 and 2 are integers the rest floats
            for offset,i in enumerate(KEYWORDS):
                if offset == 0 or i == ';': continue
                for word in line.split():
                    if word.startswith(';'): break
                    if word.startswith(i):
                        if offset == 1:
                            if int(word.lstrip(i)) == self.toolinfo_num:
                                toolinfo_flag = True
                        if offset in(1,2):
                            try:
                                array[offset]= int(word.lstrip(i))
                            except:
                                print "ToolTable int error", word
                        else:
                            try:
                                array[offset]= locale.format("%10.4f", float(word.lstrip(i)))
                            except:
                                print "ToolTable float error", word.lstrip(i)
                        break
            self.toolinfo.append(array)

    # Note we have to save the float info with a decimal even if the locale uses a comma
    def save(self):
        if self.toolfile == None:return
        file = open(self.toolfile, "w")
        print self.toolfile
        for row in self.toolinfo:
            values = [ value for value in row ]
            #print values
            line = ""
            for num,i in enumerate(values):
                if num == 0: continue
                if i == None: continue
                elif num in (1,2): # tool# pocket#
                    line = line + "%s%d "%(KEYWORDS[num], i)
                elif num == 16: # comments
                    test = i.lstrip()
                    line = line + "%s%s "%(KEYWORDS[num],test)
                else:
                    test = i.lstrip() # localized floats
                    line = line + "%s%s "%(KEYWORDS[num], locale.atof(test))

            print >>file,line
            #print line
        # tell linuxcnc we changed the tool table entries
        try:
            linuxcnc.command().load_tool_table()
        except:
            print "Reloading tooltable into linuxcnc failed"

    def set_offset(self, toolnumber, value):
        for row in self.toolinfo:
            if (row[1] == toolnumber):
                row[5] = str(value)
                break
            
if __name__ == '__main__':
    st = linuxcnc.stat()
    st.poll()
    print st.gcodes
    print st.mcodes
    exit(1)
    tt = ToolTable("tool-simu.tbl")
    print tt.toolinfo
    tt.set_offset(3, 34.5)
    print tt.toolinfo
    tt.save()