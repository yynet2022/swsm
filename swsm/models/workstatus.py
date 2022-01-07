# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkStatus(models.Model):
    STATUS_CHOICES = (
        (0,  '勤務外'),
        (10, '勤務中'),
        (20, '中断中'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    status = models.IntegerField('勤務状態', default=0, choices=STATUS_CHOICES)
    update_at = models.DateTimeField('更新日時', default=timezone.now)

    def status_sf(self):
        if self.status == 10:
            return '○'
        elif self.status == 20:
            return '△'
        else:
            return '×'

    def __str__(self):
        try:
            s = "<Status:%s," % self.user.email
        except Exception:
            s = "<Status:-,"
        s += self.get_status_display() + ","
        s += str(timezone.localtime(self.update_at)) + ">"
        return s
