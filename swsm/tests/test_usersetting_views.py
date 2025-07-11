# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from swsm.models import (
    UserSetting, FavoriteGroup, WorkNotificationRecipient
)

User = get_user_model()


class UserSettingViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )
        self.usersetting = UserSetting.objects.create(user=self.user)

    def test_usersetting_view_url_resolves(self):
        """
        UserSettingView のURLが正しく解決されるかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        response = self.client.get(reverse('swsm:usersetting'))
        self.assertEqual(response.status_code, 200)

    def test_usersetting_view_uses_correct_template(self):
        """
        UserSettingView が正しいテンプレートを使用しているかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        response = self.client.get(reverse('swsm:usersetting'))
        self.assertTemplateUsed(response, 'swsm/usersetting.html')

    def test_usersetting_view_permission_denied_for_unauthenticated_user(self):
        """
        未認証ユーザーが UserSettingView にアクセスした場合に
        PermissionDenied が発生するかテスト。
        """
        response = self.client.get(reverse('swsm:usersetting'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_usersetting_update(self):
        """
        ユーザー設定が正しく更新されるかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        response = self.client.post(reverse('swsm:usersetting'), {
            'nickname': 'Updated Nickname',
            'rows_description': 10,
            'us_submit': 'ok'
        })
        # Redirects after successful POST
        self.assertEqual(response.status_code, 302)
        self.usersetting.refresh_from_db()
        self.assertEqual(self.usersetting.nickname, 'Updated Nickname')
        self.assertEqual(self.usersetting.rows_description, 10)


class FavoriteGroupViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )
        self.usersetting = UserSetting.objects.create(user=self.user)

    def test_favorite_group_view_url_resolves(self):
        """
        お気に入りグループ設定のURLが正しく解決されるかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_favoritegroup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_favorite_group_view_uses_correct_template(self):
        """
        お気に入りグループ設定が正しいテンプレートを使用しているかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_favoritegroup')
        response = self.client.get(url)
        self.assertTemplateUsed(
            response, 'swsm/usersetting_favoritegroup.html')

    def test_favorite_group_view_permission_denied_for_unauthenticated_user(
            self):
        """
        未認証ユーザーがお気に入りグループ設定にアクセスした場合に
        PermissionDenied が発生するかテスト。
        """
        url = reverse('swsm:usersetting_favoritegroup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_favorite_group_add(self):
        """
        お気に入りグループが正しく追加されるかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_favoritegroup')
        response = self.client.post(url, {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-name': 'New Group',
            'form-0-user': self.user.pk,
        })
        self.assertEqual(response.status_code, 302)
        exists = FavoriteGroup.objects.filter(
            user=self.user, name='New Group').exists()
        self.assertTrue(exists)

    def test_favorite_group_add_duplicate_name(self):
        """
        同じ名前のお気に入りグループを追加しようとした場合に
        エラーが発生するかテスト。
        """
        FavoriteGroup.objects.create(user=self.user, name='Existing Group')
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_favoritegroup')
        response = self.client.post(url, {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-name': 'Existing Group',
            'form-0-user': self.user.pk,
        })
        # Should not redirect on form error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '同じ名前では作成できません。')


class WorkNotificationRecipientViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )
        self.usersetting = UserSetting.objects.create(user=self.user)

    def test_work_notification_recipient_view_url_resolves(self):
        """
        勤務通知先設定のURLが正しく解決されるかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_worknotificationrecipient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_work_notification_recipient_view_uses_correct_template(self):
        """
        勤務通知先設定が正しいテンプレートを使用しているかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_worknotificationrecipient')
        response = self.client.get(url)
        self.assertTemplateUsed(
            response, 'swsm/usersetting_worknotificationrecipient.html')

    def test_work_notification_recipient_view_permission_denied_for_unauthenticated_user(self):  # noqa: E501
        """
        未認証ユーザーが勤務通知先設定にアクセスした場合に
        PermissionDenied が発生するかテスト。
        """
        url = reverse('swsm:usersetting_worknotificationrecipient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_work_notification_recipient_add(self):
        """
        勤務通知先が正しく追加されるかテスト。
        """
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_worknotificationrecipient')
        response = self.client.post(url, {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-recipient': 'new@example.com',
            'form-0-user': self.user.pk,
        })
        self.assertEqual(response.status_code, 302)
        exists = WorkNotificationRecipient.objects.filter(
            user=self.user, recipient='new@example.com').exists()
        self.assertTrue(exists)

    def test_work_notification_recipient_add_duplicate_email(self):
        """
        同じメールアドレスの勤務通知先を追加しようとした場合に
        エラーが発生するかテスト。
        """
        WorkNotificationRecipient.objects.create(
            user=self.user, recipient='existing@example.com')
        self.client.login(email="test@example.com", password="password123")
        url = reverse('swsm:usersetting_worknotificationrecipient')
        response = self.client.post(url, {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-recipient': 'existing@example.com',
            'form-0-user': self.user.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '同じメアドでは作成できません。')
