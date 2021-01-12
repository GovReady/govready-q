import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from random import sample
from loadtesting.web import WebClient

class Command(BaseCommand):
    client = None
    bad_comps = []

    help = 'Starts one or many assessments for an org'

    def add_arguments(self, parser):
        parser.add_argument('--org', type=str, required=True, help="")
        parser.add_argument('--username', type=str, required=True, help="")
        parser.add_argument('--password', type=str, required=True, help="")
        parser.add_argument('--to-completion', action="store_true", help="")

    def handle(self, *args, **options):
        self.client = WebClient(options['username'], options['org'])

        if options['to_completion']:
            comps = self.client.get_components()
            repeatable_comp_count = len(self.client.selector.css('.question-title .glyphicon-plus'))
            print("{} repeatable components".format(repeatable_comp_count))
            while options['to_completion'] and len(comps) > repeatable_comp_count + len(self.bad_comps):
                print("{} components left ({} repeatable)".format(len(comps)-len(self.bad_comps), repeatable_comp_count))
                self._do_single()
                comps = self.client.get_components()
            print("{} repeatable components, {} non-completable components".format(repeatable_comp_count, len(self.bad_comps)))
        else:
            self._do_single()

    def _do_single(self):
        all = self.client.get_components()
        comp = sample(all, 1)[0]
        if len(all) > len(self.bad_comps):
            while comp in self.bad_comps:
                comp = sample(all, 1)[0]
        print(comp)
        self.client.load('/store?q=' + comp)
        url_before = self.client.current_url
        self.client.add_comp()
        url_after = self.client.current_url

        if url_before == url_after:
            self.bad_comps.append(comp)
            print("Got same URL, marking component {} as non-completable".format(comp))
