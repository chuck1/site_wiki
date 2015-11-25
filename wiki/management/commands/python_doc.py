import os, sys, pydoc

import markdown
import importlib

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import django.template.loader

import wiki.util

def gen(mod_name, output_dir):
	'''
	generate HTML documentation
	'''
        mod_main = importlib.import_module(mod_name)

        mod_list = mod_main.PYDOC_LIST

	mod_dir = os.path.dirname(mod_main.__file__)
	
	d = pydoc.HTMLDoc()
	
	try:
		os.mkdir(output_dir)
	except OSError: pass
	
	for x in mod_list:
		mod = importlib.import_module(x)

		fn = os.path.join(output_dir, x+'.html')
		with open(fn, 'w') as f:
			print 'writing ', fn
			#f.write(d.document(sys.modules[x]))
			f.write(d.document(mod))
	
	# render README.md
	
	with open(os.path.join(mod_dir, 'README.md'), 'r') as f:
		text = f.read()
	
	html = markdown.markdown(text)
	
	with open(os.path.join(output_dir, mod_name +'.'+ 'README.html'), 'w') as f:
		f.write(html)
	

class Command(BaseCommand):
    help = 'help message'
	
    def add_arguments(self, parser):
	parser.add_argument('module_name')
	parser.add_argument('destination_folder')
	parser.add_argument('makrdir', action='store_true')

    def handle(self, *args, **options):
		
	module_name = options['module_name']
	output_dir = options['destination_folder']
        makedir = options['makedir']
	
        if makedir:
            output_dir = os.path.join(output_dir, module_name)

	output_dir = os.path.join(settings.WIKI_BLD_ROOT, output_dir)
		
	print 'module', repr(module_name)
	print 'dest  ', repr(output_dir)
	
	gen(module_name, output_dir)



