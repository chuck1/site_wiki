from django.contrib import admin

# Register your models here.

from .models import Task, TaskEvent, TaskUserSharedWith

admin.site.register(Task)
admin.site.register(TaskUserSharedWith)
admin.site.register(TaskEvent)

