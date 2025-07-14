#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse

# --- コマンドライン引数の設定 ---
parser = argparse.ArgumentParser(
    description='Clear sessions for inactive users.')
parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Simulate the process without actually deleting sessions.')
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
from django.contrib.auth import get_user_model  # noqa: E402
from django.contrib.sessions.models import Session  # noqa: E402

User = get_user_model()

if DRY_RUN:
    print("(DRY RUN MODE)")

# 1. is_active=False のユーザーIDを取得
# UUIDFieldの場合、DBからはUUIDオブジェクトが返るので、文字列に変換する
inactive_user_ids = [
    str(uid) for uid in
    User.objects.filter(is_active=False).values_list('id', flat=True)
]

if not inactive_user_ids:
    print("No inactive users found.")
    sys.exit()

# 2. 有効期限内の全セッションを取得
all_sessions = Session.objects.filter(expire_date__gte=timezone.now())

sessions_to_delete_keys = []
# 3. 各セッションをループし、非アクティブユーザーのものか判定
for session in all_sessions:
    session_data = session.get_decoded()
    # セッションデータ内のユーザーID（これも文字列）を取得
    user_id_in_session = session_data.get('_auth_user_id')

    # user_id_in_session が存在し、
    # それが非アクティブユーザーのIDリスト（文字列リスト）に含まれるか確認
    if user_id_in_session and user_id_in_session in inactive_user_ids:
        sessions_to_delete_keys.append(session.session_key)

# 4. 該当するセッションを一括で削除 (Dry Runの場合はスキップ)
if sessions_to_delete_keys:
    print(f"Found {len(sessions_to_delete_keys)} session(s) to delete.")
    if not DRY_RUN:
        deleted_count, _ = Session.objects.filter(
            session_key__in=sessions_to_delete_keys).delete()
        print(f"Successfully deleted {deleted_count} session(s).")
    else:
        print("--- DRY RUN: Skipping deletion. ---")
else:
    print("No active sessions found for inactive users.")
