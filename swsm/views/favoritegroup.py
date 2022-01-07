# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from ..apps import AppConfig
from ..models import FavoriteGroup, FavoriteGroupUser
import base64

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


def __redirect(request):
    try:
        next_url = request.POST.get('next')
        logger.info("> next_url: %s", next_url)

        return redirect(next_url)
    except Exception as e:
        logger.error("> next_url.error: %s", str(e))
    return redirect(AppConfig.name + ':home')


def favorite_group_member_add(request, *args, **kwargs):
    logger.info("> In favorite_group_member_add: request=%s", request)
    if not request.user.is_authenticated:
        raise PermissionDenied

    try:
        fg_eid = request.POST.get('fg_eid')
        logger.info("> fg:eid: %s", fg_eid)

        fg_pk = base64.b64decode(fg_eid).decode().replace('z', '-')
        logger.info("> fg:pk: %s", fg_pk)

        fg = FavoriteGroup.objects.get(pk=fg_pk)
    except Exception as e:
        logger.error("> fg.error: %s", str(e))
        return __redirect(request)

    try:
        mm_eid = request.POST.get('mm_eid')
        logger.info("> mm:eid: %s", mm_eid)

        mm_pk = base64.b64decode(mm_eid).decode().replace('z', '-')
        logger.info("> mm:pk: %s", mm_pk)

        mm = User.objects.get(pk=mm_pk)
    except Exception as e:
        logger.error("> mmk.error: %s", str(e))
        return __redirect(request)

    try:
        x = FavoriteGroupUser.objects.create(favorite_group=fg, member=mm)
        logger.info("> %s", x)
    except Exception as e:
        logger.error("> FGU.create.error: %s", str(e))

    return __redirect(request)


def favorite_group_member_del(request, *args, **kwargs):
    logger.info("> In favorite_group_member_del: request=%s", request)
    if not request.user.is_authenticated:
        raise PermissionDenied

    try:
        fgu_eid = request.POST.get('fgu_eid')
        logger.info("> fgu:eid: %s", fgu_eid)

        fgu_pk = base64.b64decode(fgu_eid).decode().replace('z', '-')
        logger.info("> fgu:pk: %s", fgu_pk)

        FavoriteGroupUser.objects.get(pk=fgu_pk).delete()
    except Exception as e:
        logger.error("> fgu.error: %s", str(e))

    return __redirect(request)
