from . import views

from django.urls import path

app_name = 'record'

urlpatterns = [
    path('api/v1/user_record_set/', views.User_Record_set.as_view(), name='user_record_set'), # post - Food Record Set
    path('api/v1/user_record_get/', views.User_Record_get.as_view(), name='user_record_get'), # post - Food Record Get
    path('api/v1/user_day_analysis_get/', views.User_Day_Analysis_get.as_view(), name='user_day_analysis_get'), # post - Day Analysis Get
    path('api/v1/user_month_analysis_get/', views.User_Month_Analysis_get.as_view(), name='user_month_analysis_get'), # post - Month Analysis Get
]
