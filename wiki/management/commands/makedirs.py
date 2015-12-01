import django.core.management
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os
import subprocess
import wiki.util

class Command(BaseCommand):
    help = 'help message'
	
    def add_arguments(self, parser):
	parser.add_argument('abspath')
        
    def handle(self, *args, **options):
	
        lock = wiki.util.acquire_lock()

        abspath = options['abspath']

        os.makedirs(abspath)
        
        filename = os.path.join(abspath, 'index.md')

        p = subprocess.Popen(["touch",filename])
       	p.communicate()
      	
	django.core.management.call_command('commit_all', 
			'folder create {}'.format(abspath, locked=True))

        lock.delete()
        

