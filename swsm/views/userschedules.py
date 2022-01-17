# -*- coding: utf-8 -*-
import datetime
from django.views import generic
from django.contrib.auth import get_user_model
from ..apps import AppConfig
from ..forms import EmailForm
from ..models import Schedule
from .mixins import MonthCalendarMixin, WeekCalendarMixin, UtilsCalendarMixin

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class UserSchedulesView(MonthCalendarMixin,
                        WeekCalendarMixin,
                        UtilsCalendarMixin,
                        generic.DetailView):
    template_name = AppConfig.name + '/userschedules.html'
    model = Schedule

    def get_context_data(self, **kwargs):
        logger.info("> get_context_data: method=%s", self.request.method)
        logger.info("> get_context_data: user=%s", self.request.user)

        qdict = {}
        for u in User.objects.all():
            qdict[u.pk] = {'user': u, 'favorite': 0, }
        for s in self.object_filter(date=self.target_date):
            qdict[s.user.pk]['schedule'] = s

        try:
            for g in self.request.user.favoritegroup_set.all():
                for u in g.favoritegroupuser_set.all():
                    qdict[u.member.pk]['favorite'] = 10
        except Exception:
            pass

        if self.request.user.is_authenticated:
            del qdict[self.request.user.pk]

        s = []
        for x in qdict.keys():
            if not qdict[x]['user'].is_active:
                s.append(x)
        for x in s:
            del qdict[x]

        key = None
        if self.request.method == "GET":
            key = self.request.GET.get('key')
            logger.info("  key=%s", key)

        if key is None:
            qlist = qdict.values()
        else:
            for x in qdict.values():
                if key == "n" or key == "nr":
                    u = x['user']
                    try:
                        x['key'] = u.usersetting.nickname
                    except Exception:
                        x['key'] = u.get_short_name()
                elif key == "v" or key == "vr":
                    try:
                        x['key'] = x['schedule'].vacation
                    except Exception:
                        x['key'] = 100
                elif key == "w" or key == "wr":
                    try:
                        x['key'] = x['schedule'].working
                    except Exception:
                        x['key'] = 100
                elif key == "f" or key == "fr":
                    try:
                        x['key'] = x['favorite']
                    except Exception:
                        x['key'] = 0
                else:
                    x['key'] = 0
            qlist = sorted(qdict.values(), key=lambda x: x['key'])
            if key == 'nr' or key == 'vr' or key == 'wr' or key == 'fr':
                qlist.reverse()

        def _get_month_schedules():
            for x in context['month_days']:
                s = self.get_week_schedules(x)
                h = self.get_week_holidays(x)
                yield {y: (s[y], h[y]) for y in x}

        context = super().get_context_data(**kwargs)
        context.update(
            self.get_week_calendar(self.target_date, self.show_weekend))
        context.update(self.get_month_calendar(self.target_date))
        context.update({
            'today': datetime.date.today(),
            'date': self.target_date,
            'week_schedules': self.get_week_schedules(context['week_days']),
            'week_holidays': self.get_week_holidays(context['week_days']),
            'month_schedules': _get_month_schedules(),
            'userform': EmailForm(),
            'qlist': qlist,
            'apptag': AppConfig.name + ':userschedules',
            })

        logger.info("< get_context_data")
        return context
