# -*- coding: utf-8 -*-
from django.core.management.utils import get_random_secret_key
secret_key = get_random_secret_key()
print("SECRET_KEY = '{0}'".format(secret_key))
