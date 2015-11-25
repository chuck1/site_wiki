from django.db import models
#from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings
from django.core.urlresolvers import reverse
import django.core.mail
from django.utils import timezone

import datetime
import sys
import random
random.seed()

# Create your models here.

class MyUserManager(BaseUserManager):
    def create_user(self, request, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)

        user.is_active = False

        # send email

        print 'request', request.META['HTTP_HOST']

        code = random.randint(0, sys.maxint)
        
        ref = 'http://' + request.META['HTTP_HOST'] + reverse('confirmation', args=[code])
	link = '<a href="{0}">{0}</a>'.format(ref)
        ret = django.core.mail.send_mail('django site confirmation', link,
			'charles.rymal@nortek.com', [user.email], html_message=link,
                        fail_silently=False)
        print 'email',repr(ret)

        # save

        user.save(using=self._db)

        
        # confirmation
        con = Confirmation()
        con.user = user
        con.code = code
        con.expire = timezone.now() + datetime.timedelta(days=1)
        con.save()

        print 'confirm code',con.code

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_active

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Confirmation(models.Model):
    code = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    expire = models.DateTimeField(auto_now_add=True)

