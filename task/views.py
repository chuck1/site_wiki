from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse


import xml.etree.ElementTree as ET

# Create your views here.

import task.util

from .models import Task
from .forms import TaskEditForm, TaskCreateForm

@login_required
def task_list(request):
	user = request.user
	
	#tasks = Task.objects.get(user_create=user)
	
	#tasks_create = user.tasks_create.all()
	#tasks_shared_with = user.tasks_shared_with.all()
	tasks_create = user.tasks_create.filter(status=Task.STATUS_STARTED)
	tasks_shared_with = user.tasks_shared_with.filter(status=Task.STATUS_STARTED)
	
	lst = list(tasks_create) + list(tasks_shared_with)
	
	tree = task.util.task_tree(lst)

	print 'task list'
	print 'user ',user
	print 'tasks',len(lst)
	
	#print tree


	#el = task.util.element_tree(tree, 'ul', task.util.func_item_1, func)
	el = task.util.element_tree(None, tree)
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
	
        form = TaskEditForm(initial={'name':task.name})

	return render(request, 'task/task_edit.html', {'form':form, 'task':task})

@login_required
def task_set_hide_children(request, task_id, val):

    task = get_object_or_404(Task, pk=task_id)
    
    task.hide_children = bool(int(val))
    task.save()

    return HttpResponseRedirect('/task/task_list')

@login_required
def task_action(request, task_id, ac):

    task = get_object_or_404(Task, pk=task_id)
    
    task.action(ac, request.user)

    return HttpResponseRedirect('/task/task_list')
    
   
@login_required
def task_create(request, parent_task_id):

	parent_task = get_object_or_404(Task, pk=parent_task_id)
	user = request.user
	if not (user == parent_task.user_create):
		return HttpResponse('Error')

	if request.method == 'POST':

		form = TaskCreateForm(request.POST)
		
		if form.is_valid():

			name = form.cleaned_data['name']

			task = Task()
			task.name = name
			task.user_create = user
			task.parent = parent_task
			task.save()

			print 'create task'
			print 'name       ', name
			print 'user_create', user
			print 'parent     ', parent_task


			return HttpResponseRedirect('/task/task_list')
		else:
			return render(request, 'task/task_create.html', {
				'form':form, 'parent_task':parent_task})

	form = TaskCreateForm()

	return render(request, 'task/task_create.html', {
		'form':form, 'parent_task':parent_task})





