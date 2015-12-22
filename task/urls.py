
from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^debug$', views.debug, name='debug'),
	url(r'^task_list$', views.task_list, name='task_list'),
	url(r'^(\d+)/task_edit$', views.task_edit, name='task_edit'),
	url(r'^(\d+)/task_create$', views.task_create, name='task_create'),
	url(r'^(\d+)/(\w+)/task_action$', views.task_action, name='task_action'),
	url(r'^(\d+)/(\d+)/task_set_hide_children$',
        views.task_set_hide_children, 
        name='task_set_hide_children')]

