
from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'^(\d+)/sheet$', views.sheet, name="sheets_sheet")
       	]



