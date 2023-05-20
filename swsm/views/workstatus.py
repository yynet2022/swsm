# -*- coding: utf-8 -*-
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from ..apps import AppConfig
from ..models import WorkStatus, UserLog, Holiday
import datetime
from textwrap import indent

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)


def send_mail(subject, message, from_email, recipient_list):
    connection = get_connection(False)
    mail = EmailMultiAlternatives(
        subject, message, from_email, recipient_list,
        connection=connection,
        headers={'X-swsm': 'workstatus/1.0'},
    )
    return mail.send()


def is_dayoff(date):
    try:
        # もし登録があるならそれに従う。
        # 土曜日勤務の場合もありえるから。
        x = Holiday.objects.get(date=date)
        return x.dayoff
    except Exception:
        pass
    w = date.weekday()
    if w == 5 or w == 6:  # 土曜日 or 日曜日
        return True
    return False


def make_schstr(s):
    q = ''
    v = s.vacation_f()
    if v:
        q += v + '\n'
    w = s.working_f()
    if w:
        q += w + '\n'
    ws = s.ws_time_f()
    we = s.we_time_f()
    if ws and we:
        q += '出社 ' + ws.strftime('%H:%M') + \
            ' - ' + we.strftime('%H:%M') + '\n'
    zs = s.zs_time_f()
    ze = s.ze_time_f()
    if zs and ze:
        q += '在宅 ' + zs.strftime('%H:%M') + \
            ' - ' + ze.strftime('%H:%M') + '\n'
    dc = s.description
    if dc:
        q += dc + '\n'
    return indent(q, '  ')


def get_schstr(u, n):
    d = datetime.date.today()
    schstr = '本日 (%s) の予定:\n' % d
    try:
        s = u.schedule_set.get(date=d)
        schstr += make_schstr(s)
    except Exception:
        schstr += '  (登録されていません)\n'

    W = ['月', '火', '水', '木', '金', '土', '日']
    p = 0
    for x in range(n):
        dd = d + datetime.timedelta(days=x+1)
        try:
            s = u.schedule_set.get(date=dd)
            schstr += '\n%s (%s):\n' % (dd, W[dd.weekday()])
            schstr += make_schstr(s)
            if s.vacation != 10:
                break
            p += 1
            if p > 2:
                break
        except Exception:
            if not is_dayoff(dd):
                schstr += '\n%s (%s):\n' % (dd, W[dd.weekday()])
                schstr += '  (登録されていません)\n'
                break
    return schstr


def work_status(request, *args, **kwargs):
    logger.info("> In work_status: request=%s", request)
    # logger.info(">    args=%s", args)
    # logger.info(">    kwargs=%s", kwargs)
    logger.info(">    request.POST=%s", request.POST)

    next_url = AppConfig.name + ':home'
    if request.method.lower() == 'post':
        if request.user.is_authenticated:
            try:
                submit = request.POST['workstatus']
                next_url = request.POST['next']
            except Exception:
                submit = ""
                next_url = AppConfig.name + ':home'
            logger.info("> submit=%s", submit)
            logger.info("> next_url=%s", next_url)

            s = request.user.schedule_set
            if not s.filter(date=datetime.date.today()).exists():
                logger.error(" In work_status: not exist schedule")
                return render(request,
                              AppConfig.name + '/error_wnrnosch.html',
                              {'error_str': "Not exist schedule for today.", })

            try:
                workstatus = WorkStatus.objects.get(user=request.user)
            except Exception:
                workstatus = WorkStatus.objects.create(user=request.user)

            title = None
            if submit == "in":
                logger.info("> workstatus to IN")
                ws = workstatus.status
                workstatus.status = 10
                workstatus.update_at = timezone.now()
                workstatus.save()
                if ws == 20:
                    title = "勤務再開"
                else:
                    title = "勤務開始"

            elif submit == "stop":
                logger.info("> workstatus to STOP")
                workstatus.status = 20
                workstatus.update_at = timezone.now()
                workstatus.save()
                title = "勤務中断"

            elif submit == "out":
                logger.info("> workstatus to OUT")
                workstatus.status = 0
                workstatus.update_at = timezone.now()
                workstatus.save()
                title = "勤務終了"

            to_addr = []
            if title is not None:
                UserLog.objects.create(user=request.user,
                                       message=title)

                try:
                    to_addr = [
                        x.recipient for x in
                        request.user.worknotificationrecipient_set.all()]
                except Exception:
                    pass

            if title is not None and len(to_addr) > 0:
                if request.user.email not in to_addr:
                    to_addr.append(request.user.email)

                nn = 0
                if workstatus.status == 0:  # 終了のとき
                    nn = 14
                schstr = get_schstr(request.user, nn)
                current_site = get_current_site(request)
                domain = current_site.domain
                try:
                    myname = request.user.usersetting.nickname
                except Exception:
                    myname = ''
                if not myname:
                    myname = request.user.get_short_name()
                context = {
                    'protocol': request.scheme,
                    'domain': domain,
                    'title': title,
                    'name': myname,
                    'schstr': schstr,
                    'from_addr': settings.DEFAULT_FROM_EMAIL,
                    'REMOTE_ADDR': request.META.get('REMOTE_ADDR'),
                }
                try:
                    subject = render_to_string(
                        AppConfig.name + '/mail/wnr_subject.txt',
                        context).strip()
                    message = render_to_string(
                        AppConfig.name + '/mail/wnr_message.txt', context)
                    logger.info("> message:[%s]", message)
                    send_mail(subject, message, request.user.email, to_addr)
                except Exception as e:
                    logger.error(" In work_status: error: %s", str(e))
                    return render(request,
                                  AppConfig.name + '/error_wnrmail.html',
                                  {'error_str': str(e), })

    # print(request.get_full_path())
    # print(request.META.get('HTTP_REFERER'))
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect(next_url)
