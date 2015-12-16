import os
import sys
import socket
import struct


from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import *

# Create your views here.

def lock_sheet_sock():
    pass

def unlock_sheet_sock():
    pass

class Request(object):
    def __init__(self, s, p): #sessid=None):
        self.s = s
        self.p = p
        #self.sessid = sessid
        
    def do(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("", self.p))
        
        buf = pickle.dumps(self)
        
        self.s.send(struct.pack("i", len(buf)))
        self.s.send(buf)
    
        self.read()

        self.s.close()

    def read(self):

        buf = self.s.recv(4)
        
        l = struct.unpack("i", buf)

        buf = self.s.recv(l)

        self.res = buf

def get_sheet(p):
    req = ss.service.Request('get sheet', p) #sessid)
    req.do()
    
    if req.res[:5]=="error":
        raise ValueError(req.res)
    
    sheet = pickle.loads(req.res)
    return sheet


#def sheet(request, sheet_id):

    

def sheet(request, sheet_id):
    #sessid,
    #cookie_out, 
    #cookie_in, 
    #display_func, 
    #debug_lines):

    print request.session

    sheet = get_object_or_404(Sheet, pk=sheet_id)
    
    assert(request.user == sheet.user)

    #debug_default(
    #        debug_lines,
    #        cookie_out,
    #        cookie_in,
    #        )

    # let other processes know that a socket is being opened for this sheet
    lock_sheet_sock()

    # test if there already exists a socket

    if sheet.port == -1:
    
        temps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temps.bind(("", 0))
        temps.listen(1)
    
        tempport = temps.getsockname()[1]


        # launch bg process
        path = os.path.join(settings.BASE_DIR, "sheets", "scripts", "bg0.py")
        os.spawnl(os.P_NOWAIT, path, tempport, "sheet_{}.bin")
        
        conn, addr = temps.accept()
        
        buf = conn.recv(4)
   
        port = struct.unpack("i", buf)

        temps.close()
        
        # save new port number
        sheet.port = port
        sheet.save()

    unlock_sheet_sock()

    sheetdata = get_sheet(sheet.port) #sessid)
    
    
    
    html  = et.tostring(form_sheet_ctrl(sessid))
    html += "\n"
    html += sheet.html(display_func, sessid)

    c = {
            "html": html,
            "debug_lines": "\n".join("<pre>"+l+"</pre>" for l in debug_lines),
            "debug": debug,
            }

    return render(request, "templates/sheet.html", c)




