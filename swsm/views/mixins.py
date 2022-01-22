# -*- coding: utf-8 -*-
import calendar
import datetime
from ..models import Holiday, Information, DEFAULT_S_TIME, DEFAULT_E_TIME

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)


class BaseCalendarMixin:
    # 週の始まりの曜日を指定する。
    # 0 は月曜から、1 は火曜から。6 なら日曜日から。
    __FIRST_WEEKDAY = 6

    # 月曜日から書くこと前提。['Mon', 'Tue'...
    __WEEK_NAMES = ['月', '火', '水', '木', '金', '土', '日']

    @property
    def calendar(self):
        try:
            return getattr(self, "__pv_calendar")
        except AttributeError:
            self.__pv_calendar = calendar.Calendar(self.__FIRST_WEEKDAY)
            return self.__pv_calendar

    @property
    def week_names(self):
        try:
            return getattr(self, "__pv_week_names")
        except AttributeError:
            self.__pv_week_names = tuple(self.__WEEK_NAMES[x]
                                         for x in self.calendar.iterweekdays())
            return self.__pv_week_names


class WeekCalendarMixin(BaseCalendarMixin):
    def get_week_days(self, date, show_weekend):
        iwdays = tuple(self.calendar.iterweekdays())
        w = iwdays.index(date.weekday())
        s = tuple(date+datetime.timedelta(days=-w+x) for x in range(7))
        if not show_weekend:
            s = tuple(d for i, d in zip(iwdays, s) if i < 5)
        return s

    def get_week_calendar(self, date, show_weekend):
        days = self.get_week_days(date, show_weekend)
        first = days[0]
        last = days[-1]

        w_names = self.week_names
        iwdays = self.calendar.iterweekdays()
        if not show_weekend:
            w_names = tuple(d for i, d in zip(iwdays, w_names) if i < 5)

        return {
            'week_names': w_names,
            'week_prev':  first - datetime.timedelta(days=7),
            'week_next':  first + datetime.timedelta(days=7),
            'week_days':  days,
            'week_first': first,
            'week_last':  last,
        }


class MonthCalendarMixin(BaseCalendarMixin):
    def get_prev_month(self, date):
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)
        else:
            return date.replace(month=date.month-1, day=1)

    def get_next_month(self, date):
        if date.month == 12:
            return date.replace(year=date.year+1, month=1, day=1)
        else:
            return date.replace(month=date.month+1, day=1)

    def get_month_days(self, date):
        return self.calendar.monthdatescalendar(date.year, date.month)

    def get_month_calendar(self, date):
        current_month = date.replace(day=1)
        return {
            'month_week_names': self.week_names,
            'month_curr': current_month,
            'month_prev': self.get_prev_month(current_month),
            'month_next': self.get_next_month(current_month),
            'month_days': self.get_month_days(current_month),
        }


class UtilsCalendarMixin:
    def __get_target_date(self):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if year and month and day:
            return datetime.date(year=int(year),
                                 month=int(month), day=int(day))
        elif month and year:
            return datetime.date(year=int(year), month=int(month), day=1)
        else:
            return datetime.date.today()

    @property
    def target_date(self):
        try:
            return getattr(self, "__pv_target_date")
        except AttributeError:
            self.__pv_target_date = self.__get_target_date()
            return self.__pv_target_date

    def object_filter(self, **kwargs):
        return self.model.objects.filter(**kwargs)

    def get_model(self):
        return self.model(ws_time=self.user_s_time,
                          we_time=self.user_e_time,
                          zs_time=self.user_s_time,
                          ze_time=self.user_e_time)

    def get_object(self):
        if self.request.user.is_authenticated:
            kwargs = {'user': self.request.user,
                      'date': self.target_date, }
            x = self.object_filter(**kwargs)
            if x.exists():
                return x.first()
            else:
                return self.get_model()
        return None

    def get_initial(self):
        v = super().get_initial()
        # v['user'] = self.request.user # これは意味無い。(formに渡さないから)
        v['date'] = self.target_date
        return v

    def get_week_schedules(self, days):
        schedules = {day: None for day in days}

        first = days[0]
        last = days[-1]
        lookup = {'date__range': (first, last), }
        if self.request.user.is_authenticated:
            lookup['user'] = self.request.user
            logger.info("> get_week_schedules: lookup=%s", lookup)
            for sch in self.object_filter(**lookup):
                schedules[sch.date] = sch
        return schedules

    def get_week_holidays(self, days):
        holidays = {day: "" for day in days}

        first = days[0]
        last = days[-1]
        lookup = {'date__range': (first, last), }
        logger.info("> get_week_holidays: lookup=%s", lookup)
        for hol in Holiday.objects.filter(**lookup):
            holidays[hol.date] = hol.name
        logger.debug("< get_week_holidays: %s", holidays)
        return holidays

    @property
    def show_weekend(self):
        try:
            return self.request.user.usersetting.show_weekend
        except Exception:
            return True

    @property
    def rows_description(self):
        try:
            return self.request.user.usersetting.rows_description
        except Exception:
            return 5

    @property
    def user_s_time(self):
        try:
            return self.request.user.usersetting.s_time
        except Exception:
            return DEFAULT_S_TIME

    @property
    def user_e_time(self):
        try:
            return self.request.user.usersetting.e_time
        except Exception:
            return DEFAULT_E_TIME

    @property
    def informations(self):
        return Information.objects.order_by('created_at').reverse()
