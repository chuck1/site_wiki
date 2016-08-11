from django.db import models
from django.conf import settings
from django.db.models import Q, Max
from django.utils import timezone

class Task(models.Model):
	name = models.CharField(max_length=128)
        
        priority = models.IntegerField(default=0)
        
        notes = models.TextField()

        bool_wait_for_feedback = models.BooleanField(default=False)
        
        parent = models.ForeignKey('Task', blank=True, null=True)
	

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
            #print 'q ',q
            #print 'te',te
            b = bool(te.event_type == TaskEvent.TYPE_OPEN)
            #print 'b ',b
            return b

        def get_event2(self, q):
            """
            get the event matching q for this task with the greatest event_datetime
            """
            q = self.taskevent_set.filter(q)
            
            if not q: return None

            dt = q.aggregate(Max('event_datetime'))['event_datetime__max']
            q2 = q.filter(event_datetime=dt)

            return q2[0]

        def get_event(self, event_type):
            """
            get the event of type event_type for this task with the greatest event_datetime
            """
            q = self.taskevent_set.filter(Q(event_type=event_type))
            
            if not q: return None

            dt = q.aggregate(Max('event_datetime'))['event_datetime__max']
            q2 = q.filter(event_datetime=dt)

            return q2[0]

        def get_datetime_end(self):
            """
            find datetime_end or duration event with greatest event_datetime
            if it is a duration event, use start to calculate end
            
            """

            q = Q(event_type=TaskEvent.TYPE_DATETIME_END) | Q(event_type=TaskEvent.TYPE_DURATION)

            ev = self.get_event2(q)
            
            if ev is None: return None

            if ev.event_type == TaskEvent.TYPE_DURATION:
                start = self.get_datetime_start()
                if start is None:
                    return None
                
                end = start + datetime.timedelta(hours=duration)
                
                if end.hour > 16:
                    end = end + datetime.timedelta(hours=15)

                if end.weekday() > 4:
                    end = end + datetime.timedelta(days=2)

                return 

            elif ev.event_type == TaskEvent.TYPE_DATETIME_END:
                return ev.datetime

        def get_datetime_start(self):
            ev = self.get_event(TaskEvent.TYPE_DATETIME_START)

            if ev is not None:
                return ev.datetime

            self.get_precedents()


        def get_precedents(self):

            p = []

            query = self.taskevent_set.filter(Q(event_type=TaskEvent.TYPE_PRECEDENT_ADD)|Q(event_type=TaskEvent.TYPE_PRECEDENT_REMOVE)).order_by("event_datetime")
            
            if not query: return
            
            print "precedents"
            for e in query:
                if e.event_type == TaskEvent.TYPE_PRECEDENT_ADD:
                    p.append(e.precedent)

                print e.event_type, "task=", e.precedent
            

	def __unicode__(self):
            #return self.name
            return "{:4} {}".format(self.id,self.name)

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
    TYPE_DATETIME_END = 2
    TYPE_DURATION = 3
    TYPE_DATETIME_START = 4
    TYPE_PRECEDENT_ADD = 5
    TYPE_PRECEDENT_REMOVE = 6
    
    TYPE_CHOICES = (
            (TYPE_OPEN, 'open'),
            (TYPE_CLOSE, 'close'),
            (TYPE_DATETIME_START, 'datetime start'),
            (TYPE_DATETIME_END, 'datetime end'),
            (TYPE_DURATION, 'duration'),
            (TYPE_PRECEDENT_ADD, 'precedent add'),
            (TYPE_PRECEDENT_REMOVE, 'precedent remove'),
            )
    
    event_type = models.IntegerField(choices=TYPE_CHOICES)

    datetime = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    precedent = models.ForeignKey(Task, blank=True, null=True, related_name = "taskevent_precedent")

    event_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.task) + " " + str(self.event_type)

class TaskUserSharedWith(models.Model):
    task = models.ForeignKey('Task')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


