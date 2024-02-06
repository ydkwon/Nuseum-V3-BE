from . import views

from django.urls import path

app_name = 'food'

urlpatterns = [
    # path("test_view/", views.test_view),

    path('api/v1/user_recommend_list/', views.User_Recommend_FoodList.as_view(), name='user_recommend'), # post - 카드별 푸드 전체 추천 리스트 
    path('api/v1/user_recommend_food/', views.User_Food_Recommend.as_view(), name='user_recommend'), # post - 카드별 푸드 및 레시피 추천 함수 
    path('api/v1/user_recommend_product/', views.User_Recommend_ProductList.as_view(), name='user_recommend_product'), # 카드별 푸드 리스트 추천 함수
    path('api/v1/user_product_recommend/<int:product_id>/', views.UserProductRecommendDetailAPIView.as_view(), name='user-product-recommend-detail'),
    path('api/v1/user_food_use_set/', views.Food_Use_Set.as_view(), name='food_use_set'), # 사용자 주문 시 해당 food 사용 체크   
    path('api/v1/food_effect/', views.Food_Effect_Set.as_view(), name='food_effect_set'), # 푸드 Effect API
]