# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from .defs import (
    DEFAULT_S_TIME, DEFAULT_E_TIME,
    DEFAULT_LUNCH_S_TIME, DEFAULT_LUNCH_E_TIME,
    DEFAULT_WORKING_AT)
from .favoritegroup import FavoriteGroup

User = get_user_model()


class UserSetting(models.Model):
    WORKING_AT_CHOICES = (
        (10, '出社 (在宅無)'),
        (30, '終日在宅 (出社無)'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)

    nickname = models.CharField('ニックネーム', max_length=64, default="")
    show_weekend = models.BooleanField('週末の表示', default=False)
    rows_description = models.IntegerField(
        '補足の入力行数', default=5,
        validators=[MinValueValidator(3), MaxValueValidator(15)])

    working_at = models.IntegerField('出社/在宅', default=DEFAULT_WORKING_AT,
                                     choices=WORKING_AT_CHOICES)

    s_time = models.TimeField('開始時間', default=DEFAULT_S_TIME)
    e_time = models.TimeField('終了時間', default=DEFAULT_E_TIME)

    ls_time = models.TimeField('昼休み開始時間', default=DEFAULT_LUNCH_S_TIME)
    le_time = models.TimeField('昼休み終了時間', default=DEFAULT_LUNCH_E_TIME)

    favorite_group_primary = \
        models.ForeignKey(FavoriteGroup,
                          on_delete=models.SET_NULL, null=True, blank=True)

    show_month_calendar = models.BooleanField('スケジュール(月)の表示', default=False)

    show_favorite_users_only = models.BooleanField('お気に入りだけ表示', default=False)

    wnr_subject = models.CharField('勤務状態メールのサブジェクト',
                                   max_length=64, default='[勤務#s#] #n#')

    def __str__(self):
        try:
            u = str(self.user.email)
        except Exception:
            u = "-"
        try:
            f = str(self.favorite_group_primary.name)
        except Exception:
            f = "-"
        s = "UserSetting<user=%s/%s," + \
            "show_weekend=%s,rows_description=%d," + \
            "working_at=%d," + \
            "s_time=%s,e_time=%s," + \
            "ls_time=%s,le_time=%s," + \
            "fg_primary=%s,show_month=%s,show_fav_users=%s>"
        return s % (u, self.nickname,
                    str(self.show_weekend), self.rows_description,
                    self.working_at,
                    str(self.s_time), str(self.e_time),
                    str(self.ls_time), str(self.le_time),
                    f,
                    str(self.show_month_calendar),
                    str(self.show_favorite_users_only))

    def get_itemlist(self):
        try:
            u = str(self.user.email)
        except Exception:
            u = ''
        try:
            f = str(self.favorite_group_primary.name)
        except Exception:
            f = ''
        return (u, self.nickname, self.show_weekend,
                self.rows_description,
                self.working_at,
                self.s_time, self.e_time,
                self.ls_time, self.le_time,
                f,
                self.show_month_calendar,
                self.show_favorite_users_only)


def get_usersetting_object(user):
    if user.is_authenticated:
        x = UserSetting.objects.filter(user=user)
        if x.exists():
            return x.first()
        return UserSetting.objects.create(user=user)
    return None
