# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from .defs import DEFAULT_S_TIME, DEFAULT_E_TIME
from .favoritegroup import FavoriteGroup

User = get_user_model()


class UserSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)

    nickname = models.CharField('ニックネーム', max_length=64, default="")
    show_weekend = models.BooleanField('週末の表示', default=False)
    rows_description = models.IntegerField(
        '補足の入力行数', default=5,
        validators=[MinValueValidator(3), MaxValueValidator(15)])

    s_time = models.TimeField('開始時間', default=DEFAULT_S_TIME)
    e_time = models.TimeField('終了時間', default=DEFAULT_E_TIME)

    favorite_group_primary = \
        models.ForeignKey(FavoriteGroup,
                          on_delete=models.SET_NULL, null=True, blank=True)

    show_month_calendar = models.BooleanField('スケジュール(月)の表示', default=False)

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
            "s_time=%s,e_time=%s,fg_primary=%s,show_month=%s>"
        return s % (u, self.nickname,
                    str(self.show_weekend), self.rows_description,
                    str(self.s_time), str(self.e_time), f,
                    str(self.show_month_calendar))

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
                self.rows_description, self.s_time, self.e_time, f,
                self.show_month_calendar)


def get_usersetting_object(user):
    if user.is_authenticated:
        x = UserSetting.objects.filter(user=user)
        if x.exists():
            return x.first()
        return UserSetting.objects.create(user=user)
    return None
