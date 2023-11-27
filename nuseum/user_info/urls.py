from . import views

from django.urls import path

app_name = 'user_info'

urlpatterns = [
    # path("test_view/", views.test_view),

    path('api/v1/userinfo_save/', views.UserInfo_Post.as_view()), # post - User Information Create
    path('api/v1/userinfo_list/', views.UserInfo_Get.as_view()), # get - User Information Read
    path('api/v1/userinfo_edit/<int:card_id>/', views.UserInfo_Update.as_view(), name='User Info Edit'), # put - User Information Update
    path('api/v1/userinfo_delete/<int:card_id>/', views.UserInfo_Delete.as_view(), name='User Info Delete'), # User Infomation Delete
    path('api/v1/affliction_post', views.Affliction_Post.as_view(), name='affliction_post'), # 사용자 고민 리스트 Post    
    path('api/v1/affliction_get', views.Affliction_Get.as_view(), name='affliction_get'), # 사용자 고민 리스트 Get
    path('api/v1/incongruity_post', views.Incongruity_Post.as_view(), name='incongruity_post'), # 사용자 알러지 리스트 Post    
    path('api/v1/incongruity_get', views.Incongruity_Get.as_view(), name='incongruity_get'), # 사용자 알러지 리스트 Get
]