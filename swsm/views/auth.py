# -*- coding: utf-8 -*-
import hashlib
import base64
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from ..apps import AppConfig
from ..models import UserLog
from ..forms import EmailForm

import logging
logger = logging.getLogger(__name__)
# logger.setLevel(logging.WARNING)
logger.setLevel(logging.INFO)

User = get_user_model()


class InputAddress(generic.FormView):
    """ログインのためにメールアドレスを入力するビュー"""
    form_class = EmailForm

    def get(self, request, *args, **kwargs):
        logger.error(" In input address: error: GET.")
        return render(self.request,
                      AppConfig.name + '/error_and_home.html',
                      {'error_str': 'GET request', })

    def form_invalid(self, form):
        logger.error(" In input address: error: form invalid.")
        return render(self.request,
                      AppConfig.name + '/error_and_home.html',
                      {'error_str': 'form invalid', })

    def form_valid(self, form):
        submit = form.data.get('auth_submit', None)
        logger.debug("> form_valid: submit=%s", submit)

        email = form.cleaned_data.get('email', None)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email)
            user.is_active = False

        atime = timezone.now()
        token_str = "<" + user.email + ">" + str(atime) + "yy"

        user.access_at = atime
        user.token = hashlib.sha256(token_str.encode()).hexdigest()
        user.save()
        logger.debug("> user.save: %s", user)

        current_site = get_current_site(self.request)
        domain = current_site.domain
        expire = atime + User.TIMEOUT
        sid = str(user.id).replace('-', 'z')
        logger.debug("> sid: %s", sid)
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'eid': base64.b64encode(sid.encode()).decode(),
            'expire': str(timezone.localtime(expire)),
            'user': user,
            'from_addr': settings.DEFAULT_FROM_EMAIL,
        }
        try:
            subject = render_to_string(
                AppConfig.name + '/mail/subject.txt', context).strip()
            message = render_to_string(
                AppConfig.name + '/mail/message.txt', context)
            # logger.info("> message:[%s]", message)
            user.email_user(subject=subject, message=message)
        except Exception as e:
            logger.error(" In input address: error: %s", str(e))
            return render(self.request,
                          AppConfig.name + '/error_and_home.html',
                          {'error_str': str(e), })

        return redirect(AppConfig.name + ':inputedaddress')


class InputedAddress(generic.TemplateView):
    template_name = AppConfig.name + '/inputed_address.html'


class AuthTokenEmail(generic.TemplateView):
    """ホントにログインの処理をするビュー"""
    template_name = AppConfig.name + '/auth_token_email.html'

    def get_context_data(self, **kwargs):
        """ 表示する内容を決めるメソッド """
        token = self.kwargs.get('token')
        eid = self.kwargs.get('eid')
        logger.debug("> eid: %s", eid)
        try:
            pk = base64.b64decode(eid).decode().replace('z', '-')
        except Exception:
            pk = None
        logger.debug("> auth:token:%s", token)
        logger.debug("> auth:pk:%s", pk)

        user = authenticate(pk=pk, token=token)
        if user is not None:
            login(self.request, user)
            logger.debug("> auth:OK")
            UserLog.objects.create(user=user, message="ログイン成功")
        else:
            logger.warning("> auth:NG")
        return super().get_context_data(**kwargs)


def LogoutView(request):
    logout(request)
    return redirect(AppConfig.name + ':home')
