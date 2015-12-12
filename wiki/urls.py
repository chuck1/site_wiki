
from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^commit_all$', views.commit_all, name='wiki_commit_all'),
	url(r'^folder_create$', views.folder_create, name='wiki_folder_create'),
	url(r'^file_create$', views.file_create, name='wiki_file_create'),
	url(r'^search$', views.search, name='wiki_search'),
	url(r'^edit$', views.edit, name='edit'),
	url(r'^(\d+)/page_download_pdf$', views.page_download_pdf, 
            name='wiki_page_download_pdf'),
	url(r'^patch_list$', views.patch_list, name='wiki_patch_list'),
	url(r'^process_data$', views.process_data, name='process_data'),
	url(r'^edit_save$', views.edit_save, name='edit_save'),
	url(r'^test$', views.test, name='test'),
	#url(r'^([\w\/]+)$', views.page, name='page'),
	url(r'^([\w\/]+[\w\.]+\.[\w]+)$', views.page, name='page'),
	url(r'^([\w\/]+[\w\.]+\.html)$', views.page_static, name='page_static'),
	]



