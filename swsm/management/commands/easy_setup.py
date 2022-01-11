# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
import sys
from pathlib import Path

__all__ = ['Command']


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--force', action='store_true', help='Force')

    def handle(self, *args, **kwargs):
        try:
            mode = 'w' if kwargs['force'] else 'wx'
            p = Path('.') / 'project' / 'local_settings.py'
            print("Making '", p, "'...", flush=True, sep='', end=' ')
            with p.open(mode) as fd:
                fd.write("# -*- coding: utf-8 -*-\n")
                fd.write("#\n")

                secret_key = get_random_secret_key()
                fd.write("SECRET_KEY = 'easy_setup#{0}'\n".format(secret_key))
                fd.write("\n")
                fd.write("ALLOWED_HOSTS = ['*']\n")
                fd.write("\n")
                fd.write("DEFAULT_FROM_EMAIL = 'webmaster@localhost'\n")
                fd.write("EMAIL_HOST = 'localhost'\n")
                fd.write("\n")
            print("done.")
        except Exception as e:
            print('error,', e, file=sys.stderr)
            sys.exit(1)
