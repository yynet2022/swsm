# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from ..apps import AppConfig
from ..models import Schedule, Holiday, FavoriteGroupUser
from ..forms import ScheduleForm, EmailForm
from .mixins import MonthCalendarMixin, WeekCalendarMixin, UtilsCalendarMixin
import datetime
import base64

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.INFO)

User = get_user_model()


class MonthScheduleForm(ScheduleForm):
    mark_add = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                          'onclick': 'return false;', }),
    )
    mark_sel = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
    )

    class Meta(ScheduleForm.Meta):
        pass


class CalendarTools(MonthCalendarMixin,
                    WeekCalendarMixin,
                    UtilsCalendarMixin):
    model = None

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def get_context_data(self, **kwargs):
        context = kwargs
        context.update(self.get_month_calendar(self.target_date))
        context.update({
            'today': datetime.date.today(),
            'date': self.target_date,
            })
        del context['month_week_names']
        del context['month_days']
        return context


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


def month_schedules(request, *args, **kwargs):
    logger.info("> In month_schedules: request=%s", request)
    # logger.info(">    args=%s", args)
    # logger.info(">    kwargs=%s", kwargs)
    # logger.info(">    request.POST=%s", request.POST)
    if not request.user.is_authenticated:
        raise PermissionDenied

    ct = CalendarTools(request, *args, **kwargs)
    target_date = ct.target_date
    next_month = ct.get_next_month(target_date)

    ts = target_date.replace(day=1)
    te = next_month - datetime.timedelta(days=1)
    dt = te - ts
    ndays = dt.days + 1

    qs_none = Schedule.objects.none()
    target_user = request.user
    kwargs = {'user': target_user,
              'date__range': (ts, te), }
    qs_org = Schedule.objects.filter(**kwargs)

    init_data = {}
    s_time = ct.user_s_time
    e_time = ct.user_e_time
    for i in range(ndays):
        tt = target_date.replace(day=i+1)

        if is_dayoff(tt):
            continue

        init_data[tt] = {'date':    tt,
                         'ws_time': s_time,
                         'we_time': e_time,
                         'zs_time': s_time,
                         'ze_time': e_time,
                         'description': '',
                         'mark_add': True,
                         'mark_sel': False, }

    for q in qs_org:
        init_data[q.date] = {'date':        q.date,
                             'vacation':    q.vacation,
                             'working':     q.working,
                             'ws_time':     q.ws_time,
                             'we_time':     q.we_time,
                             'zs_time':     q.zs_time,
                             'ze_time':     q.ze_time,
                             'description': q.description,
                             'mark_add': False,
                             'mark_sel': False, }

    # mark_add を小細工する。バックアップを取り、全部 False に。
    org_mark_add = [init_data[x]['mark_add'] for x in sorted(init_data.keys())]
    for x in init_data.values():
        x['mark_add'] = False

    initial = [init_data[x] for x in sorted(init_data.keys())]
    ScheduleCreateFormSet = forms.modelformset_factory(
        Schedule, form=MonthScheduleForm, extra=len(initial)
    )

    submit_message = ""
    if request.method == 'POST':
        post = {}
        for k in request.POST:
            # 日付について、datetime.date 型の値になるように調整
            # 正常終了して redirect されるならこの処理は不要
            # けど、エラー (not is_valid) のとき、これが必要。
            if (k.endswith("-date")):
                rp_k = request.POST[k]
                d = datetime.date(*(int(x) for x in rp_k.split("-")))
                # logger.info(">> %s: %s" % (k, d))
                post[k] = d
            else:
                post[k] = request.POST[k]

        formset = ScheduleCreateFormSet(post,
                                        queryset=qs_none, initial=initial)
        if formset.is_valid():
            submit = ""
            try:
                submit = request.POST['form_submit']
            except Exception:
                pass

            formset.save(commit=False)

            for x in formset.deleted_objects:
                logger.info(" Delete: %s", x)
                x.delete()

            if submit == "update":
                for form in formset.saved_forms:
                    q = form.instance
                    for x in qs_org.filter(user=target_user, date=q.date):
                        x.delete()
                    q.user = target_user
                    logger.info(" Update: %s", q)
                    q.save()
            elif submit == "delete":
                for form in formset.saved_forms:
                    if form.cleaned_data.get('mark_sel'):
                        d = form.instance.date
                        for x in qs_org.filter(user=target_user, date=d):
                            logger.info(" Delete: %s", x)
                            x.delete()
            else:
                logger.warning(" Unknown submit value: %s", submit)

            return redirect(AppConfig.name + ':monthschedules',
                            year=target_date.year, month=target_date.month)
        else:
            logger.info("> formset: not valid: %s" % formset.errors)
            logger.info("> formset: errors: %d" % formset.total_error_count())
            logger.info("> formset: form: %s" % formset.non_form_errors())
    else:
        formset = ScheduleCreateFormSet(None,
                                        queryset=qs_none,
                                        initial=initial)

        k = []
        for form, x in zip(formset, org_mark_add):
            form.initial['mark_add'] = x
            if x:
                k.append(form.initial['date'])

        if len(k) > 0:
            submit_message = \
                "［お知らせ］ 未登録日があります（" + \
                str(k[0]) + " など " + str(len(k)) + \
                " 件）。暫定値が入っていますので、確認して更新してください。"

    context = ct.get_context_data()
    """ In context of ct.
    {
     'month_curr': ...,
     'month_prev': ...,
     'month_next': ...,
     'today': ...,
     'date': ...,
    }
    """
    context.update({
        'formset': formset,
        'submit_message': submit_message,
    })
    return render(request, AppConfig.name + '/monthschedules.html', context)


class MonthSchedulesEID(generic.TemplateView):
    template_name = AppConfig.name + '/monthschedules_eid.html'

    def get_context_data(self, **kwargs):
        logger.info("> In MonthSchedulesEID: request=%s", self.request)
        logger.info(">    kwargs=%s", kwargs)
        logger.info(">    self.kwargs=%s", self.kwargs)

        try:
            eid = pk = None

            eid = kwargs.get('eid')
            logger.info("> eid: %s", eid)

            pk = base64.b64decode(eid).decode().replace('z', '-')
            logger.info("> pk: %s", pk)

            target_user = User.objects.get(pk=pk)
        except Exception as e:
            logger.error(" Exception: %s", str(e))
            logger.error(" pk: %s", pk)
            logger.error(" eid: %s", eid)
            target_user = self.request.user

        ct = CalendarTools(self.request, *self.args, **self.kwargs)
        target_date = ct.target_date
        next_month = ct.get_next_month(target_date)

        ts = target_date.replace(day=1)
        te = next_month - datetime.timedelta(days=1)
        dt = te - ts
        ndays = dt.days + 1

        qkwargs = {'user': target_user,
                   'date__range': (ts, te), }
        qs_org = Schedule.objects.filter(**qkwargs)

        init_data = {}
        for i in range(ndays):
            tt = target_date.replace(day=i+1)

            if is_dayoff(tt):
                continue

            init_data[tt] = {'date':    tt,
                             'mark_add': True, }

        for q in qs_org:
            init_data[q.date] = {'date':        q.date,
                                 'vacation':    q.vacation_f(),
                                 'working':     q.working_f(),
                                 'ws_time':     q.ws_time_f(),
                                 'we_time':     q.we_time_f(),
                                 'zs_time':     q.zs_time_f(),
                                 'ze_time':     q.ze_time_f(),
                                 'description': q.description,
                                 'mark_add': False, }

        data = [init_data[x] for x in sorted(init_data.keys())]
        for x in data:
            if x['mark_add']:
                x['mark_add'] = '×'
            else:
                x['mark_add'] = ''

        if self.request.user.is_authenticated:
            ulist = User.objects.all().exclude(pk=self.request.user.pk)
        else:
            ulist = User.objects.all()

        fg = fgu = None
        fgl = ()
        try:
            fg = self.request.user.usersetting.favorite_group_primary
            fgl = FavoriteGroupUser.objects.filter(favorite_group=fg)
            fgu = FavoriteGroupUser.objects.get(favorite_group=fg,
                                                member=target_user)
        except Exception:
            pass

        is_target_in_favorite = False
        if (len(fgl) > 0 and target_user.pk == self.request.user.pk) or \
           target_user in [x.member for x in fgl]:
            is_target_in_favorite = True

        self.extra_context = ct.get_context_data()
        """ In context of ct.
        {
        'month_curr': ...,
        'month_prev': ...,
        'month_next': ...,
        'today': ...,
        'date': ...,
        }
        """
        self.extra_context.update({
            'target_user': target_user,
            'data': data,
            'userlist': ulist.exclude(is_active=False),
            'userform': EmailForm(),
            'favorite_group': fg,
            'favorite_group_list': fgl,
            'favorite_group_user': fgu,
            'is_target_in_favorite': is_target_in_favorite,
        })
        return super().get_context_data(**kwargs)
