# -*- coding: utf-8 -*-
import uuid
from django.db import models


class Holiday(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField('日付', unique=True)
    name = models.CharField('名前', max_length=64)
    dayoff = models.BooleanField('休日', default=True)

    def __str__(self):
        return "%s,%s,%s" % (str(self.date), self.name, self.dayoff)

    def get_itemlist(self):
        return (self.date, self.name, self.dayoff)
