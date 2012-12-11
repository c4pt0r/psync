#!/usr/bin/env python
#encoding=utf-8
"""
p-sync client
"""
import os
import sys
import optparse
import socket
import json
import zlib

CONF_FILE = '.psync.conf'
INDEX_FILE = '.psync.index'

def _crc(fileName):
    prev = 0
    for eachLine in open(fileName,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def _is_conf_file(filename):
    for fn in [CONF_FILE, INDEX_FILE]:
        if fn in filename:
            return True
    return False

def get_file_list(): 
    for dirname, _ , fnames  in os.walk('.'):
        for f in fnames:
            full_fn =  os.path.join(dirname, f)
            if  not _is_conf_file(full_fn):
                yield full_fn

def init():
    fp = open(CONF_FILE, 'a+')
    fp.close()
    fp = open(INDEX_FILE, 'a+')
    fp.close()

def update_index():
    indexes = {}
    for fname in get_file_list():
        indexes[fname] = {'checksum' : _crc(fname),
                          'size': os.path.getsize(fname),
                          'mode': os.stat(fname).st_mode}
    try:
        fp = open(INDEX_FILE, 'r+w')
        fp.write(json.dumps(indexes))
    except IOError:
        print 'index file not found'
        sys.exit(-1)

def read_indexs():
    fp = open(INDEX_FILE, 'r')
    indexs = json.loads(fp.read())

if __name__ == '__main__':
    pass