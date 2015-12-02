import os
from django.db import models
from django.conf import settings

import myauth.models

class PageUserView(models.Model):
    page = models.ForeignKey('Page')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
class PageUserEdit(models.Model):
    page = models.ForeignKey('Page')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
class PageGroupView(models.Model):
    page = models.ForeignKey('Page')
    group = models.ForeignKey(myauth.models.Group)
class PageGroupEdit(models.Model):
    page = models.ForeignKey('Page')
    group = models.ForeignKey(myauth.models.Group)

class Page(models.Model):
    path = models.CharField(max_length=1000)
    
    user_create = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    
    users_view = models.ManyToManyField(settings.AUTH_USER_MODEL, 
            related_name = "page_users_view",
            blank = True,
            through = 'PageUserView')
    users_edit = models.ManyToManyField(settings.AUTH_USER_MODEL, 
            related_name = "page_users_edit",
            blank = True,
            through = 'PageUserEdit')
    groups_view = models.ManyToManyField(myauth.models.Group, 
            related_name = "page_users_view",
            blank = True,
            through = 'PageGroupView')
    groups_edit = models.ManyToManyField(myauth.models.Group, 
            related_name = "page_users_edit",
            blank = True,
            through = 'PageGroupEdit')

    def check_perm_view(self, user):
        print 'check_perm_view', user
        return True

    def check_perm_edit(self, user):
        print 'check_perm_edit', user
        return True

    def get_build_abspath(self):
        h,e = os.path.splitext(self.path)
        if e == '.html':
            return os.path.join(settings.WIKI_BUILD_DIR, self.path)
    	elif e == '.png':
	    return os.path.join(settings.WIKI_SEMISTATIC_DIR, self.path)
        else:
            raise ValueError(self.path)
        '''
        elif e == '':
            # for old paths that didnt save .html extension
            return os.path.join(settings.WIKI_BUILD_DIR, path)
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


