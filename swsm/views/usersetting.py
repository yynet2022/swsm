# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from ..apps import AppConfig
from ..forms import UserSettingForm
from ..models import UserSetting, FavoriteGroup

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class UserSettingView(generic.UpdateView):
    template_name = AppConfig.name + '/usersetting.html'
    model = UserSetting
    form_class = UserSettingForm

    def object_filter(self, **kwargs):
        return self.model.objects.filter(**kwargs)

    def get_object(self):
        if self.request.user.is_authenticated:
            x = self.object_filter(user=self.request.user)
            if len(x) > 0:
                return x[0]
            return self.model.objects.create(user=self.request.user)
        return None

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise PermissionDenied

        logger.info("> us.get_context_data: obj=%s", self.object)
        logger.info("> us.get_context_data: user=%s", self.request.user)

        context = super().get_context_data(**kwargs)
        logger.info("< us.get_context_data: ", context)
        return context

    def form_valid(self, form):
        """ 入力フォームから値のチェック後に来るメソッド """
        submit = form.data.get('us_submit', None)
        logger.info("> form_valid: submit=%s", submit)
        logger.info("  .object: %s", self.object)
        logger.info("  .user: %s", self.request.user)

        if submit == "ok":
            if form.has_changed() and self.request.user.is_authenticated:
                obj = form.save(commit=False)
                obj.user = self.request.user
                if not obj.favorite_group_primary:
                    logger.info(" not has fg.")
                    x = FavoriteGroup.objects.filter(user=self.request.user)
                    if len(x) > 0:
                        f = x[0]
                    else:
                        f = FavoriteGroup.objects.create(
                            user=self.request.user,
                            name="お気に入り",
                        )
                    obj.favorite_group_primary = f
                logger.info(" Update: %s", obj)
                obj.save()

        return redirect(AppConfig.name + ':home')
