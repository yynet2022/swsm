# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render, redirect
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
            if x.exists():
                return x.first()
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
                    if x.exists():
                        f = x.first()
                    else:
                        f = FavoriteGroup.objects.create(
                            user=self.request.user,
                            name="お気に入り",
                        )
                    obj.favorite_group_primary = f
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


def usersetting_favoritegroup(request, *args, **kwargs):
    logger.info("> In usersetting_favoritegroup: request=%s", request)
    if not request.user.is_authenticated:
        raise PermissionDenied

    if not UserSetting.objects.filter(user=request.user).exists():
        # もし万が一作成されてなかったら、強制的に作成する。
        UserSetting.objects.create(user=request.user)

    qs_org = request.user.favoritegroup_set.all().order_by('name')
    FavoriteGroupFormSet = forms.modelformset_factory(
        FavoriteGroup, form=FavoriteGroupForm, extra=5, can_delete=True,
    )
    formset = FavoriteGroupFormSet(request.POST or None, queryset=qs_org)
    if request.method == 'POST' and formset.is_valid():
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
            except Exception as e:
                logger.error("save(): %s: %s", type(e), str(e))

        if not request.user.favoritegroup_set.all().exists():
            # もし全部消してしまったら
            FavoriteGroup.objects.create(
                user=request.user,
                name="お気に入り",
            )
        if request.user.usersetting.favorite_group_primary is None:
            request.user.usersetting.favorite_group_primary = \
                request.user.favoritegroup_set.all().first()
            request.user.usersetting.save()
        return redirect(AppConfig.name + ':usersetting_favoritegroup')

    elif request.method == 'POST':
        logger.error("usersetting_favoritegroup:")
        logger.error("formset: %s", str(formset))

    context = {
        'formset': formset,
    }
    return render(request,
                  AppConfig.name + '/usersetting_favoritegroup.html', context)
