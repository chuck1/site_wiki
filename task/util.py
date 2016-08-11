from django.core.urlresolvers import reverse
from django.conf import settings

from .models import Task

import xml.etree.ElementTree as ET
import pytz
import numpy

class StyleGenerator(object):
    def __init__(self, cm0, cm1, priority_max, scale):
        self.cm0 = cm0
        self.cm1 = cm1
        self.p_max = priority_max
        self.scale = scale

    def bg(self, task):
        if self.p_max == 0:
            x = 0
        else:
            x = float(task.priority) / float(self.p_max) * self.scale

        if task.bool_wait_for_feedback:
            c = self.cm1(x)[:3]
        else:
            c = self.cm0(x)[:3]
        
        s = "#" + "".join(["{:02X}".format(x) for x in (numpy.array(c)*255).astype(int)])
        
        return s


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

def task_line_hidden(line):
    for l in line[:-1]:
        if not l.is_open():
            return True
    return False

def task_tree(tasks):
	
	tree = {}
	
	for t in tasks:
	    line = t.get_task_line()
	    
            if task_line_hidden(line):
                continue

	    task_tree_insert(tree, line)
	
	return tree

def func_item(e, d):
	e = ET.SubElement(e, 'tr')
	e = ET.SubElement(e, 'td')
	e.attrib['class'] = 'item'
	e.attrib['style'] = "padding-left:{}px".format(d*20)
	return e

def table_datetime_start(tr, i):
        # datetime end
        td = ET.SubElement(tr, 'td')
        dt = i.get_datetime_start()

        if dt is not None:
            dt2 = dt.astimezone(pytz.timezone(settings.TIME_ZONE))
            td.text = dt2.strftime("%Y/%m/%d %H:%M")
            #td.text = repr()

def table_datetime_end(tr, i):
        # datetime end
        td = ET.SubElement(tr, 'td')
        dt = i.get_datetime_end()

        if dt is not None:
            dt2 = dt.astimezone(pytz.timezone(settings.TIME_ZONE))
            td.text = dt2.strftime("%Y/%m/%d %H:%M")
            #td.text = repr()

def func(parent, i, e, d, styleGen):
	#t = ET.SubElement(e, 'table')
	tr = ET.SubElement(e, 'tr')
        
        if parent is not None:
            tr.attrib['data-parent-id'] = str(parent.id)
        tr.attrib['data-id'] = str(i.id)
        tr.attrib['data-depth'] = str(d)

	td = ET.SubElement(tr, 'td')
        td.text = str(i.id)

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


        if not i.hide_children:
            td = ET.SubElement(tr, 'td')
            f = ET.SubElement(td, 'form')
    	    f.attrib['action'] = reverse('task_set_hide_children', args=[i.id, '1'])
            ip = ET.SubElement(f, 'input')
    	    ip.attrib['type'] = 'submit'
            ip.attrib['value'] = '-'
            #ip.attrib['onclick'] = "collapse(this, true)"
            ip.attrib['data-id'] = str(i.id)
        else:
            td = ET.SubElement(tr, 'td')
            f = ET.SubElement(td, 'form')
    	    f.attrib['action'] = reverse('task_set_hide_children', args=[i.id, '0'])
            ip = ET.SubElement(f, 'input')
            ip.attrib['type'] = 'submit'
            ip.attrib['value'] = '+'
            #ip.attrib['onclick'] = "collapse(this, false)"
            ip.attrib['data-id'] = str(i.id)

        table_datetime_start(tr, i)
        table_datetime_end(tr, i)

	td = ET.SubElement(tr, 'td')
	
        #td.text = str(i)
	td.text = i.name

        td.attrib['style'] = "padding-left:{}px;background-color:{}".format(
                d*20, styleGen.bg(i))


def element_tree(parent, tree, styleGen, c = None, d = 0):
	
        #if parent:
        #    print 'parent',parent.id

	if c is None:
		c_null = True
		c = ET.Element('table')
		c.attrib['class'] = 'task_list'
	else:
		c_null = False
        
        def task_cmp(t1, t2):
            #if t1.datetime_create != t2.datetime_create:
            return cmp(t1.datetime_create, t2.datetime_create)

        items = sorted(tree.items(), cmp=task_cmp, key=lambda i: i[0])

	for task, subtree in items:
	    #e = func_item(c, d)
	    
            func(parent, task, c, d, styleGen)
	    
	    if subtree:
                if not task.hide_children:
		    element_tree(task, subtree, styleGen, c, d+1)

	if c_null:
	    return ET.tostring(c,method='html')

