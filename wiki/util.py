from django.conf import settings

import markdown
import os
import json

def list_data_src():
	for root, dirs, files in os.walk(settings.WIKI_SRC_ROOT):
		for f in files:
			if f == 'data.txt':
				path = os.path.join(root, f)
				print path

def get_data_dir(dir):
	path = os.path.join(settings.WIKI_SRC_ROOT, dir, 'data.txt')
	if not os.path.exists(path): return None
	with open(path, 'r') as f:
		s = f.read()
	return json.loads(s)

def get_data_file(f):
	f,_ = os.path.splitext(f)
	path = os.path.join(settings.WIKI_SRC_ROOT, f + '.txt')
	if not os.path.exists(path): return None
	with open(path, 'r') as f:
		s = f.read()
	return json.loads(s)

def flt_files(x):
	if x[0] == '.': return False
	_,e = os.path.splitext(x)
	if e: return True
	return False

def flt_folders(x):
	if x[0] == '.': return False
	_,e = os.path.splitext(x)
	if e: return False
	return True

def mylistdir(dir, flt):
	lst = os.listdir(os.path.join(settings.WIKI_SRC_ROOT, dir))
	
	lst = filter(flt, lst)
	
	def srt(x,y):
		_,e0 = os.path.splitext(x)
		_,e1 = os.path.splitext(y)
		
		#print x,y
		#print e0,e1
		
		if bool(e0) != bool(e1):
			return cmp(bool(e0), bool(e1))
		
		return cmp(x,y)
	
	lst = sorted(lst, srt)
	
	def proc(x):
		#print 'x',x
		x = x.replace('\\','/')
		#print 'x',x
		
		h,e = os.path.splitext(x)
		if not e:
			return x + '/index'
		return h
	
	lst = [proc(x) for x in lst]
	
	def proc2(x):
		h,t = os.path.split(x)
		if h:
			return '- [{}]({})'.format(h,x)
		return '- [{}]({})'.format(t,x)
	
	lst = [proc2(x) for x in lst]
	
	return lst

def sibling_link_html(dir):
	lst = mylistdir(dir, flt_files)
	
	#for l in lst:
	#	print '  {}'.format(l)
	
	raw = '\n'.join(lst)
	html = markdown.markdown(raw)
	return html
	
def child_link_html(dir):
	lst = mylistdir(dir, flt_folders)
	
	#for l in lst:
	#	print '  {}'.format(l)
	
	raw = '\n'.join(lst)
	html = markdown.markdown(raw)
	return html

	