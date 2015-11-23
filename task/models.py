from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Task(models.Model):
	name = models.CharField(max_length=128)
        
        STATUS_STARTED='ST'
        STATUS_COMPLETED='CO'
        STATUS_CANCELLED='CA'
        STATUS_CHOICES = (
                (STATUS_STARTED, 'started'),
                (STATUS_COMPLETED, 'completed'),
                (STATUS_CANCELLED, 'cancelled'))
        
        status = models.CharField(max_length=2, choices=STATUS_CHOICES,
                default=STATUS_STARTED, blank=True)

        parent = models.ForeignKey('Task', blank=True, null=True)
	
	user_create = models.ForeignKey(User, related_name='tasks_create')
	user_assign = models.ForeignKey(User, related_name='tasks_assign', 
		blank=True, null=True)
	
	user_shared_with = models.ManyToManyField(User, 
		related_name='tasks_shared_with', blank=True)

        hide_children = models.BooleanField(default=False)

        def action_close(self):
            self.status = Task.STATUS_COMPLETED
            self.save()
        def action(self, ac, user):
            if user != self.user_create:
                raise django.core.exceptions.PermissionDenied()
            
            o = {
                    'close': self.action_close
                    }
            
            o[ac]()

	def __unicode__(self):
            return self.name
            #return "{:4} {}".format(self.id,self.name)

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
