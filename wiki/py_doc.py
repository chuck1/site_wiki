import os, sys, pydoc

import markdown

import experimental_matrix
import experimental_matrix.tests
import experimental_matrix.tests.coil_testing
import experimental_matrix.tests.header_testing

def gen(dir = None):
	'''
	generate HTML documentation
	'''
	
	l = [
		'experimental_matrix',
		'experimental_matrix.tests',
		'experimental_matrix.tests.coil_testing',
		'experimental_matrix.tests.header_testing',
		]
	
	mod_dir = os.path.dirname(experimental_matrix.__file__)
	
	if dir is None:
		dir = os.path.join(mod_dir, 'doc')
	
	d = pydoc.HTMLDoc()
	
	try:
		os.mkdir(dir)
	except OSError: pass
	
	for x in l:
		fn = os.path.join(dir, x+'.html')
		with open(fn, 'w') as f:
			print 'writing ', fn
			f.write(d.document(sys.modules[x]))
	
	# render README.md
	
	with open(os.path.join(mod_dir, 'README.md'), 'r') as f:
		text = f.read()
	
	html = markdown.markdown(text)
	
	with open(os.path.join(dir, 'README.html'), 'w') as f:
		f.write(html)
	
	