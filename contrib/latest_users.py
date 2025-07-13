#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime

if os.path.dirname(__file__).endswith('contrib'):
    sys.path.append(os.path.dirname(__file__)[:-7])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

from swsm.models import UserLog, Schedule

VERBOSE=False
for user in User.objects.filter(is_active=True):
    now = datetime.datetime.now(datetime.timezone.utc)
    n = datetime.datetime(year=2000, month=1, day=1, tzinfo=now.tzinfo)

    try:
        log = UserLog.objects.filter(user=user).latest('created_at')
        if n < log.created_at:
            n = log.created_at
    except UserLog.DoesNotExist as e:
        pass

    try:
        sch = Schedule.objects.filter(user=user).latest('created_at')
        if n < sch.created_at:
            n = sch.created_at
    except Schedule.DoesNotExist as e:
        pass

    print(user.email, n, now - n, sep='\t')
