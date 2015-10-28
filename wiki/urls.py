
from django.conf.urls import url

from . import views

urlpatterns = [
		url(r'^page$', views.page, name='page'),
		url(r'^edit$', views.edit, name='edit'),
		url(r'^edit_save$', views.edit_save, name='edit_save'),
		]

