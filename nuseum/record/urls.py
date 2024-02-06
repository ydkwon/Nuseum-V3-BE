from . import views

from django.urls import path

app_name = 'record'

urlpatterns = [
    path('api/v1/user_record_set/', views.User_Record_set.as_view(), name='user_record_set'), # post - Food Record Set
    path('api/v1/user_record_get/', views.User_Record_get.as_view(), name='user_record_get'), # post - Food Record Get
]
