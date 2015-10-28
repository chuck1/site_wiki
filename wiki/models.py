from django.db import models

# Create your models here.

class Page(models.Model):
    path = models.CharField(max_length=200)

class Branch(models.Model):
    """
    """
    pass

