# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist, _strtobool
from ...models import Holiday
import datetime


class Command(MyBaseCommand):
    Model = Holiday

    def do_csv_line(self, ln, commit):
        d, name, b = [x.strip() for x in ln]

        date = datetime.date.fromisoformat(d)
        dayoff = _strtobool(b)

        try:
            x = self.Model.objects.get(date=date)

            changed = False
            if x.name != name:
                x.name = name
                changed = True
            if x.dayoff != dayoff:
                x.dayoff = dayoff
                changed = True

            self.do_update(x, commit, changed)
        except ObjectDoesNotExist:
            x = self.Model(date=date, name=name, dayoff=dayoff)
            self.do_create(x, commit)
