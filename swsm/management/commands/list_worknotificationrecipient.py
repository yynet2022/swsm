# -*- coding: utf-8 -*-
from ..base import MyBaseCommand, ObjectDoesNotExist, _strtobool
from ...models import WorkNotificationRecipient
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(MyBaseCommand):
    Model = WorkNotificationRecipient

    def do_csv_line(self, ln, commit):
        u, recipient, act = [x.strip() for x in ln]

        user = User.objects.get(email=u)
        is_active = _strtobool(act)

        try:
            x = self.Model.objects.get(user=user, recipient=recipient)
            if x.is_active != is_active:
                x.is_active = is_active
                changed = True
            self.do_update(x, commit, changed)
        except ObjectDoesNotExist:
            x = self.Model(user=user,
                           recipient=recipient,
                           is_active=is_active)
            self.do_create(x, commit)
