# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist, _strtobool
from ...models import UserSetting, FavoriteGroup
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


class Command(MyBaseCommand):
    Model = UserSetting

    def do_csv_line(self, ln, commit=False):
        u, nickname, w, r, wat, s, e, ls, le, f_name, m = \
            [x.strip() for x in ln]

        user = User.objects.get(email=u)
        show_weekend = _strtobool(w)
        rows_description = int(r)
        working_at = int(wat)
        s_time = datetime.time.fromisoformat(s)
        e_time = datetime.time.fromisoformat(e)
        ls_time = datetime.time.fromisoformat(ls)
        le_time = datetime.time.fromisoformat(le)
        favorite_group_primary = None
        show_month_calendar = _strtobool(m)
        show_favorite_users_only = _strtobool(m)

        if f_name:
            try:
                favorite_group_primary = \
                    FavoriteGroup.objects.get(user=user, name=f_name)
            except ObjectDoesNotExist:
                favorite_group_primary = \
                    FavoriteGroup(user=user, name=f_name)
                self.do_create(favorite_group_primary, commit)

        try:
            x = self.Model.objects.get(user=user)

            changed = False
            if x.nickname != nickname:
                x.nickname = nickname
                changed = True
            if x.show_weekend != show_weekend:
                x.show_weekend = show_weekend
                changed = True
            if x.rows_description != rows_description:
                x.rows_description = rows_description
                changed = True
            if x.working_at != working_at:
                x.working_at = working_at
                changed = True
            if x.s_time != s_time:
                x.s_time = s_time
                changed = True
            if x.e_time != e_time:
                x.e_time = e_time
                changed = True
            if x.ls_time != ls_time:
                x.ls_time = ls_time
                changed = True
            if x.le_time != le_time:
                x.le_time = le_time
                changed = True
            if x.favorite_group_primary != favorite_group_primary:
                x.favorite_group_primary = favorite_group_primary
                changed = True
            if x.show_month_calendar != show_month_calendar:
                x.show_month_calendar = show_month_calendar
                changed = True
            if x.show_favorite_users_only != show_favorite_users_only:
                x.show_favorite_users_only = show_favorite_users_only
                changed = True

            self.do_update(x, commit, changed)
        except ObjectDoesNotExist:
            x = self.Model(user=user,
                           nickname=nickname, show_weekend=show_weekend,
                           rows_description=rows_description,
                           working_at=working_at,
                           s_time=s_time, e_time=e_time,
                           ls_time=ls_time, le_time=le_time,
                           show_month_calendar=show_month_calendar,
                           show_favorite_users_only=show_favorite_users_only)
            if favorite_group_primary is not None:
                x.favorite_group_primary = favorite_group_primary

            self.do_create(x, commit)
