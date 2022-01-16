# -*- coding: utf-8 -*-
from django.urls import path
from . import apps, views

app_name = apps.AppConfig.name
urlpatterns = [
    path('',
         views.HomeView.as_view(), name='home'),
    path('<int:year>/<int:month>/<int:day>/',
         views.HomeView.as_view(), name='home'),

    path('userschedules/',
         views.UserSchedulesView.as_view(), name='userschedules'),
    path('userschedules/<int:year>/<int:month>/<int:day>/',
         views.UserSchedulesView.as_view(), name='userschedules'),

    path('monthschedules/',
         views.month_schedules, name='monthschedules'),
    path('monthschedules/<int:year>/<int:month>/',
         views.month_schedules, name='monthschedules'),
    path('monthschedules/<eid>/',
         views.MonthSchedulesEID.as_view(), name='monthschedules_eid'),
    path('monthschedules/<eid>/<int:year>/<int:month>/',
         views.MonthSchedulesEID.as_view(), name='monthschedules_eid'),

    path('login/',
         views.InputAddress.as_view(), name='inputaddress'),
    path('login/done',
         views.InputedAddress.as_view(), name='inputedaddress'),
    path('auth/<token>/<eid>/',
         views.AuthTokenEmail.as_view(), name='authtokenemail'),
    path('logout/',
         views.LogoutView, name='logout'),
    path('usersetting/',
         views.UserSettingView.as_view(), name='usersetting'),
    path('usersetting/favoritegroup/',
         views.usersetting_favoritegroup, name='usersetting_favoritegroup'),
    path('workstatus/',
         views.work_status, name='workstatus'),
    path('favorite/group/member/add/',
         views.favorite_group_member_add, name='favorite_group_member_add'),
    path('favorite/group/member/del/',
         views.favorite_group_member_del, name='favorite_group_member_del'),
    path('userlog/',
         views.user_log, name='userlog'),
    path('userlog/<int:filterbits>/<int:page>/',
         views.user_log, name='userlog'),
    path('userlog/download/',
         views.user_log_download, name='userlog_download'),
]
