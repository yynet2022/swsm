# -*- coding: utf-8 -*-
from django.utils import timezone
from django.shortcuts import redirect
from ..apps import AppConfig
from ..models import WorkStatus, UserLog

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)


def work_status(request, *args, **kwargs):
    logger.info("> In work_status: request=%s", request)
    # logger.info(">    args=%s", args)
    # logger.info(">    kwargs=%s", kwargs)
    logger.info(">    request.POST=%s", request.POST)

    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                submit = request.POST['workstatus']
                next_url = request.POST['next']
            except Exception:
                submit = ""
                next_url = AppConfig.name + ':home'
            logger.info("> submit=%s", submit)
            logger.info("> next_url=%s", next_url)

            try:
                workstatus = WorkStatus.objects.get(user=request.user)
            except Exception:
                workstatus = WorkStatus.objects.create(user=request.user)

            if submit == "in":
                logger.info("> workstatus to IN")
                ws = workstatus.status
                workstatus.status = 10
                workstatus.update_at = timezone.now()
                workstatus.save()
                if ws == 20:
                    UserLog.objects.create(user=request.user,
                                           message="勤務再開")
                else:
                    UserLog.objects.create(user=request.user,
                                           message="勤務開始")
            elif submit == "stop":
                logger.info("> workstatus to STOP")
                workstatus.status = 20
                workstatus.update_at = timezone.now()
                workstatus.save()
                UserLog.objects.create(user=request.user,
                                       message="勤務中断")
            elif submit == "out":
                logger.info("> workstatus to OUT")
                workstatus.status = 0
                workstatus.update_at = timezone.now()
                workstatus.save()
                UserLog.objects.create(user=request.user,
                                       message="勤務終了")

    """
    context = {
        'today': datetime.date.today(),
    }
    """
    # print(request.get_full_path())
    # print(request.META.get('HTTP_REFERER'))
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect(next_url)
