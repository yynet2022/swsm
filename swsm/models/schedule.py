# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from .defs import DEFAULT_S_TIME, DEFAULT_E_TIME, DEFAULT_WORKING_AT

User = get_user_model()


class Schedule(models.Model):
    VACATION_CHOICES = (
        (0, ''),
        (10, '終日休'),
        (20, 'AM休'),
        (30, 'PM休'),
    )
    WORKING_CHOICES = (
        (10, '出社 (在宅無)'),
        (20, '部分在宅+部分出社'),
        (30, '終日在宅 (出社無)'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    """スケジュール"""
    date = models.DateField('日付')
    vacation = models.IntegerField('休暇', default=0, choices=VACATION_CHOICES)
    working = models.IntegerField('出社/在宅', default=DEFAULT_WORKING_AT,
                                  choices=WORKING_CHOICES)
    ws_time = models.TimeField('出社予定時間', default=DEFAULT_S_TIME)
    we_time = models.TimeField('退社予定時間', default=DEFAULT_E_TIME)
    zs_time = models.TimeField('在宅開始時間', default=DEFAULT_S_TIME)
    ze_time = models.TimeField('在宅終了時間', default=DEFAULT_E_TIME)
    description = models.TextField('補足', blank=True)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def vacation_f(self):
        return self.get_vacation_display()

    def working_f(self):
        if self.vacation == 10:
            return ''
        return self.get_working_display()

    def ws_time_f(self):
        if self.vacation == 10 or self.working == 30:
            return ''
        return self.ws_time

    def we_time_f(self):
        if self.vacation == 10 or self.working == 30:
            return ''
        return self.we_time

    def zs_time_f(self):
        if self.vacation == 10 or self.working == 10:
            return ''
        return self.zs_time

    def ze_time_f(self):
        if self.vacation == 10 or self.working == 10:
            return ''
        return self.ze_time

    def __str__(self):
        try:
            s = "<Sch:%s,%s," % (self.user.email, self.date)
        except Exception:
            s = "<Sch:-,%s," % (self.date)
        s += \
            self.vacation_f() + "," + \
            self.working_f() + "," + \
            str(self.ws_time_f()) + "," + \
            str(self.we_time_f()) + "," + \
            str(self.zs_time_f()) + "," + \
            str(self.ze_time_f()) + ">"
        return s

    def get_itemlist(self):
        try:
            u = str(self.user.email)
        except Exception:
            u = ''
        return (u, self.date, self.vacation, self.working,
                self.ws_time, self.we_time, self.zs_time, self.ze_time,
                self.description)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"],
                name="swsm_user_date_unique"
            ),
        ]
