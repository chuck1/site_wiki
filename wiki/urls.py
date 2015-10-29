
from django.conf.urls import url

from . import views

urlpatterns = [
		url(r'^edit$', views.edit, name='edit'),
		url(r'^edit_save$', views.edit_save, name='edit_save'),
		url(r'^test$', views.test, name='test'),
		url(r'^([\w\/]+)$', views.page, name='page'),
		]

