from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Page(models.Model):
	path = models.CharField(max_length=200)
	
	def __unicode__(self):
		return 'Page object path={}'.format(repr(self.path))

class Patch(models.Model):
	page = models.ForeignKey(Page)
        user = models.ForeignKey(User)
	commit_orig = models.CharField(max_length=200)
	orig = models.TextField()
	commit_edit = models.CharField(max_length=200)

        def __unicode__(self):
            if self.commit_edit:
                s = 'Patch object {} {}..{}'.format(
                    self.page.path,
                    self.commit_orig[:8],
                    self.commit_edit[:8])
            else:
                s = 'Patch object {} {}'.format(
                    self.page.path,
                    self.commit_orig[:8])
            return s

class Lock(models.Model):
	def __unicode__(self):
		return 'Lock object id={}'.format(self.id)
