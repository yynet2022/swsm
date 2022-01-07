# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist, _strtobool
from ...models import User
import datetime


class Command(MyBaseCommand):
    Model = User

    def do_csv_line(self, ln, commit=False):
        email, a, token, isact, isstf, isadm = [x.strip() for x in ln]
        access_at = datetime.datetime.fromisoformat(a)
        is_active = _strtobool(isact)
        is_staff = _strtobool(isstf)
        is_admin = _strtobool(isadm)

        try:
            x = self.Model.objects.get(email=email)

            changed = False
            if x.access_at != access_at:
                x.access_at = access_at
                changed = True
            if x.token != token:
                x.token = token
                changed = True
            if x.is_active != is_active:
                x.is_active = is_active
                changed = True
            if x.is_staff != is_staff:
                x.is_staff = is_staff
                changed = True
            if x.is_admin != is_admin:
                x.is_admin = is_admin
                changed = True

            self.do_update(x, commit, changed)
        except ObjectDoesNotExist:
            x = self.Model(email=email, access_at=access_at,
                           token=token,
                           is_active=is_active, is_staff=is_staff,
                           is_admin=is_admin)
            self.do_create(x, commit)
