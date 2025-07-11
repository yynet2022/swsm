# -*- coding: utf-8 -*-
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from swsm.models import Schedule, Information

User = get_user_model()


class HomeViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123"
        )
        self.superuser = User.objects.create_superuser(
            email="superuser@example.com",
            password="password123"
        )
        self.today = datetime.date.today()
        self.client.force_login(self.user)  # Added force_login

    def test_home_view_url_resolves(self):
        """
        ホームビューのURLが正しく解決されるかテスト。
        """
        response = self.client.get(reverse('swsm:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_uses_correct_template(self):
        """
        ホームビューが正しいテンプレートを使用しているかテスト。
        """
        response = self.client.get(reverse('swsm:home'))
        self.assertTemplateUsed(response, 'swsm/home.html')

    def test_home_view_context_data_for_unauthenticated_user(self):
        """
        未認証ユーザーのコンテキストデータが正しいかテスト。
        """
        self.client.logout()  # Logout to test unauthenticated user
        response = self.client.get(reverse('swsm:home'))
        self.assertIn('today', response.context)
        self.assertIn('date', response.context)
        self.assertIn('userlist', response.context)
        self.assertIn('informations', response.context)
        self.assertIn('favorite_infos', response.context)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_home_view_context_data_for_authenticated_user(self):
        """
        認証済みユーザーのコンテキストデータが正しいかテスト。
        """
        # Removed
        # self.client.login(email="test@example.com", password="password123")

        response = self.client.get(reverse('swsm:home'))
        self.assertIn('today', response.context)
        self.assertIn('date', response.context)
        self.assertIn('userlist', response.context)
        self.assertIn('informations', response.context)
        self.assertIn('favorite_infos', response.context)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_schedule_add_for_authenticated_user(self):
        """
        認証済みユーザーがスケジュールを追加できるかテスト。
        """
        # Removed
        # self.client.login(email="test@example.com", password="password123")
        response = self.client.post(reverse('swsm:home'), {
            'date': self.today,
            'vacation': 0,  # Default value
            'working': 10,  # Default value
            'ws_time': '09:00',
            'we_time': '17:00',
            'zs_time': '09:00',
            'ze_time': '17:00',
            'description': 'New schedule',
            'sch_submit': 'add'
        })
        # Redirects after successful POST
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Schedule.objects.filter(
            user=self.user, date=self.today,
            description='New schedule').exists())

    def test_schedule_update_for_authenticated_user(self):
        """
        認証済みユーザーがスケジュールを更新できるかテスト。
        """
        Schedule.objects.create(user=self.user, date=self.today,
                                description='Old schedule')
        # Removed
        # self.client.login(email="test@example.com", password="password123")
        response = self.client.post(reverse('swsm:home'), {
            'date': self.today,
            'vacation': 0,  # Default value
            'working': 10,  # Default value
            'ws_time': '09:00',
            'we_time': '17:00',
            'zs_time': '09:00',
            'ze_time': '17:00',
            'description': 'Updated schedule',
            'sch_submit': 'add'  # 'add' is used for both add and update
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Schedule.objects.filter(
            user=self.user, date=self.today,
            description='Updated schedule').exists())
        self.assertFalse(Schedule.objects.filter(
            user=self.user, date=self.today,
            description='Old schedule').exists())

    def test_schedule_delete_for_authenticated_user(self):
        """
        認証済みユーザーがスケジュールを削除できるかテスト。
        """
        Schedule.objects.create(user=self.user, date=self.today,
                                description='Schedule to delete')
        # Removed
        # self.client.login(email="test@example.com", password="password123")
        response = self.client.post(reverse('swsm:home'), {
            'date': self.today,
            'vacation': 0,  # Default value
            'working': 10,  # Default value
            'ws_time': '09:00',
            'we_time': '17:00',
            'zs_time': '09:00',
            'ze_time': '17:00',
            'sch_submit': 'del'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Schedule.objects.filter(
            user=self.user, date=self.today,
            description='Schedule to delete').exists())

    def test_schedule_operation_for_unauthenticated_user(self):
        """
        未認証ユーザーがスケジュール操作を試みた場合に PermissionDenied が発生するかテスト。
        """
        self.client.logout()  # Logout to test unauthenticated user
        response = self.client.post(reverse('swsm:home'), {
            'date': self.today,
            'description': 'New schedule',
            'sch_submit': 'add'
        })
        # PermissionDenied は通常、500 Internal Server Error として表示される
        # または、設定によってはログインページにリダイレクトされる
        # ここでは、PermissionDenied が発生することを確認するために、
        # ログインページへのリダイレクトがないことを確認する
        self.assertNotEqual(response.status_code, 302)
        self.assertFalse(Schedule.objects.filter(user=self.user).exists())

    def test_information_display(self):
        """
        連絡事項が正しく表示されるかテスト。
        """
        Information.objects.create(message="Test Info 1")
        Information.objects.create(message="Test Info 2")
        response = self.client.get(reverse('swsm:home'))
        self.assertContains(response, "Test Info 1")
        self.assertContains(response, "Test Info 2")
