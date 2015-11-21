from django.core.urlresolvers import reverse

import xml.etree.ElementTree as ET

def task_tree_insert(tree, line):
	
	if not line:
		return
	
	first = line.pop(0)
	
	try:
		tree = tree[first]
	except KeyError as e:
		tree[first] = dict()
		tree = tree[first]
	
	task_tree_insert(tree, line)
	
def task_tree(tasks):
	
	tree = {}
	
	for t in tasks:
		line = t.get_task_line()
	
		task_tree_insert(tree, line)
	
	return tree

def func_item(e, d):
	e = ET.SubElement(e, 'tr')
	e = ET.SubElement(e, 'td')
	e.attrib['class'] = 'item'
	e.attrib['style'] = "padding-left:{}px".format(d*20)
	return e

def func(i, e):
	t = ET.SubElement(e, 'table')
	tr = ET.SubElement(t, 'tr')

	td = ET.SubElement(tr, 'td')
	td.text = str(i)

	td = ET.SubElement(tr, 'td')
	f = ET.SubElement(td, 'form')
	f.attrib['action'] = reverse('task_edit', args=[i.id])
	ip = ET.SubElement(f, 'input')
	ip.attrib['type'] = 'submit'
	ip.attrib['value'] = 'edit'

	td = ET.SubElement(tr, 'td')
	f = ET.SubElement(td, 'form')
	f.attrib['action'] = reverse('task_create', args=[i.id])
	ip = ET.SubElement(f, 'input')
	ip.attrib['type'] = 'submit'
	ip.attrib['value'] = 'create child'

def element_tree(tree, c = None, d = 0):
	
	if c is None:
		c_null = True
		c = ET.Element('table')
		c.attrib['class'] = 'task_list'
	else:
		c_null = False
	
	for i, subtree in tree.items():
		e = func_item(c, d)
		
		if func:
			func(i, e)
		else:
			e.text = str(i)
		
		if subtree:
			element_tree(subtree, c, d+1)

	if c_null:
		return ET.tostring(c)

