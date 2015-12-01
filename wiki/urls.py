
from django.conf.urls import url

from . import views

urlpatterns = [
		url(r'^folder_create$', views.folder_create, name='wiki_folder_create'),
		url(r'^search$', views.search, name='wiki_search'),
		url(r'^edit$', views.edit, name='edit'),
		url(r'^process_data$', views.process_data, name='process_data'),
		url(r'^edit_save$', views.edit_save, name='edit_save'),
		url(r'^test$', views.test, name='test'),
		url(r'^([\w\/]+)$', views.page, name='page'),
		url(r'^([\w\/]+[\w\.]+\.html)$', views.page_static, name='page_static'),
		]



