# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import PermissionDenied
from ..apps import AppConfig
from ..models import UserLog

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class UserLogForm(forms.ModelForm):
    class Meta:
        model = UserLog
        fields = ('created_at', 'message', )
        widgets = {
            'created_at':  forms.DateTimeInput(
                attrs={'class': 'form-control', 'readonly': True, }),
            'message': forms.TextInput(
                attrs={'class': 'form-control', 'readonly': True, }),
        }


class UserLogMarkForm(UserLogForm):
    mark_sel = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
    )

    class Meta(UserLogForm.Meta):
        pass


def user_log(request, *args, **kwargs):
    logger.info("> In user_log: request=%s", request)
    # logger.info(">    args=%s", args)
    # logger.info(">    kwargs=%s", kwargs)
    # logger.info(">    request.POST=%s", request.POST)
    if not request.user.is_authenticated:
        raise PermissionDenied

    pnum = kwargs.get('page')
    if pnum is None:
        pnum = 1
    qs = UserLog.objects.filter(user=request.user) \
                        .order_by('created_at').reverse()
    UserLogFormset = forms.modelformset_factory(
        UserLog, form=UserLogMarkForm, extra=0,
    )

    paginator = Paginator(qs, 50)
    try:
        pnum = paginator.validate_number(pnum)
    except PageNotAnInteger:
        pnum = 1
    except EmptyPage:
        pnum = paginator.num_pages

    pobj = paginator.page(pnum)
    formset = UserLogFormset(request.POST or None, queryset=pobj.object_list)

    if request.method == 'POST' and formset.is_valid():
        logger.info("> formset: valid: ok.")
        formset.save(commit=False)

        for x in formset.deleted_objects:  # ここは通らないハズ
            logger.info(" Delete: %s", x)
            x.delete()

        for form in formset.saved_forms:
            if form.cleaned_data.get('mark_sel'):
                x = form.instance
                logger.info(" Delete: %s", x)
                x.delete()
        return redirect(AppConfig.name + ':userlog', page=pnum)
    elif request.method == 'POST':  # ここも通らないハズ
        logger.error("> formset: not valid: %s" % formset.errors)
        logger.error("> formset: errors: %d" % formset.total_error_count())
        logger.error("> formset: form: %s" % formset.non_form_errors())

    context = {
        'formset': formset,
        'page_obj': pobj,
    }
    return render(request, AppConfig.name + '/userlog.html', context)
