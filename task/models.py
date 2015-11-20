from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Task(models.Model):
	name = models.CharField(max_length=128)
	parent = models.ForeignKey('Task', blank=True, null=True)
	
	user_create = models.ForeignKey(User, related_name='tasks_create')
	user_assign = models.ForeignKey(User, related_name='tasks_assign', blank=True, null=True)
	
	user_shared_with = models.ManyToManyField(User, 
		related_name='tasks_shared_with', blank=True)

	def __unicode__(self):
		return self.name

	def get_task_root(self):
		if self.parent is not None:
			return self.parent.get_task_root()
		else:
			return self
	
	def get_task_line(self):
		line = []
		if self.parent is not None:
			line = self.parent.get_task_line()
		line.append(self)
		return line
