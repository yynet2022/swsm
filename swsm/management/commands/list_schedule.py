# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist
from ...models import Schedule
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


class Command(MyBaseCommand):
    Model = Schedule

    def do_csv_line(self, ln, commit):
        u, d, v, w, ws, we, zs, ze, description = [x.strip() for x in ln]

        user = User.objects.get(email=u)
        date = datetime.date.fromisoformat(d)
        vacation = int(v)
        working = int(w)
        ws_time = datetime.time.fromisoformat(ws)
        we_time = datetime.time.fromisoformat(we)
        zs_time = datetime.time.fromisoformat(zs)
        ze_time = datetime.time.fromisoformat(ze)

        try:
            x = self.Model.objects.get(user=user, date=date)

            changed = False
            if x.vacation != vacation:
                x.vacation = vacation
                changed = True
            if x.working != working:
                x.working = working
                changed = True
            if x.ws_time != ws_time:
                x.ws_time = ws_time
                changed = True
            if x.we_time != we_time:
                x.we_time = we_time
                changed = True
            if x.zs_time != zs_time:
                x.zs_time = zs_time
                changed = True
            if x.ze_time != ze_time:
                x.ze_time = ze_time
                changed = True
            if x.description != description:
                x.description = description
                changed = True

            self.do_update(x, commit, changed)
        except ObjectDoesNotExist:
            x = self.Model(user=user, date=date,
                           vacation=vacation, working=working,
                           ws_time=ws_time, we_time=we_time,
                           zs_time=zs_time, ze_time=ze_time,
                           description=description)
            self.do_create(x, commit)
