from django.contrib import admin

# Register your models here.

from .models import Page, Patch, Lock

admin.site.register(Page)
admin.site.register(Patch)
admin.site.register(Lock)
