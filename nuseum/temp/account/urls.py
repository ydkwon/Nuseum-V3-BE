from . import views

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'account'

urlpatterns = [
    path("test_view/", views.test_view),

    path("register/", views.RegisterAPIView.as_view()), # post - 회원가입
    path("auth/", views.AuthAPIView.as_view()), # post - 로그인, delete - 로그아웃, get - 유저정보
    path("auth/refresh/", TokenRefreshView.as_view()), # jwt 토큰 재발급
    path('api/v1/id-validation', views.IdValidation.as_view(), name='id_validataion'), # id validation
    path('api/v1/hp-validation', views.HPValidation.as_view(), name='hp_validation'), # hp validation
    path('api/v1/auth-message', views.AuthView.as_view(), name='auth_message'), # hp 인증번호 전송 및 저장
    path('api/v1/auth-check', views.Check_auth.as_view(), name='auth_check'), # hp 인증번호 check
]