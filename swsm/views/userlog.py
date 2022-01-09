# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import PermissionDenied
from django.db.models import Q
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


class UserLogExtraForm(forms.Form):
    check_work_start = forms.BooleanField(
        label="勤務開始",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input me-2', }),
    )
    check_work_end = forms.BooleanField(
        label="勤務終了",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input me-2', }),
    )
    check_work_stop = forms.BooleanField(
        label="勤務中断",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input me-2', }),
    )
    check_work_restart = forms.BooleanField(
        label="勤務再開",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input me-2', }),
    )


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

    filterbits = kwargs.get('filterbits')
    if filterbits is None:
        filterbits = 0xff

    qc = Q(user=request.user)

    BIT_WORK_START = 0b000001
    BIT_WORK_END = 0b000010
    BIT_WORK_STOP = 0b000100
    BIT_WORK_RESTART = 0b001000
    extraform_initial = {
        'check_work_start':   bool(filterbits & BIT_WORK_START),
        'check_work_end':     bool(filterbits & BIT_WORK_END),
        'check_work_stop':    bool(filterbits & BIT_WORK_STOP),
        'check_work_restart': bool(filterbits & BIT_WORK_RESTART),
    }
    extraform = UserLogExtraForm(request.POST or None,
                                 initial=extraform_initial)
    if request.method == 'POST' and extraform.is_valid():
        if extraform.cleaned_data['check_work_start']:
            filterbits |= BIT_WORK_START
        else:
            filterbits &= ~BIT_WORK_START
        if extraform.cleaned_data['check_work_end']:
            filterbits |= BIT_WORK_END
        else:
            filterbits &= ~BIT_WORK_END
        if extraform.cleaned_data['check_work_stop']:
            filterbits |= BIT_WORK_STOP
        else:
            filterbits &= ~BIT_WORK_STOP
        if extraform.cleaned_data['check_work_restart']:
            filterbits |= BIT_WORK_RESTART
        else:
            filterbits &= ~BIT_WORK_RESTART

    if not (filterbits & BIT_WORK_START):
        qc &= ~Q(message="勤務開始")
    if not (filterbits & BIT_WORK_END):
        qc &= ~Q(message="勤務終了")
    if not (filterbits & BIT_WORK_STOP):
        qc &= ~Q(message="勤務中断")
    if not (filterbits & BIT_WORK_RESTART):
        qc &= ~Q(message="勤務再開")

    qs = UserLog.objects.filter(qc) \
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

        # オブジェクトが削除されたのなら、pnum は (厳密には) 作成し直すべき。
        # でも、実質的に、そんなに悪影響は無いと思うので。
        # 動作は、多少「あれ？」と思うこともあるだろうけど。
        return redirect(AppConfig.name + ':userlog',
                        filterbits=filterbits, page=pnum)
    elif request.method == 'POST':  # ここも通らないハズ
        logger.error("> formset: not valid: %s" % formset.errors)
        logger.error("> formset: errors: %d" % formset.total_error_count())
        logger.error("> formset: form: %s" % formset.non_form_errors())

    context = {
        'formset': formset,
        'extraform': extraform,
        'filterbits': filterbits,
        'page_obj': pobj,
    }
    return render(request, AppConfig.name + '/userlog.html', context)
