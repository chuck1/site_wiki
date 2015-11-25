import django.core.management
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os

import wiki.util

class Command(BaseCommand):
	help = 'help message'
	
	def add_arguments(self, parser):
		#parser.add_argument('poll_id', nargs='+', type=int)
		pass
        
	def handle(self, *args, **options):
		'''
		create file tree

		recursivly descend tree and add all page html to a single string
		'''
		
		def filt(x):
			s = x[-8:]
			assert len(s) == len('data.txt')
			if s == 'data.txt':
				return True
			return False
		
		g = wiki.util.FileListGenerator(filt)
		
		file_list = g()
		
		for f in file_list:
	    	    print f
			
		    output_dir = os.path.dirname(f)
			
		    j = wiki.util.get_data(f)
			
		    print j
		    
                    def pydoc_options(d, name):
                        if name == 'makedir':
                            if 'makedir' in d:
                                return d['makedir']
                            else:
                                return True
                        else:
                            raise ValueError('invalid python_doc option')

		    if 'python_doc' in j:
                        d = j['python_doc']
		        lst = d['modules']
			for l in lst:
                            
			    django.core.management.call_command('python_doc', l,
			        output_dir,
                                makedir=pydoc_options(d, 'makedir'))
			

		
