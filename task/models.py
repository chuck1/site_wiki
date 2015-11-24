from django.db import models
from django.conf import settings
from django.db.models import Q, Max
from django.utils import timezone

# Create your models here.

print 'task.models', settings.AUTH_USER_MODEL

class Task(models.Model):
	name = models.CharField(max_length=128)

        '''
        STATUS_STARTED='ST'
        STATUS_COMPLETED='CO'
        STATUS_CANCELLED='CA'
        STATUS_CHOICES = (
                (STATUS_STARTED, 'started'),
                (STATUS_COMPLETED, 'completed'),
                (STATUS_CANCELLED, 'cancelled'))
        
        status = models.CharField(max_length=2, choices=STATUS_CHOICES,
                default=STATUS_STARTED, blank=True)
        '''
        parent = models.ForeignKey('Task', blank=True, null=True)
	
        print 'task.models', settings.AUTH_USER_MODEL
	user_create = models.ForeignKey(settings.AUTH_USER_MODEL,
		related_name='task_create')
	user_assign = models.ForeignKey(settings.AUTH_USER_MODEL,
		related_name='task_assign', blank=True, null=True)
	
	user_shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, 
		related_name='task_shared_with', blank=True, through='TaskUserSharedWith')

        hide_children = models.BooleanField(default=False)
        
        datetime_create = models.DateTimeField(auto_now_add=True)
        #datetime_create = models.DateTimeField(default=timezone.now)
        
        def action_close(self):
            #self.status = Task.STATUS_COMPLETED
            #self.save()
    
            te = TaskEvent()
            te.task = self
            te.event_type = TaskEvent.TYPE_CLOSE
            te.save()

            print 'task close',te.event_datetime

        def action(self, ac, user):
            if user != self.user_create:
                raise django.core.exceptions.PermissionDenied()
            
            o = {
                    'close': self.action_close
                    }
            
            o[ac]()

	def is_open(self):
            #q = self.taskevent_set.all()
            #print 'q ',q
            q = self.taskevent_set.filter(
                    Q(event_type=TaskEvent.TYPE_OPEN) | 
                    Q(event_type=TaskEvent.TYPE_CLOSE))
            
            if not q:
                return True

            dt = q.aggregate(Max('event_datetime'))['event_datetime__max']
            q2 = q.filter(event_datetime=dt)
            assert len(q2)==1
            te = q2[0]
            print 'q ',q
            print 'te',te
            b = bool(te.event_type == TaskEvent.TYPE_OPEN)
            print 'b ',b
            return b


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

class TaskEvent(models.Model):
    task = models.ForeignKey(Task)
    TYPE_OPEN = 0
    TYPE_CLOSE = 1
    TYPE_CHOICES = (
            (TYPE_OPEN, 'open'),
            (TYPE_CLOSE, 'close'))
    event_type = models.IntegerField(choices=TYPE_CHOICES)

    event_datetime = models.DateTimeField(auto_now_add=True)

class TaskUserSharedWith(models.Model):
    task = models.ForeignKey('Task')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


