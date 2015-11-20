
from django.conf.urls import url

from . import views

urlpatterns = [
		url(r'^task_list$', views.task_list, name='task_list'),
		url(r'^(\d+)/task_edit$', views.task_edit, name='task_edit'),
		]

