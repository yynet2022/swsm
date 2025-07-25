# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import UserSetting


class UserSettingForm(forms.ModelForm):
    class Meta:
        model = UserSetting
        fields = ('nickname',
                  's_time', 'e_time',
                  'ls_time', 'le_time',
                  'working_at',
                  'rows_description',
                  'show_weekend', 'show_month_calendar',
                  'show_favorite_users_only',
                  'wnr_subject')
        widgets = {
            'nickname': forms.TextInput(
                attrs={'class': 'form-control', }),
            'working_at':  forms.Select(attrs={'class': 'form-select', }),
            's_time':  forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', }),
            'e_time':  forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', }),
            'ls_time':  forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', }),
            'le_time':  forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', }),
            'rows_description': forms.NumberInput(
                attrs={'class': 'form-control', }),
            'show_weekend': forms.CheckboxInput(
                attrs={'class': 'form-check-input', }),
            'show_month_calendar': forms.CheckboxInput(
                attrs={'class': 'form-check-input', }),
            'show_favorite_users_only': forms.CheckboxInput(
                attrs={'class': 'form-check-input', }),
            'wnr_subject': forms.TextInput(
                attrs={'class': 'form-control', }),
        }
        help_texts = {
            'nickname': _('表示名として使用。日本語(漢字・ひらがな等)だと判り易いかと'),
            'working_at': _('出社か在宅か、どちらをデフォルトにするか'),
            's_time': _('勤務開始時刻のデフォルト値'),
            'e_time': _('勤務終了時刻のデフォルト値'),
            'ls_time': _('昼休み開始時刻'),
            'le_time': _('昼休み終了時刻'),
            'rows_description': _('3以上、15以下'),
            'show_weekend': _('スケジュール(週)に土曜日・日曜日を表示するか'),
            'show_month_calendar': _('スケジュールを月表示にするか'),
            'show_favorite_users_only': _('お気に入りユーザだけ表示'),
            'wnr_subject': _('デフォルトのままを推奨'),
        }
