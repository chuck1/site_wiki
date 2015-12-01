import os
from django.db import models
from django.conf import settings

# Create your models here.

class Page(models.Model):
    path = models.CharField(max_length=1000)
    
    def get_build_abspath(self):
        h,e = os.path.splitext(self.path)
        if e == '.html':
            return os.path.join(settings.WIKI_BLD_DIR, self.path)
    	elif e == '.png':
	    return os.path.join(settings.WIKI_SEMISTATIC_DIR, self.path)
        else:
            raise ValueError(self.path)
        '''
        elif e == '':
            # for old paths that didnt save .html extension
            return os.path.join(settings.WIKI_BLD_DIR, path)
        '''

    def __unicode__(self):
	return 'Page object path={}'.format(repr(self.path))

class Patch(models.Model):
	page = models.ForeignKey(Page)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
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


