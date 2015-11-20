from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse


import xml.etree.ElementTree as ET

# Create your views here.

import task.util

from .models import Task
from .forms import TaskEditForm

@login_required
def task_list(request):
	user = request.user
	
	#tasks = Task.objects.get(user_create=user)
	
	tasks_create = user.tasks_create.all()
	tasks_shared_with = user.tasks_shared_with.all()
	
	lst = list(tasks_create) + list(tasks_shared_with)
	
	tree = task.util.task_tree(lst)

	print 'task list'
	print 'user ',user
	print 'tasks',len(lst)
	
	#print tree

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

	el = task.util.element_tree(tree, 'ul', 'li', func)
	#print el
	
	return render(request, 'task/task_list.html', {'tree_html': el})

@login_required
def task_edit(request, task_id):

	task = get_object_or_404(Task, pk=task_id)
	user = request.user
	if not (user == task.user_create):
		return HttpResponse('Error')


	if request.method == 'POST':

		form = TaskEditForm(request.POST)
		
		if form.is_valid():

			name = form.cleaned_data['name']

			task.name = name
			task.save()

			return HttpResponseRedirect('/task/task_list')
		else:
			return render(request, 'task/task_edit.html', {
				'form':form, 'task':task})
		

	form = TaskEditForm()

	return render(request, 'task/task_edit.html', {'form':form, 'task':task})






