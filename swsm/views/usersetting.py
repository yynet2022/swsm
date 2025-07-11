# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.utils import IntegrityError
from ..apps import AppConfig
from ..forms import UserSettingForm
from ..models import (UserSetting, get_usersetting_object,
                      FavoriteGroup, get_favoritegroup_object,
                      WorkNotificationRecipient)

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class UserSettingView(generic.UpdateView):
    template_name = AppConfig.name + '/usersetting.html'
    model = UserSetting
    form_class = UserSettingForm

    def get_object(self):
        return get_usersetting_object(self.request.user)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise PermissionDenied

        logger.info("> us.get_context_data: obj=%s", self.object)
        logger.info("> us.get_context_data: user=%s", self.request.user)

        context = super().get_context_data(**kwargs)
        context['usersetting_leftmenuitem_1'] = 'active'
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
                    obj.favorite_group_primary = \
                        get_favoritegroup_object(self.request.user)
                logger.info(" Update: %s", obj)
                obj.save()

        return redirect(AppConfig.name + ':home')


class FavoriteGroupForm(forms.ModelForm):
    class Meta:
        model = FavoriteGroup
        fields = ('name', )
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', }),
        }


class FavoriteGroupBaseModelFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        names = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            name = form.cleaned_data.get('name')
            if name is None:
                continue
            if name in names:
                err = '同じ名前では作成できません。: ' + name
                raise ValidationError(err)
            names.append(name)


def usersetting_favoritegroup(request, *args, **kwargs):
    logger.info("> In usersetting_favoritegroup: request=%s", request)
    if not request.user.is_authenticated:
        raise PermissionDenied

    # もし万が一作成されてなかったら、強制的に作成しておく。
    s = get_usersetting_object(request.user)
    f = get_favoritegroup_object(request.user)
    if s.favorite_group_primary is None:
        s.favorite_group_primary = f
        logger.info("> pre-create: %s", s)
        s.save()

    qs_org = request.user.favoritegroup_set.all().order_by('name')
    FavoriteGroupFormSet = forms.modelformset_factory(
        model=FavoriteGroup, form=FavoriteGroupForm,
        formset=FavoriteGroupBaseModelFormSet,
        extra=5, can_delete=True,
    )
    formset = FavoriteGroupFormSet(request.POST or None, queryset=qs_org)
    if request.method.lower() == 'post' and formset.is_valid():
        logger.info("> formset: valid: ok.")
        formset.save(commit=False)

        for x in formset.deleted_objects:
            logger.info(" Delete: %s", x)
            x.delete()

        for form in formset.saved_forms:
            q = form.instance
            q.user = request.user
            logger.info(" Update: %s", q)
            try:
                q.save()
                # そんなに多くないだろうから bulk_create() は使わない。
                # 一旦消去してから作り直すことをすると、
                # 関連する FavoriteGroupUser が削除されてしまうので注意。
            except IntegrityError as e:
                form.add_error(None, "同じ名前のグループが既に存在します。")
                logger.error("save(): IntegrityError: %s", str(e))
            except Exception as e:
                logger.error("save(): Unexpected Exception: %s: %s",
                             type(e), str(e))

        # もし全部消してしまったら作るし、登録する。
        x = get_favoritegroup_object(request.user)
        if request.user.usersetting.favorite_group_primary is None:
            request.user.usersetting.favorite_group_primary = x
            request.user.usersetting.save()
        return redirect(AppConfig.name + ':usersetting_favoritegroup')

    elif request.method.lower() == 'post':
        logger.error("usersetting_favoritegroup:")
        logger.error("formset.errors: %s", str(formset.errors))

    context = {
        'formset': formset,
        'usersetting_leftmenuitem_2': 'active',
    }
    return render(request,
                  AppConfig.name + '/usersetting_favoritegroup.html', context)


class WorkNotificationRecipientForm(forms.ModelForm):
    class Meta:
        model = WorkNotificationRecipient
        fields = ('recipient', )
        widgets = {
            'recipient': forms.EmailInput(
                attrs={'class': 'form-control',
                       'autocomplete': 'email',
                       'placeholder': 'メールアドレス',
                       }),
        }


class WorkNotificationRecipientBaseModelFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        recipients = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            recipient = form.cleaned_data.get('recipient')
            if recipient is None:
                continue
            if recipient in recipients:
                err = '同じメアドでは作成できません。: ' + recipient
                raise ValidationError(err)
            recipients.append(recipient)


def usersetting_worknotificationrecipient(request, *args, **kwargs):
    logger.info("> In usersetting_w.n.r: request=%s", request)
    if not request.user.is_authenticated:
        raise PermissionDenied

    # もし万が一作成されてなかったら、強制的に作成する。
    get_usersetting_object(request.user)

    qs_org = request.user.worknotificationrecipient_set.all() \
                                                       .order_by('recipient')
    WorkNotificationRecipientFormSet = forms.modelformset_factory(
        model=WorkNotificationRecipient,
        form=WorkNotificationRecipientForm,
        formset=WorkNotificationRecipientBaseModelFormSet,
        extra=5, can_delete=True,
    )
    formset = WorkNotificationRecipientFormSet(
        request.POST or None, queryset=qs_org)
    if request.method.lower() == 'post' and formset.is_valid():
        logger.info("> formset: valid: ok.")
        formset.save(commit=False)

        for x in formset.deleted_objects:
            logger.info(" Delete: %s", x)
            x.delete()

        for form in formset.saved_forms:
            q = form.instance
            q.user = request.user
            logger.info(" Update: %s", q)
            try:
                q.save()
                # そんなに多くないだろうから bulk_create() は使わない。
                # 一旦消去してから作り直すことをすると、
                #  ... 別に構わない、かな？
            except IntegrityError as e:
                form.add_error(None, "同じメアドでは作成できません。")
                logger.error("save(): IntegrityError: %s", str(e))
            except Exception as e:
                logger.error("save(): Unexpected Exception: %s: %s",
                             type(e), str(e))

        return redirect(AppConfig.name +
                        ':usersetting_worknotificationrecipient')

    elif request.method.lower() == 'post':
        logger.error("usersetting_worknotificationrecipient:")
        logger.error("formset.error: %s", str(formset.errors))

    context = {
        'formset': formset,
        'usersetting_leftmenuitem_3': 'active',
    }
    return render(
        request,
        AppConfig.name + '/usersetting_worknotificationrecipient.html',
        context)
