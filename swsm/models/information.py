# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils import timezone


class Information(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField('連絡事項', blank=True)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return "%s,%s" % (self.message, str(self.created_at))

    def get_itemlist(self):
        return (self.message, self.created_at)
