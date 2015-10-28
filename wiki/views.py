import os
import markdown
import time
import git

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from .models import Page, Branch

# Create your views here.

root = '/home/chuck/site_wiki'
source_root = os.path.join(root, 'source')
build_root = os.path.join(root, 'build')

def get_build(src, dst):
    if requires_update(src, dst):
        print 'rebuilding'

        raw = get_contents(src)

        body = markdown.markdown(raw)

        with open(dst, 'w') as f:
            f.write(body)
    else:
        with open(dst, 'r') as f:
            body = f.read()

    return body

def get_mtime(path):
    try:
        return time.ctime(os.path.getmtime(path))
    except IOError:
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass
        
        with open(path, 'w') as f:
            pass
    
        return time.ctime(os.path.getmtime(path))
   

def requires_update(src, dst):
    s = get_mtime(src)
    d = get_mtime(dst)
    return s > d


def get_contents(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except IOError:
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass
        
        with open(path, 'w') as f:
            pass
    
        return ''

def edit(request):
    if not (request.method == 'POST'):
        return HttpResponseNotFound()

    try:
        branch_id = request.POST['branch_id']
    except:
        return HttpResponseNotFound()

    return HttpResponse('branch_id = {}'.format(branch_id))

def page(request):

    print 'page view'

    try:
        path = request.GET['p']
    except:
        return HttpResponseNotFound()
    
    print 'path=',path
    
    try:
        page = Page.objects.get(path=path)
    except:
        return HttpResponseNotFound()
    
    print 'page=',page
    
    build_path = os.path.join(build_root, path)
    source_path = os.path.join(source_root, path)

    body = get_build(source_path, build_path)

    # get HEAD commit string
    r = git.Repo(source_root)
    s = r.head.commit.__str__()

    print 'commit=', s

    # create a new Branch object
    b = Branch()
    b.save()

    c = {
            'path': path,
            'commit': s,
            'branch_id': b.id,
            'body': body,
            }

    return render(request, 'wiki/page.html', c)



