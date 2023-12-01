from . import views

from django.urls import path

app_name = 'food'

urlpatterns = [
    # path("test_view/", views.test_view),

    path('api/v1/user_recommend/', views.User_Recommend.as_view(), name='user_recommend'), # post - 카드별 푸드 및 레시피 추천 함수 

]