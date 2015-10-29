from django.db import models

# Create your models here.

class Page(models.Model):
	path = models.CharField(max_length=200)
	
	def __unicode__(self):
		return 'Page object path={}'.format(repr(self.path))

class Patch(models.Model):
	page = models.ForeignKey(Page)
	commit_orig = models.CharField(max_length=200)
	orig = models.TextField()
	commit_edit = models.CharField(max_length=200)

class Lock(models.Model):
	def __unicode__(self):
		return 'Lock object id={}'.format(self.id)
