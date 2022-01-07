# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist
from ...models import UserLog
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


class Command(MyBaseCommand):
    Model = UserLog

    def do_csv_line(self, ln, commit=False):
        u, d, message = [x.strip() for x in ln]

        user = User.objects.get(email=u)
        created_at = datetime.datetime.fromisoformat(d)

        try:
            x = self.Model.objects.get(user=user,
                                       created_at=created_at, message=message)
            self.do_update(x, commit, False)
        except ObjectDoesNotExist:
            x = self.Model(user=user, created_at=created_at, message=message)
            self.do_create(x, commit)
