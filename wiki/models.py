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
    group = models.ForeignKey(myauth.models.MyGroup)
class PageGroupEdit(models.Model):
    page = models.ForeignKey('Page')
    group = models.ForeignKey(myauth.models.MyGroup)

class Page(models.Model):
    path = models.CharField(max_length=1000)
    
    user_create = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    """
    By default, page permissions inherit permissions of all parent folders (folder
    permission info is currently assumed equal to the index page permissions in that
    folder). So there is a set for each of the following four fields, and each set contains
    the union of the equivalent sets for all ancestors.

    The user fields must act as ORs (thats the only thing that makes sense).
    If the user set is empty, it is ignored.

    The group fields currently act as ANDs. But I plan to split it into an AND and an OR
    field, for both view and edit.
    If the group field is empty, everyone is allowed.
    A group with the special name 'user' can be used. The site interprets this as anyone
    who is logged in.
    """

    users_view = models.ManyToManyField(settings.AUTH_USER_MODEL, 
            related_name = "page_users_view",
            blank = True,
            through = 'PageUserView')
    users_edit = models.ManyToManyField(settings.AUTH_USER_MODEL, 
            related_name = "page_users_edit",
            blank = True,
            through = 'PageUserEdit')
    groups_view = models.ManyToManyField(myauth.models.MyGroup, 
            related_name = "page_groups_view",
            blank = True,
            through = 'PageGroupView')
    groups_edit = models.ManyToManyField(myauth.models.MyGroup, 
            related_name = "page_groups_edit",
            blank = True,
            through = 'PageGroupEdit')
    
    def get_parent_index_filename(self):
        #print 'get_parent_index_filename'
        #print self.path
        h,t = os.path.split(self.path)
        #print repr(h), repr(t)
        if h == '': raise ValueError('no parent')
        h,t = os.path.split(h)
        #print h
        return os.path.join(h, 'index.html')

    def get_parent_index_page(self):
        try:
            p = Page.objects.get(path = self.get_parent_index_filename())
            return p
        except: return None
    
    def get_groups_view(self):
        #print 'get groups view'

        s = set()
        p = self.get_parent_index_page()
        if p:
            s = s.union(p.get_groups_view())
        s = s.union(set(self.groups_view.all()))
        return s

    def check_perm_view(self, user):
        print 'check_perm_view', user
        #print 'parent index'
        #print self.get_parent_index_filename()
        print 'groups'
        s = self.get_groups_view()
        print s
        b = [bool(user in g.users.all()) for g in s]
	print b
        
        print all(b)
        
        return all(b)

    def check_perm_edit(self, user):
        print 'check_perm_edit', user
        return user.is_admin

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
        datetime_create = models.DateTimeField(auto_now_add=True)

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


