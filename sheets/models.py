from django.db import models
from django.conf import settings

# Create your models here.

class Sheet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    port = models.IntegerField(default=-1)

    def get_data(self):
        pass

    def set_data(self):
        pass

    def __unicode__(self):
        return "{}".format(self.id)

