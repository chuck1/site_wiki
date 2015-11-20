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

def element_tree(tree, tag_container, tag_item, func = None, c = None):
	
	if c is None:
		c_null = True
		c = ET.Element(tag_container)
	else:
		c_null = False
	
	for i, subtree in tree.items():
		e = ET.SubElement(c, tag_item)
		
		if func:
			func(i, e)
		else:
			e.text = str(i)
		
		if subtree:
			subc = ET.SubElement(e, tag_container)
			
			element_tree(subtree, tag_container, tag_item, func, subc)

	if c_null:
		return ET.tostring(c)

