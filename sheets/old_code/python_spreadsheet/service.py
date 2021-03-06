import os
import array
import xml.etree.ElementTree as et
import pickle
import re
import numpy as np
import struct
import signal
import datetime
import random

import python_spreadsheet as ss
import python_spreadsheet.sheet
import python_spreadsheet.security

name_srv_w = "/tmp/python_spreadsheet_srv_w"
name_cli_w = "/tmp/python_spreadsheet_cli_w"

def cli_read():
    with open(name_srv_w, 'rb') as f:
        return f.read()

def cli_write(s):
    with open(name_cli_w, 'wb') as f:
        f.write(s)



class Stop(Exception):
    pass

class User(object):
    def __init__(self):
        self.sheets = {}

    def get_sheet(self, s):
        print "get_sheet({})".format(repr(s))
        try:
            sheet = self.sheets[s]
        except:
            sheet = ss.sheet.Sheet()
            self.sheets[s] = sheet
        return sheet

class Session(object):
    def __init__(self, user):
        self.sessid = random.randint(0,1000000000)
        self.user = user

class Service(object):
    def __init__(self, f):
        try:
            self.load()
            print "sheets loaded"
        except:
            self.users = {}
            print "sheets not loaded"
        
        self.sessions = {}
        
        self.logfile = f

        self.fifo_name_srv_w = "/tmp/python_spreadsheet_srv_w"
        self.fifo_name_cli_w = "/tmp/python_spreadsheet_cli_w"

        def signal_handler(signum, frame):
            print 'signal handler called with signal', signum
            if (signum == signal.SIGTERM) or (signum == signal.SIGINT):
                self.save()
                self.f.close()

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT,  signal_handler)

        try:
            os.remove(self.fifo_name_srv_w)
            print self.fifo_name_srv_w, "removed"
            os.remove(self.fifo_name_cli_w)
            print self.fifo_name_cli_w, "removed"
        except Exception as e:
            print e
            pass

        try:
            um = os.umask(000)
            print "umask was",um
            os.mkfifo(self.fifo_name_srv_w, 0777)
            print self.fifo_name_srv_w, "created"
            os.mkfifo(self.fifo_name_cli_w, 0777)
            print self.fifo_name_cli_w, "created"
            os.umask(um)
        except OSError:
            pass

    def save(self):
        fn = os.path.join(os.path.dirname(__file__),'data','sheets.bin')
        with open(fn, 'wb') as f:
            pickle.dump(self.users, f)

    def load(self):
        fn = os.path.join(os.path.dirname(__file__),'data','sheets.bin')
        with open(fn, 'rb') as f:
            self.users = pickle.load(f)

    def write(self, s):
        with open(self.fifo_name_srv_w, 'wb') as f:
            f.write(s)
    
    def read(self):
        with open(self.fifo_name_cli_w, 'rb') as f:
            return f.read()

    def parse_cell(self, s):
        m = re.match('^(\d+)_(\d+)$', s)
        r = int(m.group(1))
        c = int(m.group(2))
        return r,c

    def get_user(self, u):
        print "get_user({})".format(repr(u))
        try:
            user = self.users[u]
        except:
            user = User()
            self.users[u] = user
        return user

    def create_session(self, u):

        sess = Session(u)
        self.sessions[sess.sessid] = sess

        print "created session {} {}".format(repr(sess.sessid), repr(u))

        return sess

    def blocking_read(self):
        #a = array.array('i')

        s = self.read()
        req = pickle.loads(s)
        #a.fromstring(s)
    
        print 'req.s      =',req.s
        print 'req.sessid =',req.sessid
        
        if req.sessid:
            print "sessid = {}".format(req.sessid)
            try:
                sess = self.sessions[req.sessid]
            except KeyError as e:
                print "session not found {}".format(repr(str(req.sessid)))
                self.write('error:' + e.message)
                return
            
            # get or create sheet for user
            user = self.get_user(sess.user)
            sheet = user.get_sheet('sheet0')

            if req.s == 'get sheet':
                s_out = pickle.dumps(sheet)
                self.write(s_out)

            elif req.s == 'add row':
                sheet.add_row()
                self.write('0')
        
            elif req.s == 'add col':
                sheet.add_col()
                self.write('0')

            elif req.s == 'set cell':
                #cell = self.read()
                #text = self.read()
                #print 'cell =',cell,'text =',text
            
                cell = req.cell
                text = req.text
            
                self.write('0')
           
                print 'cell =',cell
                print 'text =',text

                r,c = self.parse_cell(cell)

                print 'r,c = ',r,c
      
                sheet.set_cell(r, c, text)
            else:
                self.write('unknown command')

        elif req.s == 'login':
            u = req.u
            p = req.p
            
            print 'usr',u
            print 'pwd',p
            
            try:
                ss.security.check_pwd(u,p)
            except ss.security.InvalidUsr:
                print 'invalid usr'
                ss.security.create_usr(u,p)
                
                sess = self.create_session(u)

                self.write("login success,{}".format(sess.sessid))
            except ss.security.InvalidPwd:
                print 'invalid pwd'
                self.write('invalid pwd')
            else:
                # create new session
                sess = self.create_session(u)
                print 'success'
                self.write("login success,{}".format(sess.sessid))

        elif req.s == 'stop':
            self.write('0')
            raise Stop()
        else:
            err_str  = "unknown command or forgot to "
            err_str += "set req.usr. req.s = {}".format(repr(req.s))

            self.write('error:' + err_str)

    def run(self):
        
        t = datetime.datetime.now() + datetime.timedelta(minutes=1)
        
        while True:
            # save every minute
            if datetime.datetime.now() > t:
                self.save()
                t = datetime.datetime.now() + datetime.timedelta(minutes=1)

            try:
                print "waiting for data"
                self.blocking_read()
            except Stop:
                break
            except IOError:
                print "got ioerror"
                break


