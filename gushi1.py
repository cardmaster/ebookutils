# -*- coding: utf-8 -*-

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
            delay_secs = fail_count * 5 * random.random()
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


def list_chaps(home, path, restrict_domain = False):
    orig = []
    filtered = []
    response = enhanced_open("http://"+home + path)
    pat = re.compile("<a href=['\"](.*?)['\"].*>(.*)</?a/?>")
    root = TreeNode('http://'+ home + path, home)
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
            if url.startswith("/"):
                url = "http://" + home + url
            if '<H2' in line or '<h2' in line:
                print 'FOUND H2'
                curnode = root.append(TreeNode(url, title))
            else:
                curnode.append(TreeNode(url, title))
            filtered.append((url, title))
    return orig, filtered, root

orig, flt, tree = list_chaps("www.ailingyi.com", "/mjgs/")
#tree.dump()

def write_book(seq, book):
    fn = 'gushi_i/%05d.html' % (seq)
    fd = open(fn, "w")
    fd.write('''<html><head><title>%s</title></head>
    <body><h1>%s</h1></body></html>''' % (book.title, book.title))

def write_chap(seq, chap):
    fn = 'gushi_i/%05d.html' % (seq)
    fd = open(fn, "w")
    chap_response = enhanced_open(chap.url)
    state = 'INIT'
    fd.write('''<html>
    <head><title>%s</title></head>
    <body>''' % chap.title)
    for line in chap_response:
        if state == 'INIT' and re.search(r'<div\s.*class="post_title".*>', line):
            state = 'BEGIN'
            #print line, state
        if state == 'BEGIN' and re.search(r'<div\s.*class="post_entry">', line):
            state = 'CONTENT'
            #print line, state
        if state == 'CONTENT' and re.search(r'<h2>', line):
            state = 'END'
        if state in ['BEGIN', 'CONTENT'] :
            fd.write(line.replace('<br/>', '<br />\n'))
    fd.write('''</body></html>
    ''')

books = tree.children[22:1418]#filter(lambda n: len(n.children) >= 0, tree.children)
book_seq=1
break_point = 1121
end_point = 1125
seq = 0
for book in books:
    if '第一章' in book.title:
        seq += 1
        booksep = TreeNode('', '第%d卷' % book_seq)
        print 'FOUND BOOK: ', booksep.title
        write_book(seq, booksep)
        book_seq += 1
    seq += 1
    print seq, book.title, book.url,
    #write_book(seq, book)
    #for chap in book.children:
    #   seq = seq + 1
    #    print '    #', seq, chap.title
    if seq < break_point or seq > end_point:
        print "... SKIP"
        continue
    print ""
    write_chap(seq, book)
