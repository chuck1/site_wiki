import os
import markdown
import time
import git
import difflib
import re

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.conf import settings
import django.core.management

from .models import Page, Patch, Lock
import wiki.forms
import wiki.util

# markdown extensions
import markdown.extensions.tables
import markdown_extension_blockmod
import markdown_extension_numbering

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

	r = git.Repo(settings.WIKI_SRC_ROOT)
	
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
	src_path = os.path.join(settings.WIKI_SRC_ROOT, npath + '.md')

	r = git.Repo(settings.WIKI_SRC_ROOT)

	# switch to my unique branch
	
	branch = r.create_head('auto_{}'.format(patch.id), patch.commit_orig)
	r.head.reference = branch
	assert not r.head.is_detached
	r.head.reset(index=True, working_tree=True)
	
	# edit file
	
	print 'CONTENTS', repr(get_contents(src_path))
	
	print 'SRC PATH', src_path
	with open(src_path, 'w') as f:
		f.write(raw)
	
	# commit
	
	diffs = r.index.diff(None)
	print 'DIFFS'
	for d in diffs:
		print '  {}'.format(d.a_path)
	
	r.index.add([diffs[0].a_path])
	c = r.index.commit('auto for {}'.format(path))
	
	print 'HEAD  ', r.head.reference
	print 'COMMIT', str(c)[:8], c.message
	
	diffs = r.index.diff(None)
	print 'DIFFS'
	for d in diffs:
		print '  {}'.format(d.a_path)
	
	# merge
	master = r.heads.master
	
	master.checkout()
	
	merge_base = r.merge_base(branch, master)
	
	#r.index.merge_tree(master, base=merge_base)
	r.index.merge_tree(branch, base=merge_base)
	
	c = r.index.commit('auto merge', parent_commits=(branch.commit, master.commit))
	
	# trying to fix
	#r.head.reference = master
	#assert not r.head.is_detached
	#r.head.reset(index=True, working_tree=True)
	
	r.head.reset(c, index=True, working_tree=True)
	
	#master.commit = branch.commit
	#r.head.reference = master
	
	print 'HEAD  ', r.head.reference
	print 'COMMIT', str(c)[:8], c.message
	return c

def apply_diff_3(patch, raw):
	"""
	using mostly execute commands
	"""
	path = patch.page.path
	npath = os.path.normpath(path)
	src_path = os.path.join(settings.WIKI_SRC_ROOT, npath + '.md')
	
	r = git.Repo(settings.WIKI_SRC_ROOT)
	
	r.git.execute(['git', 'checkout', patch.commit_orig])
	r.git.execute(['git', 'checkout', '-b', 'auto_{}'.format(patch.id)])
	
	
	with open(src_path, 'w') as f:
		f.write(raw)
	
	diffs = r.index.diff(None)
	print 'DIFFS'
	for d in diffs:
		print '  {}'.format(d.a_path)
	
	r.git.execute(['git', 'add', diffs[0].a_path])
	r.git.execute(['git', 'commit', '-m', '\'auto for {}\''.format(path)])
	
	r.git.execute(['git', 'checkout', 'master'])
	
	branch_name = 'auto_{}'.format(patch.id)
        
        commit_message = "'auto merge for {}'".format('auto_{}'.format(patch.id))
	
	try:
		r.git.execute(['git', 'merge', branch_name])
	except Exception as e:
		print e
		if 'exit code 1' in str(e):
			r.git.execute(['git', 'add', diffs[0].a_path])
			r.git.execute(['git', 'commit', '-m', commit_message])
		else:
			raise e

        commit_str = r.head.commit.__str__()

	return commit_str

####################################################

def assert_dir(path):
	d = os.path.dirname(path)
	try:
		os.makedirs(d)
	except:
		pass

def get_build(src, dst):
	'''
	get the html for the src file and save it to dst file
	'''
	
	if requires_update(src, dst):
	    print 'rebuilding'

	    j_data = wiki.util.get_data_file(src)
		
	    raw = get_contents(src)

	    #body = markdown.markdown(raw)
		
	    extensions=[
			markdown.extensions.tables.TableExtension(),
			markdown_extension_blockmod.MyExtension()]
		
	    try:
		numbering = j_data['numbering']
	    except:
		pass
	    else:
		extensions.append(markdown_extension_numbering.MyExtension(numbering))
		
	    body = markdown.markdown(raw, extensions)
		
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
	return True
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

def acquire_lock():
	while True:
		try:
			lock = Lock.objects.create(id=0)
		except:
			# wait
			print 'waiting for lock'
			time.sleep(1)
		else:
			break
	
	return lock
	
def edit_save(request):
	#try:
	patch_id = request.POST['patch_id']
	raw = request.POST['raw']
	
	raw = raw.replace('\r','')
	
	#print
	#print 'raw',repr(raw)
	#print
	
	patch = Patch.objects.get(pk=patch_id)
	
	# thread safety on git operations
	lock = acquire_lock()
	c = apply_diff_3(patch, raw)
	lock.delete()

        patch.commit_edit = c
	print 'patch.commit_edit', patch.commit_edit
        
        patch.save()

	return HttpResponseRedirect('{}'.format(patch.page.path))
	
	#except Exception as e:
	#	#return HttpResponse(str(e))
	#	raise e
	pass

@user_passes_test(lambda u: u.is_superuser)
def process_data(request):
	# call
	django.core.management.call_command('process_data')
	
	# redirect
	page_id = request.POST['page_id']
	page = Page.objects.get(pk=page_id)
	return HttpResponseRedirect('{}'.format(page.path))
	
@login_required
def edit(request):
	if not (request.method == 'POST'):
		return HttpResponseNotFound()

	try:
		patch_id = request.POST['patch_id']
	except:
		patch_id = None
		#return HttpResponseNotFound()

	patch = Patch.objects.get(pk=patch_id)

	#print 'orig',repr(patch.orig)
	
	c = {
		'path': patch.page.path,
		'patch_id': patch.id,
		'raw': patch.orig,
		}

	return render(request, 'wiki/edit.html', c)

@login_required	
def page_static(request, path0):
	
	path = os.path.normpath(path0)
	
	dir = os.path.dirname(path)
	
	build_path = os.path.join(settings.WIKI_BLD_ROOT, path)
	
	with open(build_path, 'r') as f:
		html = f.read()
	
	return HttpResponse(html)
	
@login_required	
def page(request, path0):
	
	path = os.path.normpath(path0)
	
	try:
		page = Page.objects.get(path=path0)
	except Exception as e:
		page = Page()
		page.path = path0
		page.save()
		#return HttpResponse(str(e))
	
	
	dir = os.path.dirname(path)
	
	build_path = os.path.join(settings.WIKI_BLD_ROOT, path)
	source_path = os.path.join(settings.WIKI_SRC_ROOT, path + '.md')
	
	body = get_build(source_path, build_path)
	
	# file data
	j_data = wiki.util.get_data_file(source_path)
	
	# get HEAD commit string
	r = git.Repo(settings.WIKI_SRC_ROOT)
	s = r.head.commit.__str__()
	
	# create a new Patch object
	patch = Patch()
	patch.user = request.user
	patch.page = page
	patch.orig = get_contents(source_path)
	patch.commit_orig = s
	patch.save()
	
	h,t = os.path.split(os.path.dirname(path0))
	
	child_list = wiki.util.child_link_html(dir)
	sibling_list = wiki.util.sibling_link_html(dir)
	
	parent_href = '/' + h + '/index' if h else '/index'
	
	print 'path0  {}'.format(path0)
	print 'path   {}'.format(path)
	print 'dir    {}'.format(dir)
	print 'parent {}'.format(parent_href)
	print 'j data {}'.format(repr(j_data))
	
	#print 'commit=', s
	#print 'orig',repr(patch.orig)
	
	c = {
		'page':			page,
		'path':         path0,
		'patch_id':     patch.id,
		'body':         body,
		'child_list':   child_list,
		'sibling_list': sibling_list,
		'parent_href':  parent_href,
		'user':         request.user,
		}

	return render(request, 'wiki/page.html', c)

def test(request):
	
	l = Lock.objects.create(id=0)
	print 'created id={}'.format(l.id)
	time.sleep(5)
	
	i = l.id
	
	l.delete()
	
	return HttpResponse("success<br>{}".format(i))

def register(request):
    if request.method == 'POST':
        nxt = request.POST['next']

        form = wiki.forms.Register(request.POST)
    
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data['username'],
                form.cleaned_data['email'],
                form.cleaned_data['pass0'],)
        
            print 'register success'

            return HttpResponse('register success')
                    
            return HttpResponseRedirect(
                    '/accounts/login?next={}'.format(nxt))
        else:
            print 'register failure'
    else:
        print 'register start'
        form = wiki.forms.Register()
        nxt = request.GET['next']

    c = {
                'form': form,
                'next': nxt,
                }
    return render(request, 'registration/register.html', c)




