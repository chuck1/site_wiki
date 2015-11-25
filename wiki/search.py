import re
import json
import os

import wiki.util

from django.conf import settings

def cmp_mtime(p0, p1):
    if not os.path.isfile(p1):
        return True
    return (os.path.getmtime(p0) > os.path.getmtime(p1))

def grep(source_path, pattern):

    print 'grep'
    print source_path

    pat = re.compile(pattern)

    with open(source_path, 'r') as f:
        lines = f.readlines()

    matched_lines = []
    i = 1
    for line in lines:
        matches = list(pat.finditer(line))
        if matches:
            matched_lines.append([
                i, 
                line,
                [[m.start(), m.end()] for m in matches]])
        i += 1

    print matched_lines

    return matched_lines

def read_grep_lines(filename):
    if not os.path.isfile(filename):
        return {}
    
    with open(filename, 'r') as f:
        j = json.loads(f.read())
    
    return j

def should_update_grep_lines(source_path, grep_path, pattern):
    if cmp_mtime(source_path, grep_path):
        return (True, None)

    j = read_grep_lines(grep_path)

    if pattern in j:
        return (False, j)

    return (True, j)

def update_grep_lines(source_relpath, pattern):
    
    grep_path = os.path.join(settings.WIKI_BLD_DIR, 'search_grep_files', source_relpath)
    source_path = os.path.join(settings.WIKI_SRC_DIR, source_relpath)
    
    b, j = should_update_grep_lines(source_path, grep_path, pattern)

    if b:
        matched_lines = grep(source_path, pattern)
        
        if j is None:
            j = read_grep_lines(grep_path)

        j[pattern] = matched_lines
       
        try:
            os.makedirs(os.path.dirname(grep_path))
        except:
            pass

        with open(grep_path, 'w') as f:
            f.write(json.dumps(j))
    
        return matched_lines
    else:
        return j[pattern]
        
def search(pattern):
    
    search_results = {}

    for source_relpath in wiki.util.glob_source_files():
        lines = update_grep_lines(source_relpath, pattern)
        if lines:
            search_results[os.path.splitext(source_relpath)[0]] = lines

    for f,lst in search_results.items():
        print f, len(lst)
        for l in lst:
            print l[2]

    return search_results






