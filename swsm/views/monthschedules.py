# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from ..apps import AppConfig
from ..models import Schedule, Holiday, FavoriteGroup, FavoriteGroupUser
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
            'user_ls_time': self.user_ls_time,
            'user_le_time': self.user_le_time,
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
    working_at = ct.user_working_at
    for i in range(ndays):
        tt = target_date.replace(day=i+1)

        if is_dayoff(tt):
            continue

        init_data[tt] = {'date':    tt,
                         'ws_time': s_time,
                         'we_time': e_time,
                         'zs_time': s_time,
                         'ze_time': e_time,
                         'working': working_at,
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
    if request.method.lower() == 'post':
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
                objs = []
                for form in formset.saved_forms:
                    q = form.instance
                    qs_org.filter(user=target_user, date=q.date).delete()
                    q.user = target_user
                    logger.info(" Update: %s", q)
                    objs.append(q)
                    # q.save()
                Schedule.objects.bulk_create(objs)
            elif submit == "delete":
                for form in formset.saved_forms:
                    if form.cleaned_data.get('mark_sel'):
                        d = form.instance.date
                        qs_org.filter(user=target_user, date=d).delete()
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


class MonthSchedulesEID(generic.FormView):
    template_name = AppConfig.name + '/monthschedules_eid.html'

    def get_fav_infos(self, target_user=None):
        if target_user is None:
            target_user = self.get_target_user()
        fav_infos = []
        try:
            u = self.request.user
            for g in u.favoritegroup_set.all().order_by('name'):
                x = {'name': g.name,
                     'eid': g.get_eid(),
                     'op_eid': g.get_eid(),
                     'primary': False,
                     'has_target_user': False,
                     'members': [],
                     }

                try:
                    p = u.usersetting.favorite_group_primary
                    if g.pk == p.pk:
                        x['primary'] = True
                except Exception:
                    pass

                for u in g.favoritegroupuser_set.all().order_by('created_at'):
                    p = {'user': u.member,
                         'eid': u.get_eid(),
                         }
                    if u.member.pk == target_user.pk:
                        x['has_target_user'] = True
                        x['op_eid'] = u.get_eid()
                    x['members'].append(p)
                fav_infos.append(x)
                # print(x)
        except Exception:
            # print(type(e), '::', str(e))
            # ex)
            # <class 'AttributeError'> ::
            #    'AnonymousUser' object has no attribute 'favoritegroup_set'
            pass
        return fav_infos

    def get_form(self):
        fav_infos = self.get_fav_infos()
        choices = []
        for x in fav_infos:
            if x['has_target_user']:
                choices.append(('del-'+x['op_eid'], x['name']+'から削除'))
            else:
                choices.append(('add-'+x['op_eid'], x['name']+'に追加'))

        if len(choices) > 0:
            class _ExtraForm(forms.Form):
                choice = forms.ChoiceField(
                    label="お気に操作",
                    choices=choices,
                    required=True,
                    widget=forms.Select(
                        attrs={'class': 'form-select', }),
                )
            return _ExtraForm(self.request.POST or None)
        return None

    def get_target_user(self):
        try:
            eid = pk = None

            eid = self.kwargs.get('eid')
            logger.info("> eid: %s", eid)

            pk = base64.b64decode(eid).decode().replace('z', '-')
            logger.info("> pk: %s", pk)

            return User.objects.get(pk=pk)
        except Exception as e:
            logger.error("MonthSchedulesEID.get_target_user:")
            logger.error(" Exception: %s", str(e))
            logger.error(" pk: %s", pk)
            logger.error(" eid: %s", eid)
            return self.request.user

    def form_invalid(self, form):
        logger.error("MonthSchedulesEID.form_invalid: %s", form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise PermissionDenied

        target_user = self.get_target_user()
        if self.request.user.pk != target_user.pk:
            choice = form.cleaned_data.get('choice', None)
            try:
                if choice.startswith('add-'):
                    x, eid = choice.split('-')

                    pk = base64.b64decode(eid).decode().replace('z', '-')
                    fg = FavoriteGroup.objects.get(pk=pk)

                    x = FavoriteGroupUser.objects.create(
                        favorite_group=fg, member=target_user)
                    logger.info("Create: %s", x)
                elif choice.startswith('del-'):
                    x, eid = choice.split('-')

                    pk = base64.b64decode(eid).decode().replace('z', '-')
                    fg = FavoriteGroupUser.objects.get(pk=pk)
                    logger.info("Delete: %s", fg)
                    fg.delete()
            except Exception as e:
                logger.error("MonthSchedulesEID.form_valid:")
                logger.error(" :%s", type(e))
                logger.error(" :%s", str(e))

        ct = CalendarTools(self.request, *self.args, **self.kwargs)
        target_date = ct.target_date
        return redirect(AppConfig.name + ':monthschedules_eid',
                        eid=target_user.get_eid(),
                        year=target_date.year, month=target_date.month)

    def get_context_data(self, **kwargs):
        logger.info("> In MonthSchedulesEID: request=%s", self.request)
        logger.info(">    kwargs=%s", kwargs)
        logger.info(">    self.kwargs=%s", self.kwargs)

        target_user = self.get_target_user()

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

        fav_infos = self.get_fav_infos(target_user)

        is_target_in_favorite = False
        if (sum(len(x['members']) for x in fav_infos) > 0 and
            target_user.pk == self.request.user.pk) or (
                True in [x['has_target_user'] for x in fav_infos]):
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
            'is_target_in_favorite': is_target_in_favorite,
            'favorite_infos': fav_infos,
        })
        return super().get_context_data(**kwargs)
