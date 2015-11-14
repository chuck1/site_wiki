from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os

import wiki.util

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

class Command(BaseCommand):
	help = 'help message'
	
	def add_arguments(self, parser):
		#parser.add_argument('poll_id', nargs='+', type=int)
		pass
        
        def recurse(self, p, tree):

            print 'tree',tree
            print 'p',p

            for f in sorted(tree[1], cmp=file_cmp):
                self.file_list.append(os.path.join(*(p + [f])))
            
            for key in sorted(tree[0].keys()):
                self.recurse(p + [key], tree[0][key])
        

	def handle(self, *args, **options):
		'''
                create file tree

                recursivly descend tree and add all page html to a single string
		'''
	        
                self.file_list = []

                tree = [{},[]]

		for root, dirs, files in os.walk(settings.WIKI_SRC_ROOT):
                    root = os.path.relpath(root, settings.WIKI_SRC_ROOT)
                    #h,t = os.path.split(root)
                    #print repr(h),repr(t),repr(root)
                    if root[:4] != '.git':
		        #print root
                        #print files
                        l = listize(root)
                        print l
                        n = get_node(l, tree)
                        n[1] = files

                self.recurse([], tree)

                for f in self.file_list:
                    print f

                pass


