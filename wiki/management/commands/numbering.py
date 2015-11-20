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
		for poll_id in options['poll_id']:
			try:
				poll = Poll.objects.get(pk=poll_id)
			except Poll.DoesNotExist:
				raise CommandError('Poll "%s" does not exist' % poll_id)

			poll.opened = False
			poll.save()

			self.stdout.write('Successfully closed poll "%s"' % poll_id)
		'''
		
		
		
		#for root, dirs, files in os.walk(settings.WIKI_SRC_ROOT):
		#	print root
		
		wiki.util.list_data_src()