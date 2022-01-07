# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist, _strtobool
from ...models import UserSetting, FavoriteGroup
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


class Command(MyBaseCommand):
    Model = UserSetting

    def do_csv_line(self, ln, commit=False):
        u, nickname, w, r, s, e, f_name = [x.strip() for x in ln]

        user = User.objects.get(email=u)
        show_weekend = _strtobool(w)
        rows_description = int(r)
        s_time = datetime.time.fromisoformat(s)
        e_time = datetime.time.fromisoformat(e)
        favorite_group_primary = None

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
            if x.s_time != s_time:
                x.s_time = s_time
                changed = True
            if x.e_time != e_time:
                x.e_time = e_time
                changed = True
            if x.favorite_group_primary != favorite_group_primary:
                x.favorite_group_primary = favorite_group_primary
                changed = True

            self.do_update(x, commit, changed)
        except ObjectDoesNotExist:
            x = self.Model(user=user,
                           nickname=nickname, show_weekend=show_weekend,
                           rows_description=rows_description,
                           s_time=s_time, e_time=e_time)
            if favorite_group_primary is not None:
                x.favorite_group_primary = favorite_group_primary

            self.do_create(x, commit)
