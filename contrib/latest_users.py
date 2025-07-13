#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime

if os.path.dirname(__file__).endswith('contrib'):
    sys.path.append(os.path.dirname(__file__)[:-7])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django  # noqa: E402
django.setup()

from django.utils import timezone  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402

from swsm.models import UserLog, Schedule  # noqa: E402

User = get_user_model()

# VERBOSE = False

# 比較の基準となる、十分に古いawareな日付を用意
# スクリプト実行時のタイムゾーンを使う
base_ts = datetime.datetime(2000, 1, 1, tzinfo=timezone.get_current_timezone())

# 現時刻
now_ts = timezone.now()

for user in User.objects.filter(is_active=True):
    ts = base_ts

    # UserLog の最新レコードを取得（なければ None が返る）
    log = UserLog.objects.filter(user=user).order_by('-created_at').first()
    if log:
        ts = max(ts, log.created_at)

    # Schedule の最新レコードを取得（なければ None が返る）
    sch = Schedule.objects.filter(user=user).order_by('-updated_at').first()
    if sch:
        ts = max(ts, sch.updated_at)

    print(user.email, timezone.localtime(ts), now_ts - ts, sep='\t')
