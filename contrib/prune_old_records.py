#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import datetime

# --- コマンドライン引数の設定 ---
parser = argparse.ArgumentParser(
    description='Deletes expired sessions and old records from the database.')
parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Simulate the process without deleting any records.')
args = parser.parse_args()
DRY_RUN = args.dry_run

# --- Djangoプロジェクトのパス設定 ---
if os.path.dirname(__file__).endswith('contrib'):
    sys.path.append(os.path.dirname(__file__)[:-7])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django  # noqa: E402
django.setup()
# --- ここまでセットアップ ---

from django.utils import timezone  # noqa: E402
from django.contrib.sessions.models import Session  # noqa: E402
from swsm.models import UserLog, Schedule  # noqa: E402

now = timezone.now()

n = Session.objects.all().count()
print('Session(all):', n)
n = Session.objects.filter(expire_date__lt=now).count()
print('  Session(expired):', n)

n = UserLog.objects.all().count()
print('UserLog(all):', n)
for i in range(now.year, now.year-10, -1):
    t = timezone.make_aware(datetime.datetime(i, 1, 1, 0, 0, 0))
    n = UserLog.objects.filter(created_at__lt=t).count()
    print(f'  UserLog(<{t.year}):', n)
    if n == 0:
        break

n = Schedule.objects.all().count()
print('Schedule(all):', n)
for i in range(now.year, now.year-10, -1):
    t = timezone.make_aware(datetime.datetime(i, 1, 1, 0, 0, 0))
    n = Schedule.objects.filter(created_at__lt=t).count()
    print(f'  Schedule(<{t.year}):', n)
    if n == 0:
        break
