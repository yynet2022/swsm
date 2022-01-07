# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist
from ...models import FavoriteGroup, FavoriteGroupUser
from django.contrib.auth import get_user_model
import sys

User = get_user_model()


class Command(MyBaseCommand):
    Model = FavoriteGroupUser

    def do_csv_line(self, ln, commit):
        u, name, m = [x.strip() for x in ln]

        user = User.objects.get(email=u)
        member = User.objects.get(email=m)
        try:
            favorite_group = FavoriteGroup.objects.get(user=user, name=name)
        except ObjectDoesNotExist as e:
            print("Warning:", e, "continue", file=sys.stderr)
            favorite_group = FavoriteGroup(user=user, name=name)
            self.do_create(favorite_group, commit)

        try:
            x = self.Model.objects.get(favorite_group=favorite_group,
                                       member=member)
            self.do_update(x, commit, False)
        except ObjectDoesNotExist:
            x = self.Model(favorite_group=favorite_group,
                           member=member)
            self.do_create(x, commit)
