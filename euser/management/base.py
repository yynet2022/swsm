# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
import sys
import csv
from distutils.util import strtobool

__all__ = ['MyBaseCommand', 'ObjectDoesNotExist', '_strtobool']


def _strtobool(v):
    try:
        return bool(strtobool(v))
    except Exception:
        return False


class MyBaseCommand(BaseCommand):
    Model = None

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--file', type=str, help='CSV file of Data')
        parser.add_argument(
            '-c', '--commit', action='store_true', help='commit')
        parser.add_argument(
            '-D', '--delete-all', action='store_true',
            help='Delete all entry.')

    def do_update(self, x, commit, changed):
        if commit and changed:
            x.save()
            if self.__kwargs['verbosity'] > 0:
                print("Update:", x, file=sys.stderr)
        elif changed:
            if self.__kwargs['verbosity'] > 0:
                print("Not update:", x, file=sys.stderr)
        else:
            if self.__kwargs['verbosity'] > 0:
                print("not changed:", x, file=sys.stderr)

    def do_create(self, x, commit):
        if commit:
            x.save()
            if self.__kwargs['verbosity'] > 0:
                print("Create:", x, file=sys.stderr)
        else:
            if self.__kwargs['verbosity'] > 0:
                print("Not create:", x, file=sys.stderr)

    def do_csv_line(self, ln, commit):
        pass

    def readfromcsv(self, filename, commit=False):
        with open(filename, newline='') as fd:
            for ln in csv.reader(fd):
                try:
                    self.do_csv_line(ln, commit)
                except Exception as e:
                    print(e, file=sys.stderr)

    def handle(self, *args, **kwargs):
        # self.stdout.write("args=%s" % str(args))
        # self.stdout.write("kwargs=%s" % kwargs)

        self.__args = args
        self.__kwargs = kwargs
        try:
            if kwargs['delete_all']:
                for x in self.Model.objects.all():
                    if self.__kwargs['verbosity'] > 0:
                        print("Delete:", x, file=sys.stderr)
                    x.delete()

            filename = kwargs['file']
            if filename:
                self.readfromcsv(filename, kwargs['commit'])

            writer = csv.writer(sys.stdout)
            for x in self.Model.objects.all():
                writer.writerow(x.get_itemlist())
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(1)
