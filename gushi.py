import urllib2
import re
import time
import random
random.seed(time.clock())


def enhanced_open(url, fail_limit = 100):
    fail_count = 0
    while fail_count < fail_limit:
        try:
            resp = urllib2.urlopen(url)
        except:
            fail_count = fail_count + 1
            delay_secs = fail_count * 10 * random.random()
            print 'REQUEST', url, " FAILED #%d, " % fail_count, "delay", delay_secs, "(s) arranged"
            time.sleep(delay_secs)
        else:
            return resp


class TreeNode:
    def __init__(self, url, title):
        self.title = title
        self.url = url
        self.children = []

    def append(self, child):
        self.children.append(child)
        return child

    def dump(self, lvl = 1):
        print '  '* lvl, self.title, ':', self.url
        for child in self.children:
            child.dump(lvl + 1)


def list_chaps(home, restrict_domain = True):
    orig = []
    filtered = []
    response = enhanced_open("http://"+home)
    pat = re.compile("<a href=['\"](.*)['\"].*>(.*)</?a/?>")
    root = TreeNode('http://'+home, home)
    curnode = root
    for line in response:
        orig.append(line.strip())
        if '<UL' in line or '<ul' in line:
            print 'FOUND UL'
        if '</UL' in line or '</ul' in line:
            print 'FOUND UL TERM'
            curnode = root
        mat = pat.search(line)
        if mat:
            #print line
            url, title = mat.groups()
            if '<H2' in line or '<h2' in line:
                print 'FOUND H2'
                curnode = root.append(TreeNode(url, title))
            else:
                curnode.append(TreeNode(url, title))
            filtered.append((url, title))
    return orig, filtered, root

orig, flt, tree = list_chaps("www.miaojianggushi2.com")
#tree.dump()

books = filter(lambda n: len(n.children) > 0, tree.children)

def write_book(seq, book):
    fn = '%05d.html' % (seq)
    fd = open(fn, "w")
    fd.write('''<html><head><title>%s</title></head>
    <body><h1>%s</h1></body></html>''' % (book.title, book.title))

def write_chap(seq, chap):
    fn = '%05d.html' % (seq)
    fd = open(fn, "w")
    fd_temp = open("TEMP" + fn, "w")
    chap_response = enhanced_open(chap.url)
    state = 'INIT'
    fd.write('''<html>
    <head><title>%s</title></head>
    <body>''' % chap.title)
    for line in chap_response:
        fd_temp.write(line)
        if state == 'INIT' and re.search(r'<div\s.*class="post_title".*>', line):
            state = 'BEGIN'
            #print line, state
        if state == 'BEGIN' and re.search(r'<div\s.*class="clear">', line):
            state = 'END'
            #print line, state
        if state == 'BEGIN':
            fd.write(line)
    fd.write('''</body></html>
    ''')

break_point = 534
seq = 0
for book in books:
    seq = seq + 1
    print seq, book.title
    write_book(seq, book)
    for chap in book.children:
        seq = seq + 1
        print '    #', seq, chap.title
        #if seq < break_point: continue
        #write_chap(seq, chap)
