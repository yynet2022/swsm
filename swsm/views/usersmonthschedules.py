# -*- coding: utf-8 -*-
import datetime
from django.views import generic
from django.contrib.auth import get_user_model
from django.db.models import Q
from ..apps import AppConfig
from ..forms import EmailForm
from ..models import Schedule
from .mixins import MonthCalendarMixin, WeekCalendarMixin, UtilsCalendarMixin

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class CalendarTools(MonthCalendarMixin,
                    WeekCalendarMixin,
                    UtilsCalendarMixin):
    model = None

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def get_context_data(self, **kwargs):
        context = kwargs
        context.update(self.get_month_calendar(self.target_date))
        context.update({
            'today': datetime.date.today(),
            'date': self.target_date,
            })
        del context['month_week_names']
        del context['month_days']
        return context


class UsersMonthSchedulesView(generic.TemplateView):
    template_name = AppConfig.name + '/usersmonthschedules.html'
    model = Schedule

    def get_context_data(self, **kwargs):
        logger.info("> get_context_data: method=%s", self.request.method)
        logger.info("> get_context_data: GET=%s", self.request.GET)

        v10 = v20 = v30 = w10 = w20 = w30 = None
        if self.request.method.lower() == 'get':
            v10 = self.request.GET.get('v10')
            v20 = self.request.GET.get('v20')
            v30 = self.request.GET.get('v30')
            w10 = self.request.GET.get('w10')
            w20 = self.request.GET.get('w20')
            w30 = self.request.GET.get('w30')
        if v10 is None and v20 is None and v30 is None and \
           w10 is None and w20 is None and w30 is None:
            w10 = w20 = True
        logger.info("v10=%s, v20=%s, v30=%s", v10, v20, v30)
        logger.info("w10=%s, w20=%s, w30=%s", w10, w20, w30)

        qdict = {}
        for u in User.objects.all():
            if u.is_active:
                qdict[u.pk] = {'user': u, 'favorite': 0, }

        try:
            u = self.request.user
            i = 10
            for g in u.favoritegroup_set.all().order_by('name').reverse():
                for gu in g.favoritegroupuser_set.all():
                    if gu.member.is_active:
                        qdict[gu.member.pk]['favorite'] = -i
                i += 1
            qdict[u.pk] = {'user': u, 'favorite': -i, }
        except Exception:
            pass

        qlist = sorted(qdict.values(),
                       key=lambda x: (x['favorite'],
                                      x['user'].get_short_name()))

        qdict = {}
        for k, x in enumerate(qlist):
            qdict[x['user'].pk] = k

        ct = CalendarTools(self.request, *self.args, **self.kwargs)
        target_date = ct.target_date
        ts = target_date.replace(day=1)
        te = ct.get_next_month(target_date) - datetime.timedelta(days=1)
        dt = te - ts
        ndays = dt.days + 1

        q = Q()
        if v10:
            q |= Q(vacation=10)
        if v20:
            q |= Q(vacation=20)
        if v30:
            q |= Q(vacation=30)
        if w10:
            q |= ~Q(vacation=10) & Q(working=10)
        if w20:
            q |= ~Q(vacation=10) & Q(working=20)
        if w30:
            q |= ~Q(vacation=10) & Q(working=30)
        logger.info("q=%s", q)

        def _get_mday_schedules():
            for i in range(ndays):
                tt = target_date.replace(day=i+1)
                a = [''] * len(qlist)
                for x in Schedule.objects.filter(date=tt).filter(q):
                    try:
                        k = qdict[x.user.pk]
                    except Exception:
                        continue

                    s = ''
                    if x.vacation == 10:
                        s = '休'
                    elif x.vacation == 20:
                        s = 'A'
                    elif x.vacation == 30:
                        s = 'P'
                    if x.vacation != 10:
                        if x.working == 10:
                            s += '出'
                        elif x.working == 20:
                            s += '部'
                        elif x.working == 30:
                            s += '在'
                    a[k] = s
                yield {'date': tt, 'q': a}

        context = super().get_context_data(**kwargs)
        context.update(ct.get_context_data())
        context.update({
            'mday_schedules': _get_mday_schedules(),
            'userform': EmailForm(),
            'qlist': qlist,
            'apptag': AppConfig.name + ':usersmonthschedules',
            'cv': {'v10': '' if v10 is None else 'checked',
                   'v20': '' if v20 is None else 'checked',
                   'v30': '' if v30 is None else 'checked',
                   'w10': '' if w10 is None else 'checked',
                   'w20': '' if w20 is None else 'checked',
                   'w30': '' if w30 is None else 'checked'}
            })

        logger.info("< get_context_data: %s", context)
        return context
