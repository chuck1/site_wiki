import os, sys
import markdown
import time
import git
import difflib
import re
import subprocess

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.conf import settings
import django.core.management
import django.core.exceptions

from .models import Page, Patch, Lock
import wiki.forms
import wiki.util
import wiki.search
from .forms import SearchForm, CreateFolderForm, CreateFileForm

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

	r = git.Repo(settings.WIKI_SOURCE_DIR)
	
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
	src_path = os.path.join(settings.WIKI_SOURCE_DIR, npath + '.md')

	r = git.Repo(settings.WIKI_SOURCE_DIR)

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
        
        npath_noex, e_b = os.path.splitext(npath)
        e_s = wiki.util.convert_ext_b2s(e_b)

        
	src_path = os.path.join(settings.WIKI_SOURCE_DIR, npath_noex + e_s)

        print 'ext s ', e_s
        print 'ext b ', e_b
        print 'path s', src_path
	
	r = git.Repo(settings.WIKI_SOURCE_DIR)
	
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

def get_build(src, dst, path_rel_build):
    '''
    get the html for the src file and save it to dst file
    '''
    _,e_s = os.path.splitext(src)

    if e_s == '.md':
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
            
    elif e_s == '.dot':
        if requires_update(src, dst):
            folder = os.path.dirname(dst)
            try:
                os.makedirs(folder)
            except:
                pass

            p = subprocess.Popen(["dot", "-Tpng", "-o"+dst, src])
            p.communicate()

        body = '<img src="/static/{}">'.format(path_rel_build)

    else:
        raise ValueError('invalid source extension')

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
    s = os.path.getmtime(src)
    print
    print 'requires_update'
    print src
    print dst
    print s
    if os.path.exists(dst):
        d = os.path.getmtime(dst)
        print d
    else:
        return True
    print s > d
    print
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
	
	#print
	#print 'raw',repr(raw)
	#print
	
	patch = Patch.objects.get(pk=patch_id)
	
	# thread safety on git operations
	lock = wiki.util.acquire_lock()
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

@user_passes_test(lambda u: u.is_admin)
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

        page = patch.page

        # check permissions
        if not page.check_perm_edit(request.user):
            if request.user.is_anonymous():
                return redirect('{}?next={}'.format(settings.LOGIN_URL, request.path))
            else:
                return HttpResponse("Forbidden")

	#print 'orig',repr(patch.orig)
	
	c = {
		'path': patch.page.path,
		'patch_id': patch.id,
		'raw': patch.orig,
		}

	return render(request, 'wiki/edit.html', c)


def link_list(h):
    links = []

    while True:

        href = '/wiki/' + h + '/index.html' if h else '/wiki/index.html'
        h,t = os.path.split(h)

        '''
        if h and t:
            pass
        else:
            print repr(h),repr(t)
            break
        '''

        links.insert(0, "<a href=\"{}\">{}</a>".format(href,t))

        if not h:
            break

    links.insert(0, "<a href=\"{}\">{}</a>".format("/wiki/index.html","home"))

    return "/".join(links)

@login_required	
def page_static(request, path0):
	
	path = os.path.normpath(path0)
	
	#dir = os.path.dirname(path)
	
	build_path = os.path.join(settings.WIKI_BUILD_DIR, path)
	
	with open(build_path, 'r') as f:
		html = f.read()
	
	return HttpResponse(html)

def read_semistatic_image(path):
    build_static_path = os.path.join(settings.WIKI_SEMISTATIC_DIR, path)
    
    with open(build_static_path, 'rb') as f:
	data = f.read()
    
    return data
 

#@login_required	
def page(request, path0):
        
        print
        print "PAGE ---------------------------------------------------"
        print 'request'
        print '    body     ', repr(request.body)
        print '    path     ', request.path
        print '    path_info', request.path_info
        print '    META'
        print '        CONTENT_TYPE', request.META['CONTENT_TYPE']
        print '        HTTP_ACCEPT ', request.META['HTTP_ACCEPT']
        print '        REMOTE_ADDR ', request.META['REMOTE_ADDR']
        print 
        
        h,e = os.path.splitext(path0)
        

        # handle relative paths for images
        if request.META['HTTP_ACCEPT'][:5] == "image":
            return HttpResponse(read_semistatic_image(path0), content_type="image/png")

        # look for static html files first
        if e == '.html':
            build_static_path = os.path.join(settings.WIKI_SEMISTATIC_DIR, path0)
            #print 'look for', repr(build_static_path)
            if os.path.exists(build_static_path):
	        with open(build_static_path, 'r') as f:
		    html = f.read()
	        return HttpResponse(html)
        
	try:
	    page = Page.objects.get(path=path0)
	except Exception as e:
	    page = Page()
            page.user_create = request.user
	    page.path = path0
	    page.save()
	    #return HttpResponse(str(e))
        
        # check permissions
        if not page.check_perm_view(request.user):
            if request.user.is_anonymous():
                return redirect('{}?next={}'.format(settings.LOGIN_URL, request.path))
            else:
                return HttpResponse("Forbidden")
       
        permission_edit = page.check_perm_edit(request.user)
        
        
	path = os.path.normpath(path0)
        
        path_noex, ex = os.path.splitext(path)
        
        source_path = os.path.join(settings.WIKI_SOURCE_DIR,
                path_noex + wiki.util.convert_ext_b2s(ex))

        build_path = page.get_build_abspath()
        #build_path = os.path.join(settings.WIKI_BLD_ROOT, path)
	
        dir = os.path.dirname(path)
	
	body = get_build(source_path, build_path, path)
	
	# file data
	j_data = wiki.util.get_data_file(source_path)
	
	# get HEAD commit string
	r = git.Repo(settings.WIKI_SOURCE_DIR)
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

        ll = link_list(h)

	c = {
                'link_list':    ll,
		'page':		page,
                'permission_edit': permission_edit,
                'folder':       dir,
		'path':         path0,
		'patch_id':     patch.id,
		'body':         body,
		'child_list':   child_list,
		'sibling_list': sibling_list,
		'parent_href':  parent_href,
		'user':         request.user,
		}

	return render(request, 'wiki/page.html', c)

@login_required	
def test(request):
	
	l = Lock.objects.create(id=0)
	print 'created id={}'.format(l.id)
	time.sleep(5)
	
	i = l.id
	
	l.delete()
	
	return HttpResponse("success<br>{}".format(i))

def process_search_result_for_display(res):
    for lst in res.values():
        for l in lst:
            l[0] = ('{:>5}'.format(l[0])).replace(' ', '&nbsp;')
            s0 = l[1]
            s1 = ''
            c = 0
            for mc in l[2]:
                print 'mc',mc
                s1 += s0[c:mc[0]]
                s1 += '<span class="search_match">' + s0[mc[0]:mc[1]] + '</span>'
                c = mc[1]
            s1 += s0[c:]
            l[1] = s1

@login_required	
def search(request):

    if request.method == 'POST':

	form = SearchForm(request.POST)
	
	if form.is_valid():

	    pattern = form.cleaned_data['pattern']

            results = wiki.search.search(pattern)
            
            process_search_result_for_display(results)

            return render(request, 'wiki/search.html', {'form':form, 
                'results':results.items()})
	else:
	    return render(request, 'wiki/search.html', {'form':form})
    
    form = SearchForm()
    
    return render(request, 'wiki/search.html', {'form':form})


@login_required	
def folder_create(request):

    if request.method == 'POST':

	form = CreateFolderForm(request.POST)

        parent_path = request.POST['path']
	
	if form.is_valid():
            
	    relpath = form.cleaned_data['relpath']
            
            path = os.path.join(settings.WIKI_SOURCE_DIR, parent_path, relpath)
            
            print 'create folder'
            print path
            
 	    django.core.management.call_command('makedirs', path)
            
	    return HttpResponseRedirect(os.path.join('/wiki', parent_path, relpath, 'index'))
       	else:
            return render(request, 'wiki/folder_create.html', {'form':form, 'path':parent_path})
 
    form = CreateFolderForm()
    
    parent_path = request.GET['path']

    return render(request, 'wiki/folder_create.html', {'form':form, 'path':parent_path})

@login_required	
def file_create(request):

    if request.method == 'POST':

	form = CreateFileForm(request.POST)

        parent_path = request.POST['path']
	
	if form.is_valid():
            
	    relpath = form.cleaned_data['relpath']
            
            path = os.path.join(settings.WIKI_SOURCE_DIR, parent_path, relpath)
            
            print 'create file'
            print path
            
 	    django.core.management.call_command('touch', path)
            
	    return HttpResponseRedirect(os.path.join('/wiki', parent_path, relpath))
       	else:
            return render(request, 'wiki/file_create.html', {'form':form, 'path':parent_path})
 
    form = CreateFileForm()
    
    parent_path = request.GET['path']

    return render(request, 'wiki/file_create.html', {'form':form, 'path':parent_path})



