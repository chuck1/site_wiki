import django.core.management
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import git
import os
import subprocess
import wiki.util

class Command(BaseCommand):
    help = 'help message'
	
    def add_arguments(self, parser):
	parser.add_argument('message')
	parser.add_argument('locked', action='store_true', default=False, help='already locked')
        
    def handle(self, *args, **options):
	
        if not options['locked']:
            lock = wiki.util.acquire_lock()

        r = git.Repo(settings.WIKI_SOURCE_DIR)
	
	r.git.execute(["git","add","--all"])
	r.git.execute(["git","commit","-m",options['message']])
        
        '''
        print 'commit all'
        p = subprocess.Popen(["git","add","--all"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        o,e = p.communicate()
        #print o
        #print e
        print p.returncode
        p = subprocess.Popen(["git","commit","-m",options['message']])
        p.communicate()
        print p.returncode
        '''

        if not options['locked']:
            lock.delete()
        


