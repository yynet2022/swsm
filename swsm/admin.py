# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from .models import Holiday, Information

admin.site.register(Holiday)
admin.site.register(Information)
