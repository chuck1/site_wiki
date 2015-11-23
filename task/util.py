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

def func(parent, i, e, d):
	#t = ET.SubElement(e, 'table')
	tr = ET.SubElement(e, 'tr')
        
        if parent is not None:
            tr.attrib['data-parent-id'] = str(parent.id)
        tr.attrib['data-id'] = str(i.id)
        tr.attrib['data-depth'] = str(d)

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

        td = ET.SubElement(tr, 'td')
	f = ET.SubElement(td, 'form')
	f.attrib['action'] = reverse('task_action', args=[i.id, 'close'])
	ip = ET.SubElement(f, 'input')
	ip.attrib['type'] = 'submit'
	ip.attrib['value'] = 'close'

        td = ET.SubElement(tr, 'td')
       	f = ET.SubElement(td, 'form')
	f.attrib['action'] = reverse('task_set_hide_children', args=[i.id, '1'])
        ip = ET.SubElement(f, 'input')
	ip.attrib['type'] = 'submit'
        ip.attrib['value'] = '-'
        #ip.attrib['onclick'] = "collapse(this, true)"
        ip.attrib['data-id'] = str(i.id)

        td = ET.SubElement(tr, 'td')
       	f = ET.SubElement(td, 'form')
	f.attrib['action'] = reverse('task_set_hide_children', args=[i.id, '0'])
        ip = ET.SubElement(f, 'input')
	ip.attrib['type'] = 'submit'
        ip.attrib['value'] = '+'
        #ip.attrib['onclick'] = "collapse(this, false)"
        ip.attrib['data-id'] = str(i.id)

	td = ET.SubElement(tr, 'td')
	td.text = str(i)
	td.attrib['style'] = "padding-left:{}px".format(d*20)


def element_tree(parent, tree, c = None, d = 0):
	
        #if parent:
        #    print 'parent',parent.id

	if c is None:
		c_null = True
		c = ET.Element('table')
		c.attrib['class'] = 'task_list'
	else:
		c_null = False
	
	for task, subtree in tree.items():
	    #e = func_item(c, d)
	    
            func(parent, task, c, d)
	    
	    if subtree:
                if not task.hide_children:
		    element_tree(task, subtree, c, d+1)

	if c_null:
	    return ET.tostring(c,method='html')

