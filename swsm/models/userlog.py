# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    created_at = models.DateTimeField('作成時刻', default=timezone.now)
    message = models.CharField('メッセージ', max_length=128)

    def __str__(self):
        try:
            u = self.user.email
        except Exception:
            u = '-'
        return "Log<%s,%s,%s>" % (u, str(self.created_at), self.message)

    def get_itemlist(self):
        try:
            u = str(self.user.email)
        except Exception:
            u = ''
        return (u, self.created_at, self.message)
