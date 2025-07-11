# -*- coding: utf-8 -*-
import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from swsm.models import (
    Schedule, Holiday, Information, UserSetting, WorkStatus,
    FavoriteGroup, FavoriteGroupUser, UserLog, WorkNotificationRecipient
)

User = get_user_model()


class ScheduleModelTests(TestCase):

    def setUp(self):
        """
        テストに必要なユーザーを作成
        """
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )

    def test_create_schedule(self):
        """
        Schedule オブジェクトが正しく作成されるか確認。
        """
        today = datetime.date.today()
        schedule = Schedule.objects.create(
            user=self.user,
            date=today,
            description="Test schedule"
        )
        self.assertEqual(schedule.user, self.user)
        self.assertEqual(schedule.date, today)
        self.assertEqual(schedule.description, "Test schedule")

    def test_default_values(self):
        """
        デフォルト値が正しく設定されているか確認。
        """
        today = datetime.date.today()
        schedule = Schedule.objects.create(user=self.user, date=today)
        self.assertEqual(schedule.vacation, 0)  # 0: ''
        self.assertEqual(schedule.working, 10)  # 10: '出社 (在宅無)'

    def test_user_date_unique_constraint(self):
        """
        同じユーザー、同じ日付でスケジュールを作成しようとすると
        IntegrityError が発生するか確認。
        """
        today = datetime.date.today()
        Schedule.objects.create(user=self.user, date=today)
        with self.assertRaises(IntegrityError):
            Schedule.objects.create(user=self.user, date=today)


class HolidayModelTests(TestCase):

    def test_create_holiday(self):
        """
        Holiday オブジェクトが正しく作成されるか確認。
        """
        today = datetime.date.today()
        holiday = Holiday.objects.create(
            date=today,
            name="Test Holiday"
        )
        self.assertEqual(holiday.date, today)
        self.assertEqual(holiday.name, "Test Holiday")
        self.assertTrue(holiday.dayoff)

    def test_date_unique_constraint(self):
        """
        同じ日付で休日を作成しようとすると IntegrityError が発生するか確認。
        """
        today = datetime.date.today()
        Holiday.objects.create(date=today, name="Test Holiday")
        with self.assertRaises(IntegrityError):
            Holiday.objects.create(date=today, name="Another Holiday")


class InformationModelTests(TestCase):

    def test_create_information(self):
        """
        Information オブジェクトが正しく作成されるか確認。
        """
        info = Information.objects.create(message="Test Information")
        self.assertEqual(info.message, "Test Information")


class UserSettingModelTests(TestCase):

    def setUp(self):
        """
        テストに必要なユーザーを作成
        """
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )

    def test_create_usersetting(self):
        """
        UserSetting オブジェクトが正しく作成されるか確認。
        """
        setting = UserSetting.objects.create(
            user=self.user, nickname="test_user")
        self.assertEqual(setting.user, self.user)
        self.assertEqual(setting.nickname, "test_user")

    def test_default_values(self):
        """
        デフォルト値が正しく設定されているか確認。
        """
        setting = UserSetting.objects.create(user=self.user)
        self.assertEqual(setting.nickname, "")
        self.assertFalse(setting.show_weekend)
        self.assertEqual(setting.rows_description, 5)
        self.assertEqual(setting.working_at, 10)

    def test_user_onetoone_constraint(self):
        """
        同じユーザーに複数の UserSetting を作成しようとすると
        IntegrityError が発生するか確認。
        """
        UserSetting.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            UserSetting.objects.create(user=self.user)


class WorkStatusModelTests(TestCase):

    def setUp(self):
        """
        テストに必要なユーザーを作成
        """
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )

    def test_create_workstatus(self):
        """
        WorkStatus オブジェクトが正しく作成されるか確認。
        """
        status = WorkStatus.objects.create(user=self.user, status=10)
        self.assertEqual(status.user, self.user)
        self.assertEqual(status.status, 10)

    def test_default_values(self):
        """
        デフォルト値が正しく設定されているか確認。
        """
        status = WorkStatus.objects.create(user=self.user)
        self.assertEqual(status.status, 0)  # 0: '勤務外'

    def test_user_onetoone_constraint(self):
        """
        同じユーザーに複数の WorkStatus を作成しようとすると
        IntegrityError が発生するか確認。
        """
        WorkStatus.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            WorkStatus.objects.create(user=self.user)


class FavoriteGroupModelTests(TestCase):

    def setUp(self):
        """
        テストに必要なユーザーを作成
        """
        self.user1 = User.objects.create_user(
            email="test1@example.com",
            password="password123"
        )
        self.user2 = User.objects.create_user(
            email="test2@example.com",
            password="password123"
        )

    def test_create_favorite_group(self):
        """
        FavoriteGroup オブジェクトが正しく作成されるか確認。
        """
        group = FavoriteGroup.objects.create(
            user=self.user1, name="Test Group")
        self.assertEqual(group.user, self.user1)
        self.assertEqual(group.name, "Test Group")

    def test_user_name_unique_constraint(self):
        """
        同じユーザーが同じ名前のグループを作成しようとすると
        IntegrityError が発生するか確認。
        """
        FavoriteGroup.objects.create(
            user=self.user1, name="Test Group")
        with self.assertRaises(IntegrityError):
            FavoriteGroup.objects.create(
                user=self.user1, name="Test Group")

    def test_create_favorite_group_user(self):
        """
        FavoriteGroupUser オブジェクトが正しく作成されるか確認。
        """
        group = FavoriteGroup.objects.create(
            user=self.user1, name="Test Group")
        group_user = FavoriteGroupUser.objects.create(
            favorite_group=group,
            member=self.user2)
        self.assertEqual(group_user.favorite_group, group)
        self.assertEqual(group_user.member, self.user2)

    def test_favorite_group_member_unique_constraint(self):
        """
        同じグループに同じメンバーを登録しようとすると
        IntegrityError が発生するか確認。
        """
        group = FavoriteGroup.objects.create(
            user=self.user1, name="Test Group")
        FavoriteGroupUser.objects.create(
            favorite_group=group,
            member=self.user2
        )
        with self.assertRaises(IntegrityError):
            FavoriteGroupUser.objects.create(
                favorite_group=group,
                member=self.user2
            )


class UserLogModelTests(TestCase):

    def setUp(self):
        """
        テストに必要なユーザーを作成
        """
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )

    def test_create_userlog(self):
        """
        UserLog オブジェクトが正しく作成されるか確認。
        """
        log = UserLog.objects.create(
            user=self.user, message="Test Log Message")
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.message, "Test Log Message")


class WorkNotificationRecipientModelTests(TestCase):

    def setUp(self):
        """
        テストに必要なユーザーを作成
        """
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )

    def test_create_work_notification_recipient(self):
        """
        WorkNotificationRecipient オブジェクトが正しく作成されるか確認。
        """
        recipient = WorkNotificationRecipient.objects.create(
            user=self.user,
            recipient="recipient@example.com"
        )
        self.assertEqual(recipient.user, self.user)
        self.assertEqual(recipient.recipient, "recipient@example.com")
        self.assertTrue(recipient.is_active)

    def test_user_recipient_unique_constraint(self):
        """
        同じユーザーが同じメールアドレスの通知先を登録しようとすると
        IntegrityError が発生するか確認。
        """
        WorkNotificationRecipient.objects.create(
            user=self.user,
            recipient="recipient@example.com"
        )
        with self.assertRaises(IntegrityError):
            WorkNotificationRecipient.objects.create(
                user=self.user,
                recipient="recipient@example.com"
            )
