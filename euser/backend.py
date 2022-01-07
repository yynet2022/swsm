# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.utils import timezone
# import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class MyUserBackend(BaseBackend):
    def authenticate(self, request, pk=None, token=None):
        try:
            user = User.objects.get(pk=pk)
            expire_time = user.access_at + User.TIMEOUT
            now = timezone.now()
            if user.token != token:
                logger.error("*** auth: invalid token")
            elif expire_time < now:
                logger.error("*** auth: expire over: " + str(now))
            else:
                user.is_active = True
                user.token = "xxxxx"
                user.access_at = now
                user.save()
                return user
        except User.DoesNotExist:
            pass
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
