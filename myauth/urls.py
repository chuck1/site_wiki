from django.contrib.auth import views as auth_views
from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^login/$', auth_views.login),
	url(r'^register/$', views.register),
	url(r'^(\d+)/confirmation/$', views.confirmation, name='confirmation'),
	]

