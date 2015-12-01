"""site_wiki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

import myauth.views
import wiki.views
import task.views

urlpatterns = [
    url(r'^accounts/login/$', auth_views.login, name='logout'),
    url(r'^accounts/register/$', myauth.views.register),
    url(r'^accounts/logout/$', myauth.views.logout),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^myauth/',  include('myauth.urls')),
    url(r'^wiki/',  include('wiki.urls')),
    url(r'^task/',  include('task.urls')),
    #url(r'^([\w\/]+)$', wiki.views.page, name='page'),
    #url(r'^([\w\/]+[\w\.]+\.html)$', wiki.views.page_static, name='page_static'),
    ]


