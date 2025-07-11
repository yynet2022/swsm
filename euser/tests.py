# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user(self):
        """
        create_user() を使って、ユーザーが問題なく作成されるか確認。
        """
        email = "test@example.com"
        password = "password123"
        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_admin)

    def test_create_superuser(self):
        """
        create_superuser() を使って、スーパーユーザーが問題なく作成されるか確認。
        """
        email = "superuser@example.com"
        password = "password123"
        user = User.objects.create_superuser(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin)

    def test_email_is_required(self):
        """
        email がない場合に ValueError が発生するか確認。
        """
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="password123")

    def test_email_is_unique(self):
        """
        同じ email でユーザーを作成しようとした場合に IntegrityError が発生するか確認。
        """
        email = "test@example.com"
        password = "password123"
        User.objects.create_user(email=email, password=password)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email=email, password="password456")
