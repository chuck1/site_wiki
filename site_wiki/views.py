import os, sys
import markdown
import time
import git
import difflib
import re
import subprocess

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.conf import settings
import django.core.management


def home(request):
    return render(request, 'site_wiki/home.html', {})

