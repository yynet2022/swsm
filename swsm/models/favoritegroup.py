# -*- coding: utf-8 -*-
import uuid
import base64
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class FavoriteGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    name = models.CharField('名前', max_length=64)

    created_at = models.DateTimeField('作成日', default=timezone.now)

    def get_eid(self):
        sid = str(self.id).replace('-', 'z')
        return base64.b64encode(sid.encode()).decode()

    def __str__(self):
        try:
            u = self.user.email
        except Exception:
            u = '-'
        return "<FavoriteG:%s,%s>" % (u, self.name)

    def get_itemlist(self):
        try:
            u = str(self.user.email)
        except Exception:
            u = ''
        return (u, self.name)

    class Meta:
        constraints = [  # １ユーザに、同じ名前はダメ。
            models.UniqueConstraint(
                fields=["user", "name"],
                name="swsm_user_name_unique"
            ),
        ]


class FavoriteGroupUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    favorite_group = \
        models.ForeignKey(FavoriteGroup, on_delete=models.CASCADE, default=0)
    member = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    created_at = models.DateTimeField('作成日', default=timezone.now)

    def get_eid(self):
        sid = str(self.id).replace('-', 'z')
        return base64.b64encode(sid.encode()).decode()

    def __str__(self):
        try:
            f = str(self.favorite_group)
        except Exception:
            f = '-'
        try:
            u = self.member.email
        except Exception:
            u = '-'
        return "<FGUser:%s,%s>" % (f, u)

    def get_itemlist(self):
        try:
            f = self.favorite_group.get_itemlist()
        except Exception:
            f = ('', '')
        try:
            u = str(self.member.email)
        except Exception:
            u = ''
        return f + (u, )

    class Meta:
        constraints = [  # １FavoriteGroup に、同じ名前はダメ。
            models.UniqueConstraint(
                fields=["favorite_group", "member"],
                name="swsm_favoritegroup_member_unique"
            ),
        ]
