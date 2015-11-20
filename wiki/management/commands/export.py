from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os

import wiki.util



class Command(BaseCommand):
	help = 'help message'
	
	def add_arguments(self, parser):
		#parser.add_argument('poll_id', nargs='+', type=int)
		pass
        
	def handle(self, *args, **options):
		'''
		create file tree

		recursivly descend tree and add all page html to a single string
		'''
		
		g = wiki.util.FileListGenerator()
			
		file_list = g()
		
		for f in file_list:
				print f


