from django.contrib import admin

# Register your models here.

from .models import Task, TaskEvent

admin.site.register(Task)
admin.site.register(TaskEvent)

