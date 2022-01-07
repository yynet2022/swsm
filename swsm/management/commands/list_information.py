# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist
from ...models import Information
import datetime


class Command(MyBaseCommand):
    Model = Information

    def do_csv_line(self, ln, commit):
        message, d = [x.strip() for x in ln]
        created_at = datetime.datetime.fromisoformat(d)

        try:
            x = self.Model.objects.get(message=message)

            changed = False
            if x.created_at != created_at:
                x.created_at = created_at
                changed = True

            self.do_update(x, commit, changed)
        except ObjectDoesNotExist:
            x = self.Model(message=message, created_at=created_at)
            self.do_create(x, commit)
