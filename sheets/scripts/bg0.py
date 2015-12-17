#!/usr/bin/env python
# open a sheet object from file and send and recieve information over a socket
import os
import sys
import select
import socket
import struct
import pickle

sys.stdout = open("/home/crymal/backedup/git/site_wiki/log/bg0.log", "w")
#sys.stderr = open("/home/crymal/backedup/git/site_wiki/log/bg0.err", "w")
#sys.stderr = open("/home/crymal/backedup/git/site_wiki/log/bg0.log", "w")
sys.stderr = sys.stdout

sys.path.append("/home/crymal/backedup/git/site_wiki")

import sheets.request
import sheets.sheet

def get_or_create(filename):
    try:
        f = open(filename, "rb")
    except:
        return sheets.sheet.Sheet()
    else:
        sheet = pickle.load(f)
        f.close()
        return sheet

print "bg0"
print "argv", sys.argv
print "cwd", os.getcwd()

if len(sys.argv) != 3:
    print "invalid args"
    sys.exit(1)

tempport = int(sys.argv[1])
filename = sys.argv[2]


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", tempport))

print "connected"

filename = os.path.join("sheets", filename)

sheet = get_or_create(filename)

print "start server"
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind(("", 0))
srv.listen(1)

port = srv.getsockname()[1]

print "port =", port

s.send(struct.pack("i", port))
s.close()



input_list = [srv]
#cli = []


def send(s, buf):

    s.send(struct.pack("i", len(buf)))
    s.send(buf)

def handle_get_sheet(s, req):
    send(s, pickle.dumps(sheet))

def respond(s, req):

    d = {
            "get sheet": handle_get_sheet
            }

    f = d[req.s]
    
    f(s, req)

def shutdown():

    for s in input_list:
        s.close()

    sys.exit(0)

def on_recv(s, buf):
    print "buf  ", repr(buf)

    req = pickle.loads(buf)

    print "req  ", repr(req)

    print "req  ", req.s
    
    respond(s, req)

    shutdown()


while 1:

    inputready, outputready, exceptready = select.select(input_list, [], [])

    for s in inputready:
        if s == srv:
            conn, addr = srv.accept()
            print "connection from", addr
            #cli.append(conn)
            input_list.append(conn)
            break
       
        print "recv bytes", 4
        buf = s.recv(4)
        print "recieved {} of {} bytes".format(len(buf), 4)

        if not (len(buf)==4):
            print "buf", repr(buf)
            raise Exception()

        l = struct.unpack("i", buf)[0]

        print "recieved {} {}".format(repr(buf), repr(l))
        
        print "recv bytes", l
        buf = s.recv(l)
        print "recieved {} of {} bytes".format(len(buf), l)

        if not (len(buf)==l):
            raise Exception()
        
        on_recv(s, buf)
        
        




