from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Page)
admin.site.register(PageGroupView)
admin.site.register(PageGroupEdit)
admin.site.register(Patch)
admin.site.register(Lock)


