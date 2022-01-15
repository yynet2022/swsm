# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import UserSetting


class UserSettingForm(forms.ModelForm):
    class Meta:
        model = UserSetting
        fields = ('nickname',
                  's_time', 'e_time',
                  'rows_description',
                  'show_weekend', 'show_month_calendar')
        widgets = {
            'nickname': forms.TextInput(
                attrs={'class': 'form-control', }),
            's_time':  forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', }),
            'e_time':  forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', }),
            'rows_description': forms.NumberInput(
                attrs={'class': 'form-control', }),
            'show_weekend': forms.CheckboxInput(
                attrs={'class': 'form-check-input', }),
            'show_month_calendar': forms.CheckboxInput(
                attrs={'class': 'form-check-input', }),
        }
        help_texts = {
            'nickname': _('表示名として使用。日本語(漢字・ひらがな等)だと判り易いかと'),
            's_time': _('勤務開始時間のデフォルト値'),
            'e_time': _('勤務終了時間のデフォルト値'),
            'rows_description': _('3以上、15以下'),
            'show_weekend': _('スケジュール(週)に土曜日・日曜日を表示するか'),
            'show_month_calendar': _('スケジュールを月表示にするか'),
        }
