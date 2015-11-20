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

def get_data(f):
	f = os.path.join(settings.WIKI_SRC_ROOT, f)
	with open(f, 'r') as f:
		s = f.read()
	return json.loads(s)

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

def listize(p):
    h,t = os.path.split(p)
    l = []
    while h:
        #print 'h',h,'t',t
        l.insert(0,h)
        h,t = os.path.split(t)
    l.append(t)
    return l

def get_node(lst, d):
    while lst:
        l = lst.pop(0)
        try:
            d = d[0][l]
        except KeyError:
            d[0][l] = [dict(),[]]
            d = d[0][l]
    return d

def file_cmp(x,y):
    if (x[:5] == 'index') and (y[:5] != 'index'): return True
    if (x[:5] != 'index') and (y[:5] == 'index'): return False
    return cmp(x,y)

class FileListGenerator(object):
	
	def __init__(self, filter_func = None):
		self.filter_func = filter_func
	
	def recurse(self, p, tree):
		#print 'tree',tree
		#print 'p',p

		for f in sorted(tree[1], cmp=file_cmp):
			self.file_list.append(os.path.join(*(p + [f])))
		
		for key in sorted(tree[0].keys()):
			self.recurse(p + [key], tree[0][key])
		
	def __call__(self):
	
		self.file_list = []
		
		tree = [{},[]]
		
		for root, dirs, files in os.walk(settings.WIKI_SRC_ROOT):
			#print 'root',root
			#print 'dirs',dirs
			root = os.path.relpath(root, settings.WIKI_SRC_ROOT)
			
			#h,t = os.path.split(root)
			#print repr(h),repr(t),repr(root)
			if root[:4] != '.git':
				#print root
				#print files
				l = listize(root)
				#print l
				n = get_node(l, tree)
				n[1] = files
		
		self.recurse([], tree)
		
		def file_list_cmp(p0,p1):
			h0, t0 = os.path.split(p0)
			h1, t1 = os.path.split(p1)
			
			if h0 != h1:
				return cmp(h0, h1)
			
			return file_cmp(t0,t1)
		
		self.file_list = sorted(self.file_list, cmp=file_list_cmp)
		
		# filter
		if self.filter_func is not None:
			self.file_list = filter(self.filter_func, self.file_list)
		
		return self.file_list




