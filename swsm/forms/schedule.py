# -*- coding: utf-8 -*-
from django import forms
# from django.utils.translation import gettext_lazy as _
from ..models import Schedule

import logging
logger = logging.getLogger(__name__)
# logger.setLevel(logging.WARNING)
logger.setLevel(logging.INFO)


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('date', 'vacation', 'working',
                  'ws_time', 'we_time',
                  'zs_time', 'ze_time',
                  'description')

        widgets = {
            'date':     forms.HiddenInput(),
            'vacation': forms.Select(attrs={'class': 'form-select', }),
            'working':  forms.Select(attrs={'class': 'form-select', }),
            'ws_time':  forms.TimeInput(format='%H:%M',
                                        attrs={'class': 'form-control',
                                               'maxlength': 10, 'size': 8, }),
            'we_time':  forms.TimeInput(format='%H:%M',
                                        attrs={'class': 'form-control',
                                               'maxlength': 10, 'size': 8, }),
            'zs_time':  forms.TimeInput(format='%H:%M',
                                        attrs={'class': 'form-control',
                                               'maxlength': 10, 'size': 8, }),
            'ze_time':  forms.TimeInput(format='%H:%M',
                                        attrs={'class': 'form-control',
                                               'maxlength': 10, 'size': 8, }),
            'description': forms.Textarea(attrs={'class': 'form-control', }),
        }
        """
        help_texts = {
            'date':     _('forms.HiddenInput'),
            'vacation': _('休暇だよん'),
            'working':  _('ざいたく？'),
            'ws_time':  _('しごとはじめ'),
            'we_time':  _('しごとおわり'),
            'zs_time':  _('ざいたくはじめ'),
            'ze_time':  _('ざいたくおわり'),
            'description': _('ほかにかくことある？'),
        }
        """

    def clean_we_time(self):
        # logger.info("> In clean_we_time:cleaned_data=%s" % self.cleaned_data)
        if "ws_time" not in self.cleaned_data.keys():
            raise forms.ValidationError('出社予定時間が設定されていません')
        if "we_time" not in self.cleaned_data.keys():
            raise forms.ValidationError('退社予定時間が設定されていません')

        ws_time = self.cleaned_data['ws_time']
        we_time = self.cleaned_data['we_time']
        if we_time <= ws_time:
            raise forms.ValidationError(
                '退社予定時間は、出社予定時間よりも後にしてください'
            )
        return we_time

    def clean_ze_time(self):
        if "zs_time" not in self.cleaned_data.keys():
            raise forms.ValidationError('在宅開始時間が設定されていません')
        if "ze_time" not in self.cleaned_data.keys():
            raise forms.ValidationError('在宅終了時間が設定されていません')
        zs_time = self.cleaned_data['zs_time']
        ze_time = self.cleaned_data['ze_time']
        if ze_time <= zs_time:
            raise forms.ValidationError(
                '在宅終了時間は、在宅開始時間よりも後にしてください'
            )
        return ze_time
