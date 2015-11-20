from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os
import importlib

import wiki.util

class Command(BaseCommand):
	help = 'help message'
	
	def add_arguments(self, parser):
		parser.add_argument('module_name')
		parser.add_argument('destination_folder')
		pass

	def handle(self, *args, **options):
		'''
		for poll_id in options['poll_id']:
			try:
				poll = Poll.objects.get(pk=poll_id)
			except Poll.DoesNotExist:
				raise CommandError('Poll "%s" does not exist' % poll_id)

			poll.opened = False
			poll.save()

			self.stdout.write('Successfully closed poll "%s"' % poll_id)
		'''
		
		module_name = options['module_name']
		destination_folder = options['destination_folder']
		
		destination_folder = os.path.join(settings.WIKI_BLD_ROOT, destination_folder)
		
		print 'module', repr(module_name)
		print 'dest  ', repr(destination_folder)
		
		mod = importlib.import_module(module_name)
		
		mod.gen(destination_folder)
		
		
		