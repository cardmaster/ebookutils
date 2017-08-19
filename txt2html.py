# -*- coding: utf-8 -*-
import os
import re
import cgi

inputdir = "C:/Users/leaf/Downloads/监高启明"
outputdir = "C:/Users/leaf/Downloads/监高启明HTML"
if not outputdir:
    outputdir = inputdir
if not os.path.isdir(outputdir):
    os.mkdir(outputdir)

inputcoding = 'utf-8'
outputcoding = 'utf-8'

def digit_ext_strings(slist):    
    maxlen = 1
    digipat = re.compile('\d+')
    slist = list(slist)
    for s in slist:
        al = [len(v) for v in re.findall(digipat, s)]
        al.append(maxlen)
        maxlen = max(al)

    digifmt = '%0{}d'.format(maxlen)
    def digiext(m):
        iv = int(m.string[m.start():m.end()])
        return digifmt % iv
    
    return sorted([(re.sub(digipat, digiext, s), s) for s in slist], key=lambda c:c[0])


class HtmlBuilder:
    def __init__(self, ofd, hlv = 2):
        self.ofd = ofd
        self.firstline = True
        self.hlv = hlv

    def istitle(self, lns):
        if self.firstline:
            self.firstline = False
            return True
    
    def write_head(self, title):
        self.ofd.write('''<html><head>
<meta http-equiv="Content-Type" content="text/html; charset={}" />
<title>{}</title></head><body>'''.format(outputcoding, title))
    
    def write_end(self):
        self.ofd.write("</body></html>")
    
    def feed(self, ln):
        if not ln.strip():
            return
        lnescape = cgi.escape(ln.rstrip())
        tag = "p"
        if self.istitle(ln.strip()):
            tag = "h{}".format(self.hlv)
        self.ofd.write("".join(["<", tag, ">", lnescape, "</",tag,">\n"]))


def convert_file(ifn, ofn):
    ifd = open(ifn, "r", encoding = inputcoding)
    ofd = open(ofn, "w", encoding = outputcoding)
    blder = HtmlBuilder(ofd)
    blder.write_head(ifn)
    for ln in ifd:
        blder.feed(ln)
    blder.write_end()


flist = os.listdir(inputdir)
flist = digit_ext_strings(filter(lambda f:f.endswith(".txt"), flist))
#print("\n".join([" ".join(c) for c in flist]))
extpat = re.compile('.txt$')
for extn, fn in flist:
    ofn = re.sub(extpat, '.html', extn)
    print (ofn, fn)
    convert_file(os.path.join(inputdir, fn), os.path.join(outputdir, ofn))

