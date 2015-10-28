import os
import markdown
import time
import git
import difflib
import re

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

from .models import Page, Patch

# Create your views here.

#root = '/home/chuck/site_wiki'
root = 'P:\\data\\site_wiki'

source_root = os.path.join(root, 'source')
build_root = os.path.join(root, 'build')

####################################################

def fix(l):
	if 0:
		if l[0] == '-':
			if '\r' in l[1:]:
				h,t = l[1:].split('\r')
				ret = ['-'+h+'\n']
				if t:
					if t[-1] != '\n':
						t += '\n'
					#ret += ['-' + t, '\\ No newline at end of file']
					ret += ['-' + t]
				return ret
	
	if 1:
		if l[-1] != '\n':
			if l[-1] != '\r':
				return [l + '\n']
	
	if 0:
		if l[-1] == '\r':
			return [l[:-1]+'\n']
	
	return [l]

def fix_diff(d, g):
	
	if '-' in d:
		d.remove('-')
		g[1] -= 1
	
	return d, g
	
class MyDiff(object):
	def __init__(self, head, g, lines):
		self.head = head
		self.g = g
		self.lines = lines
	
	def combine(self):
		s0 = ',{}'.format(self.g[1]) if self.g[1] else ''
		
		s1 = ',{}'.format(self.g[3]) if self.g[3] else ''
		
		l = '@@ -{}{} +{}{} @@\n'.format(
			self.g[0],
			s0,
			self.g[2],
			s1
			)
		
		return self.head + [l] + self.lines
		
	def apply(self, r):
		filename_patch = os.path.join(root, 'patch.diff')
		
		with open(filename_patch, 'w') as f:
			f.writelines(self.combine())
		
		#res = r.git.execute(['git', 'apply', '--ignore-whitespace', '--check', filename_patch])
		
		#res = r.git.execute(['git', 'apply', '-3', '--ignore-whitespace', filename_patch])
		res = r.git.execute(['git', 'apply', '--ignore-whitespace', filename_patch])
		print 'res',repr(res)

def create_diff(lines_a, lines_b, filename):
	g = difflib.unified_diff(lines_a, lines_b, 'a/'+filename, 'b/'+filename)

	d = list(g)
	
	header = d[:3]
	d = d[3:]
	
	m = re.match('@@ -(\d+)(,\d+)? \+(\d+)(,\d+)? @@', header[2])
	if not m:
		print 'header',header[2]
	
	g = [int(x.replace(',','')) if x else None for x in m.groups()]
	print 'info', g
	
	print 'original patch lines'
	print
	for l in d:
		print repr(l)
	print
	
	d, g = fix_diff(d, g)
	
	
	#for l in d:
	#	print repr(l)
	
	#header[2] = '@@ -{},{} +{},{} @@\n'.format(g[0], g[1], g[2], g[3])
	
	if d:
		h = d
		t = []
		if 0:
			t = h[-1:]
			h = h[:-1]
			
		d1 = [fix(l) for l in h]
		d1 = [item for sublist in d1 for item in sublist]
		
		d = d1 + t
		
		# if the last two lines dont have a newline, that means they are at the
		# end of the file
		if 0:
			if (d[-1][-1] != '\n') and (d[-2][-1] != '\n'):
				d[-1] = d[-1] + '\n'
				d[-2] = d[-2] + '\n'
				d.append('\\ No newline at end of file')

		#if (d[-1][-1] != '\n'):
		#	d[-1] = d[-1] + '\n'
		#	d.append('\\ No newline at end of file')
	
	return MyDiff(header[:2], g, d)

def apply_diff(patch, raw):

	r = git.Repo(source_root)
	
	#filename = 'a'
	
	lines_a = patch.orig.split('\n')
	lines_b = raw.split('\n')

	# create diff between two files
	
	dif = create_diff(lines_a, lines_b, patch.page.path+'.md')
	
	if not dif.lines:
		print 'no diff'
		#raw_input()
		#sys.exit(0)
		return
	
	print 'fixed patch lines'
	print
	for l in dif.lines:
		print repr(l)
	print
	#raw_input()

	# apply diff
	
	try:
		dif.apply(r)
	except Exception as e:
		print 'e',e
		
		dif.g[1] -= 1
		dif.g[3] -= 1
		try:
			dif.apply(r)
		except Exception as e:
			print 'e',e
			return str(e)
	
	dl = r.index.diff(None)
	do = dl[0]
	print do.a_path
	print do.b_path
	r.index.add([do.a_path])
	c = r.index.commit('auto patch of {}'.format(do.a_path))
	print c
	
	#raw_input()
	return c

def apply_diff_2(patch, raw):
	"""
	a simpler way of submitting changes to the repo
	"""
	path = patch.page.path
	npath = os.path.normpath(path)
	src_path = os.path.join(source_root, npath + '.md')
	
	print 'SRC PATH', src_path
	
	with open(src_path, 'w') as f:
		f.write(raw)
	
	r = git.Repo(source_root)

	r.index.add([src_path])
	c = r.index.commit('auto for {}'.format(path))
	
	return c
	
####################################################

def assert_dir(path):
	d = os.path.dirname(path)
	try:
		os.makedirs(d)
	except:
		pass

def get_build(src, dst):
	if requires_update(src, dst):
		print 'rebuilding'

		raw = get_contents(src)

		body = markdown.markdown(raw)
		
		assert_dir(dst)
		
		with open(dst, 'w') as f:
			f.write(body)
	else:
		with open(dst, 'r') as f:
			body = f.read()

	return body

def get_mtime(path):
	try:
		return time.ctime(os.path.getmtime(path))
	#except IOError, WindowsError:
	except:
		return 0
		
		try:
			os.makedirs(os.path.dirname(path))
		except OSError:
			pass
		
		#with open(path, 'w') as f:
		#	f.write('hi')
		
		#try:
		#return time.ctime(os.path.getmtime(path))
		#except:
		#	return 0
	pass

def requires_update(src, dst):
	if not os.path.exists(dst):
		return True

	s = get_mtime(src)
	d = get_mtime(dst)
	return s > d

def get_contents(path):
	#try:
	with open(path, 'r') as f:
		return f.read()
	#except IOError:
	#    try:
	#        os.makedirs(os.path.dirname(path))
	##    except OSError:
	#        pass
	#    
	#    return 'file not found = {}'.format(repr(path))
	pass

def edit_save(request):
	#try:
	patch_id = request.POST['patch_id']
	raw = request.POST['raw']
	
	raw = raw.replace('\r','')
	
	print
	print 'raw',repr(raw)
	print
	
	patch = Patch.objects.get(pk=patch_id)
	
	res = apply_diff_2(patch, raw)
	
	return HttpResponseRedirect('{}'.format(patch.page.path))
	
	#except Exception as e:
	#	#return HttpResponse(str(e))
	#	raise e
	pass
	
def edit(request):
	if not (request.method == 'POST'):
		return HttpResponseNotFound()

	try:
		patch_id = request.POST['patch_id']
	except:
		patch_id = None
		#return HttpResponseNotFound()

	patch = Patch.objects.get(pk=patch_id)

	print 'orig',repr(patch.orig)
	
	c = {
		'path': patch.page.path,
		'patch_id': patch.id,
		'raw': patch.orig,
		}

	return render(request, 'wiki/edit.html', c)

def page(request, path0):
	
	path = os.path.normpath(path0)
	
	try:
		page = Page.objects.get(path=path0)
	except Exception as e:
		page = Page()
		page.path = path0
		page.save()
		#return HttpResponse(str(e))
	
	print 'page=',page
	
	build_path = os.path.join(build_root, path)
	source_path = os.path.join(source_root, path + '.md')
	
	body = get_build(source_path, build_path)
	
	# get HEAD commit string
	r = git.Repo(source_root)
	s = r.head.commit.__str__()
	
	print 'commit=', s
	
	# create a new Patch object
	patch = Patch()
	patch.page = page
	patch.orig = get_contents(source_path)
	patch.save()

	print 'orig',repr(patch.orig)
	
	c = {
			'path': path0,
			'patch_id': patch.id,
			'body': body,
			}

	return render(request, 'wiki/page.html', c)



