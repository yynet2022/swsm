# -*- coding: utf-8 -*-
import datetime
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from ..apps import AppConfig
from ..forms import ScheduleForm, EmailForm
from ..models import Schedule
from .mixins import MonthCalendarMixin, WeekCalendarMixin, UtilsCalendarMixin

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class HomeView(MonthCalendarMixin,
               WeekCalendarMixin,
               UtilsCalendarMixin,
               generic.UpdateView):
    template_name = AppConfig.name + '/home.html'
    model = Schedule
    form_class = ScheduleForm

    def get_fav_infos(self):
        fav_infos = []
        try:
            u = self.request.user
            for g in u.favoritegroup_set.all().order_by('name'):
                x = {'name': g.name,
                     'members': [], }
                for u in g.favoritegroupuser_set.all():
                    x['members'].append({'user': u.member, })
                fav_infos.append(x)
        except Exception:
            pass
        return fav_infos

    def get_context_data(self, **kwargs):
        logger.info("> get_context_data: obj=%s", self.object)
        logger.info("> get_context_data: user=%s", self.request.user)

        if self.request.user.is_authenticated:
            ulist = User.objects.all().exclude(pk=self.request.user.pk)
        else:
            ulist = User.objects.all()

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
            'apptag': AppConfig.name + ':home',
            'informations': self.informations,
            'userlist': ulist.exclude(is_active=False),
            'favorite_infos': self. get_fav_infos(),
        })
        context['form'].fields['description'].widget.attrs['rows'] = \
            self.rows_description

        logger.info("< get_context_data")
        return context

    def form_invalid(self, form):
        logger.info("< form_invalid: %s", form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise PermissionDenied

        submit = form.data.get('sch_submit', None)
        date = form.cleaned_data.get('date', None)
        logger.info("> form_valid: submit: %s", submit)
        logger.info("  form.date: %s", date)
        logger.info("  form.has_changed: %s", form.has_changed())
        logger.info("  .object: %s", self.object)
        logger.info("  .user: %s", self.request.user)

        if date is None:
            return redirect(AppConfig.name + ':home')

        if submit == "del":
            self.object_filter(user=self.request.user, date=date).delete()

        if submit == "add":
            sch = form.save(commit=False)
            try:
                if self.request.user == sch.user and form.has_changed():
                    sch.save()
                    logger.info("  update: %s", sch)
            except User.DoesNotExist:
                # 'user' が存在しない、つまり DB にはまだ登録されてない
                # モデルなので、ここで user を設定して save する。
                sch.user = self.request.user
                sch.save()
                logger.info("  new: %s", sch)
            except Exception as e:
                logger.error("home.form_valid.error: %s", str(e))

        return redirect(AppConfig.name + ':home',
                        year=date.year, month=date.month, day=date.day)
