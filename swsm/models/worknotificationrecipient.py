# -*- coding: utf-8 -*-
import uuid
import base64
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkNotificationRecipient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    recipient = models.EmailField(
        verbose_name='メールアドレス',
        max_length=255,
    )
    is_active = models.BooleanField(default=True)

    def get_eid(self):
        sid = str(self.id).replace('-', 'z')
        return base64.b64encode(sid.encode()).decode()

    def __str__(self):
        try:
            u = self.user.email
        except Exception:
            u = '-'
        return "<WorkNotificationRecipient:%s,%s>" % (u, self.recipient)

    def get_itemlist(self):
        try:
            u = str(self.user.email)
        except Exception:
            u = ''
        return (u, self.recipient, self.is_active)

    class Meta:
        constraints = [  # １ユーザに、同じメアドはダメ。
            models.UniqueConstraint(
                fields=["user", "recipient"],
                name="swsm_user_work_notification_recipient_unique"
            ),
        ]
