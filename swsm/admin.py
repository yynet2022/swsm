# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from .models import Holiday, Information, UserSetting

admin.site.register(Holiday)
admin.site.register(Information)
admin.site.register(UserSetting)
