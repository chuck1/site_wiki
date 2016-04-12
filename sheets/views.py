import os
import sys
import socket
import struct
import subprocess
import pickle

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings

import sheets.models

import sheets.request

# Create your views here.

def lock_sheet_sock():
    pass

def unlock_sheet_sock():
    pass
   
def send_request(p, r):
    print "send request"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", p))
    
    buf = pickle.dumps(r)
    
    # write

    s.send(struct.pack("i", len(buf)))
    s.send(buf)
    
    # read
    print "recv 4"
    buf = s.recv(4)
    l = struct.unpack("i", buf)[0]
    print "recv", l
    buf = s.recv(l)

    res = buf

    s.close()

    return res

def test_connection(p):
    req = sheets.request.Request('test')
    
    res = send_request(p, req)

    print "test response", res

def get_sheet(p):
    req = sheets.request.Request('get sheet') #sessid)
    
    res = send_request(p, req)
    
    if res[:5]=="error":
        raise ValueError(res)
    
    sheet = pickle.loads(res)
    return sheet


#def sheet(request, sheet_id):

def launch_process(sheet):
    print "open temps"
    temps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temps.bind(("", 0))
    temps.listen(1)
    
    tempport = temps.getsockname()[1]
    print "tempport =", tempport

    # launch bg process
    path = os.path.join(settings.BASE_DIR, "sheets", "scripts", "bg0.py")
    print "launching process path =", path
    #pid = os.spawnl(os.P_NOWAIT, path, tempport, "sheet_{}.bin")
    cmd = [path, str(tempport), "sheet_{}.bin".format(sheet.id)]
    pid = subprocess.Popen(cmd).pid
    
    print "process launched pid =", pid
    
    print "accept connection"
    conn, addr = temps.accept()
    
    print "recieve bytes"
    buf = conn.recv(4)
   
    port = struct.unpack("i", buf)[0]

    print "port =", port

    temps.close()
    
    # save new port number
    sheet.port = port
    sheet.save()



def sheet(request, sheet_id):
    """
    the actual view
    """

    sheet = get_object_or_404(sheets.models.Sheet, pk=sheet_id)

    # permissions
    assert(request.user == sheet.user)
    
    message = ""


    #debug_default(
    #        debug_lines,
    #        cookie_out,
    #        cookie_in,
    #        )

    # let other processes know that a socket is being opened for this sheet
    lock_sheet_sock()

    # test if there already exists a socket

    if sheet.port == -1:
        launch_process(sheet)
    else:
        message += "test connection<br>"
        
        try:
            test_connection(sheet.port)
        except:
            launch_process(sheet)
        else:
            message += "connection success<br>"

    unlock_sheet_sock()

    sheetdata = get_sheet(sheet.port) #sessid)
    
    message+= " {} ".format(sheet.port)
    

    # process button click

    if request.method == "POST":
        #message = "btn=" + request.POST["btn"]
        message += repr(request.POST)
        try:
            message += " "+request.POST[u"btn"]
        except: pass

    elif request.method == "GET":
        message += "GET"
    
    
    #html  = et.tostring(form_sheet_ctrl(sessid))
    #html += "\n"
    html = sheetdata.html()#display_func, sessid)
    
    #html = repr(sheet)

    c = {
            "html": html,
            #"debug_lines": "\n".join("<pre>"+l+"</pre>" for l in debug_lines),
            #"debug": debug,
            "message": message,
            }

    return render(request, "sheets/sheet.html", c)




