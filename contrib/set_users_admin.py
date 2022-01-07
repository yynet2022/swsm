# -*- coding: utf-8 -*-
## python manage.py shell < (this file)
#
from django.utils import timezone
from django.contrib.auth import get_user_model
User=get_user_model()

email_list=['yokota@yynet.org']
for email in email_list:
    try:
        user = User.objects.get(email=email)
        user.is_admin = True
        user.is_active = True
        user.save()
    except User.DoesNotExist:
        print ("No user")

    print(" >>", user, "ID>>", user.id)
