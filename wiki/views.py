import pdfkit
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
import django.core.urlresolvers
from django.utils.encoding import smart_str
from django.core.servers.basehttp import FileWrapper

from .models import Page, Patch, Lock
import wiki.forms
import wiki.util
import wiki.search
from .forms import SearchForm, CreateFolderForm, CreateFileForm

for p in sys.path: print p

# markdown extensions
import markdown.extensions.tables
# custom
import markdown_extension_blockmod
import markdown_extension_link
import markdown_extension_numbering
import markdown_extension_equation_block

####################################################

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
	
        r.git.execute(['git', 'add', npath_noex + e_s])
	#r.git.execute(['git', 'add', npath])
	#r.git.execute(['git', 'add', diffs[0].a_path])
        try:
	    r.git.execute(['git', 'commit', '-m', '\'auto for {}\''.format(path)])
        except git.GitCommandError as e:
            # if nothing to commit, exit
            return
	
	r.git.execute(['git', 'checkout', 'master'])
	
	branch_name = 'auto_{}'.format(patch.id)
        
        commit_message = "auto merge for '{}' user='{}'".format(
                'auto_{}'.format(patch.id),
                str(patch.user))
	
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

def get_build(src, dst, path_rel_build, force_update=False):
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
            
            prefix = django.core.urlresolvers.get_script_prefix()
            print "get_script_prefix", repr(prefix)

            extensions=[
        		markdown.extensions.tables.TableExtension(),
        		markdown_extension_blockmod.MyExtension(),
        		markdown_extension_link.MyExtension(prefix),
        		markdown_extension_equation_block.MyExtension(),
                        ]
        	
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
        o,e = None, None
        if requires_update(src, dst) or force_update:
            folder = os.path.dirname(dst)
            try:
                os.makedirs(folder)
            except:
                pass
            
            print "building", repr(src)
            p = subprocess.Popen(["dot", "-Tpng", "-o"+dst, src], 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o,e = p.communicate()
        
        prefix = django.core.urlresolvers.get_script_prefix() + 'wiki/'
        
        body = ""
        if o:
            body += o+"<br>"
        if e:
            body += e+"<br>"
        body += '<img src="{}{}">'.format(prefix, path_rel_build)

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
    #print
    #print 'requires_update'
    #print src
    #print dst
    #print s
    if os.path.exists(dst):
        d = os.path.getmtime(dst)
        #print d
    else:
        return True
    #print s > d
    #print
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

        if c is None:
            # nothing was commited
            print "nothing to commit"
            pass
        else:
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

@user_passes_test(lambda u: u.is_admin)
def commit_all(request):
    path = request.POST['path']
    django.core.management.call_command('commit_all', 
            'manual commit all from page "{}"'.format(path))
    return HttpResponseRedirect('{}'.format(path))
    
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
        
        prefix = django.core.urlresolvers.get_script_prefix() + 'wiki/'

        href = prefix + h + '/index.html' if h else '/wiki/index.html'
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

    links.insert(0, "<a href=\"{}\">{}</a>".format(prefix+"index.html","home"))

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
        #print '        CONTENT_TYPE', request.META['CONTENT_TYPE']
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
        
        prefix = django.core.urlresolvers.get_script_prefix()

        # check permissions
        if not page.check_perm_view(request.user):
            if request.user.is_anonymous():

                # setting contains prefix
                href = settings.LOGIN_URL
                print "redirecting to {}".format(href)
                return redirect('{}?next={}'.format(href, request.path))
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

        print "GET", request.GET

        build = False
        if "build" in request.GET:
            build = True

	body = get_build(source_path, build_path, path, build)
	
	# file data
	j_data = wiki.util.get_data_file(source_path)
	
	# get HEAD commit string
	r = git.Repo(settings.WIKI_SOURCE_DIR)
	s = r.head.commit.__str__()
        ret = r.git.execute(["git","status"])

        is_dirty=False
        if not "nothing to commit, working directory clean" in ret:
            print "GIT REPO IS DIRTY"
            is_dirty = True


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
                'is_dirty':     is_dirty,
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
            
            #print 'create folder'
            #print path
            
 	    django.core.management.call_command('makedirs', path)
            
            href = django.core.urlresolvers.get_script_prefix() + os.path.join('wiki', 
                    parent_path, relpath, 'index.html')

	    return HttpResponseRedirect(href)
       	else:
            return render(request, 'wiki/folder_create.html', 
                    {'form':form, 'path':parent_path})
 
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
            
            #print 'create file'
            #print path
            
 	    django.core.management.call_command('touch', path)

            href = django.core.urlresolvers.get_script_prefix() + os.path.join('wiki', 
                    parent_path, relpath)
            
	    return HttpResponseRedirect(href)
       	else:
            return render(request, 'wiki/file_create.html', {'form':form, 'path':parent_path})
 
    form = CreateFileForm()
    
    parent_path = request.GET['path']

    return render(request, 'wiki/file_create.html', {'form':form, 'path':parent_path})

@login_required
def page_download_pdf(request, page_id):

        page = Page.objects.get(pk=page_id)

	path = page.path
        
        path_noex, ex = os.path.splitext(path)
        
        source_path = os.path.join(settings.WIKI_SOURCE_DIR,
                path_noex + wiki.util.convert_ext_b2s(ex))

        build_path = page.get_build_abspath()
        #build_path = os.path.join(settings.WIKI_BLD_ROOT, path)
	
        dirname = os.path.dirname(path)

        #print "GET", request.GET

	body = get_build(source_path, build_path, path, False)

        c = {
                #'is_dirty':     is_dirty,
                #'link_list':    ll,
		'page':		page,
                #'permission_edit': permission_edit,
                #'folder':       dir,
		#'path':         path0,
		#'patch_id':     patch.id,
		'body':         body,
		#'child_list':   child_list,
		#'sibling_list': sibling_list,
		#'parent_href':  parent_href,
		'user':         request.user,
		}

        res = render(request, 'wiki/page.html', c)
        
        html = res.content

        path_build = os.path.join(settings.WIKI_SEMISTATIC_DIR, path_noex + ".pdf")

        dir_build = os.path.dirname(path_build)

        try:
            os.makedirs(dir_build)
        except: pass

        print "path_build =", path_build

        try:
            os.remove(path_build)
        except Exception as e:
            print "remove file failed"
            print e
        else:
            print "remove file success"

        if 1:
            pdfkit.from_string(html, path_build, options={"--redirect-delay":10000})
        else:
            path_temp = os.path.join(settings.WIKI_SEMISTATIC_DIR, "temp")
            with open(path_temp, "w") as f:
                f.write(html)
        
            cmd = ["wkhtmltopdf", path_temp, path_build]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o,e = p.communicate()
        
            print "o",o
            print "e",e
       
        prefix = django.core.urlresolvers.get_script_prefix()
        href = prefix + "wiki/" + path

        print "href =", href

        f = open(path_build, "r")
        myfile = django.core.files.File(f)

        response = HttpResponse(FileWrapper(myfile), 
                content_type='application/force-download')
        #response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str("filename.pdf")
        #response['X-Sendfile'] = smart_str(path_build)

        return response

        return HttpResponseRedirect(href)

@login_required
def patch_list(request):

    patches = list(Patch.objects.all())

    def f(p):
        return bool(p.commit_edit)

    patches = filter(f, patches)

    patches = sorted(patches, key=lambda x: x.datetime_create, cmp=lambda x,y: cmp(y,x))

    patches = patches[:100]

    return render(request, "wiki/patch_list.html", {"patches":patches})

