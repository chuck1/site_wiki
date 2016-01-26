from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse

import numpy
import matplotlib as mpl
import matplotlib.cm as cm

import xml.etree.ElementTree as ET

# Create your views here.

import task.util

from .models import Task
from .forms import TaskEditForm, TaskCreateForm

@login_required
def task_list(request):
	user = request.user
	
	tasks_create = user.task_create.all()
	tasks_shared_with = user.task_shared_with.all()
	
	lst = list(tasks_create) + list(tasks_shared_with)
	
        lst = filter(lambda x: x.is_open(), lst)

        priority = [x.priority for x in lst]

	tree = task.util.task_tree(lst)

	print 'task list'
	print 'user ',user
	print 'tasks',len(lst)
        print("priority", priority, numpy.max(priority))
	
        sg = task.util.StyleGenerator(cm.Reds, cm.Greens, numpy.max(priority), 0.8)

	el = task.util.element_tree(None, tree, sg)
	
        return render(request, 'task/task_list.html', {'tree_html': el, 
            'next': '/task/task_list'})

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
		priority = form.cleaned_data['priority']
                bool_wait_for_feedback = form.cleaned_data["bool_wait_for_feedback"]
                parent = form.cleaned_data["parent"]

		task.name = name
		task.priority = priority
		task.bool_wait_for_feedback = bool_wait_for_feedback
                task.parent = parent
		task.save()

		return HttpResponseRedirect(reverse('task_list'))
	    else:
		return render(request, 'task/task_edit.html', {
			'form':form, 'task':task})
	
        form = TaskEditForm(initial={
            'name':task.name,
            'priority':task.priority,
            "bool_wait_for_feedback":task.bool_wait_for_feedback,
            "parent":task.parent})

	return render(request, 'task/task_edit.html', {'form':form, 'task':task})

@login_required
def task_set_hide_children(request, task_id, val):

    task = get_object_or_404(Task, pk=task_id)
    
    task.hide_children = bool(int(val))
    task.save()

    return HttpResponseRedirect(reverse('task_list'))

@login_required
def task_action(request, task_id, ac):

    task = get_object_or_404(Task, pk=task_id)
    
    task.action(ac, request.user)

    return HttpResponseRedirect(reverse('task_list'))
   
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
		priority = form.cleaned_data['priority']
                bool_wait_for_feedback = form.cleaned_data["bool_wait_for_feedback"]

		task = Task()
		task.name = name
	        task.priority = priority
                task.bool_wait_for_feedback = bool_wait_for_feedback
		task.user_create = user
		task.parent = parent_task
		task.save()

		print 'create task'
		print 'name       ', name
		print 'user_create', user
		print 'parent     ', parent_task


		return HttpResponseRedirect(reverse('task_list'))
	    else:
		return render(request, 'task/task_create.html', {
			'form':form, 'parent_task':parent_task})

	form = TaskCreateForm()

	return render(request, 'task/task_create.html', {
		'form':form, 'parent_task':parent_task})


def calc_styles(n):

    #norm = mpl.colors.Normalize(vmin=-20, vmax=10)
    #cmap = cm.hot
    #x = 0.3
    #m = cm.ScalarMappable(norm=norm, cmap=cmap)
    #print m.to_rgba(x)

    #cmap = cm.hot
    cmap = cm.Reds

    x1 = 0.8

    colors = [cmap(x) for x in numpy.linspace(0,x1,n)]
    #colors = [cmap(x) for x in numpy.linspace(1,0,n)]
   
    print("colors",colors)

    R = (numpy.array([c[0] for c in colors])*255).astype(int)
    G = (numpy.array([c[1] for c in colors])*255).astype(int)
    B = (numpy.array([c[2] for c in colors])*255).astype(int)

    print("r",R)

    R = ["{:02X}".format(x) for x in R]
    G = ["{:02X}".format(x) for x in G]
    B = ["{:02X}".format(x) for x in B]
    
    print("r",R)
   
    styles = ["#"+r+g+b for r,g,b in zip(R,G,B)]

    return styles

def debug(request):
   
    styles = calc_styles(7)

    print("styles",styles)

    return render(request, "task/debug.html", {"styles":styles})


