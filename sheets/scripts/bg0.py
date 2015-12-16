#!/usr/bin/env python
# open a sheet object from file and send and recieve information over a socket

import sys
import select
import socket
import struct

if len(sys.argv) != 3:
    print "invalid args"
    sys.exit(1)

tempport = int(sys.argv[1])
filename = sys.argv[2]


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("", tempport))


f = open(filename, "r")

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind(("", 0))
srv.listen(1)

port = srv.getsockname()[1]

s.send(struct.pack("i", port))
s.close()



input_list = [srv]
cli = []



def on_recv(ptype, buf):
    print "ptype", repr(ptype)
    print "buf  ", repr(buf)

while 1:

    inputready, outputready, exceptready = select.select(input_list, [], [])

    for s in inputready:
        if s == srv:
            conn, addr = srv.accept()
            print "connection from", addr
            cli.append(conn)
            input_list.append(conn)
            break
       
        print "recv bytes", 8
        buf = s.recv(8)

        if not (len(buf)==8):
            print "recieved {} of {} bytes".format(len(buf), 8)
            print "buf", repr(buf)
            raise Exception()


        length, ptype = struct.unpack("ii", buf)

        print "recieved {} {} {}".format(repr(buf), repr(length), repr(ptype))
        
        print "recv bytes", length
        buf = s.recv(length)

        if not (len(buf)==length):
            print "recieved {} of {} bytes".format(len(buf), length)
            raise Exception()
        
        on_recv(ptype, buf)
        
        




