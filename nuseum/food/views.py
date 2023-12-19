import jwt, json
import os, hmac, time, base64, requests

from django.contrib.auth import authenticate, get_user_model

# choices.py 파일에서 Food_Category 가져오기
from .choices import Food_Category
from .serializers import UserFoodListSerializer, UserFoodPurchaseSerializer, UserProductRecListSerializer, ProductListSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User_Food_List, Food_List, User_Food_Recommend_List, UserFoodPurchase, Product_List, User_Product_Recommend_List
from user_info.models import User_Card, User_Affliction, User_Incongruity
from account.models import User

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction  # 트랜잭션 처리를 위한 import 추가

def get_user_pk_by_userid(userid):
    User = get_user_model()
    try:
        user = User.objects.get(user_id=userid)
        return user.pk
    except User.DoesNotExist:
        return None

# 사용자 푸드 리스트 생성 API
class User_Recommend_FoodList(APIView):
    def post(self, request):
        try:
            # userid = request.data.get('user_id')
            user_card_id = request.data.get('user_card')            

            user_incongruity = User_Card.objects.get(id=user_card_id).user_incongruity.all()
            user_afflictions = User_Card.objects.get(id=user_card_id).user_affliction.all()

            food_list = Food_List.objects.exclude(incongruity_info__in=user_incongruity)
            accumulated_food_list = []

            for affliction in user_afflictions:
                food_list_for_affliction = food_list.filter(affliction_info=affliction)
                accumulated_food_list.extend(food_list_for_affliction)

            # 중복을 제거하고 리스트로 변환
            accumulated_food_list = list(set(accumulated_food_list))

            with transaction.atomic():
                for category_code, category_name in Food_Category:
                    category_food_list = [food for food in accumulated_food_list if food.food_category == category_code]

                    if category_food_list:
                        # 기존에 추천된 푸드를 가져옴
                        existing_user_food_list = User_Food_List.objects.filter(user_id_c=user_card_id, food_category=category_code).first()
                        
                        if not existing_user_food_list:
                            user_food_list = User_Food_List.objects.create(
                                user_id_c=User_Card.objects.get(id=user_card_id),
                                food_category=category_code
                            )                                                        
                            user_food_list.user_food_list.clear()
                            print(category_food_list )
                            user_food_list.user_food_list.set(category_food_list)
                            print("New user_food_list created")
                        else:
                            
                            user_food_list = existing_user_food_list                            
                            user_food_list.user_food_list.clear()
                            user_food_list.user_food_list.add(*category_food_list )
                            print(user_food_list)
                            print("Existing user_food_list updated")                            
                        
            user_food_lists = User_Food_List.objects.filter(user_id_c=user_card_id)
            
            return Response({'message': 'Success'}, status=status.HTTP_200_OK)
            
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

# 사용자 푸드 추천 API
class User_Food_Recommend(APIView):
    def post(self, request):
        try:
            user_card_id = request.data.get('user_card')
            
            user_food_lists = User_Food_List.objects.filter(user_id_c=user_card_id)

            with transaction.atomic():
                for category_code, category_name in Food_Category:
                    category_food_list = []

                    for user_food_list in user_food_lists:                       

                        if user_food_list.food_category == category_code:
                            # 사용자가 사용한 음식 중에서 user_food_use가 True인 음식 가져오기
                            used_foods = user_food_list.user_food_list.filter(userfoodpurchase__user_food_use=True)
                            #  dislike food 가져오기
                            dislike_food = user_food_list.user_food_list.filter(userfoodpurchase__user_food_dislike=True)
                            
                            # 사용한 음식을 제외한 음식 가져오기
                            available_foods = user_food_list.user_food_list.exclude(id__in=used_foods.values_list('id', flat=True)).exclude(id__in=dislike_food.values_list('id', flat=True))
                            
                            category_food_list.extend(available_foods)
                        
                     # 기존에 추천된 푸드를 가져오기
                    existing_user_recommend_list = User_Food_Recommend_List.objects.filter(
                        user_id_c=user_card_id, 
                        user_recommend_food_category=category_code
                    ).first()

                    if not existing_user_recommend_list:
                        user_recommend_foods = User_Food_Recommend_List.objects.create(
                            user_id_c=User_Card.objects.get(id=user_card_id),
                            user_recommend_food_category=category_code,
                        )
                        print(user_recommend_foods)
                    
                    else:
                        user_recommend_foods = existing_user_recommend_list
                                        
                    if category_food_list:
                        user_recommend_foods.user_food_list.set(category_food_list)
                    else:
                        print(f"No food available for category {category_code}")                    

            result = User_Food_Recommend_List.objects.all()

            return Response(
                {
                    'message': 'Success',
                    "code" : "0000",
                    "detail" : result.values()
                }, status=status.HTTP_200_OK
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

# food use set, food like set, food like count increase API        
class Food_Use_Set(APIView):    
    def post(self, request):
        try:
            user_card_id = request.data.get('user_card')
            food_id = request.data.get('food_id')

            # 사용자의 특정 푸드에 대한 UserFoodPurchase 객체 생성 또는 업데이트
            user_food_purchase, created = UserFoodPurchase.objects.get_or_create(
                user_food_list__user_id_c=user_card_id,
                food_id=food_id,
            )

            # 사용자가 해당 푸드를 사용함으로 표시 (user_food_use를 True로 설정)
            user_food_purchase.user_food_use = True
            user_food_purchase.user_food_like = True
            user_food_purchase.user_food_like_cnt += 1 
            user_food_purchase.save()

            return Response(
                {
                    'message': 'Success'
                }, status=status.HTTP_200_OK
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class User_Recommend_ProductList(APIView):
    def post(self, request):
        try:
            # user_id = request.data.get('user_id')
            user_card_id = request.data.get('user_card')   

            # User_Food_Recommend_List에서 해당 사용자의 추천 음식 카테고리 및 음식 리스트 조회
            recommendations = User_Food_Recommend_List.objects.filter(
                user_id_c=user_card_id
            ).values_list('user_recommend_food_category', 'user_food_list__id')

            print(recommendations)

            for category, food_id in recommendations:
                # Product_List에서 해당 음식이 있는 제품을 찾음
                products_with_food = Product_List.objects.filter(
                    food_id=food_id
                )

                # 찾은 제품을 User_Product_Recommend_List에 저장
                for product in products_with_food:
                    User_Product_Recommend_List.objects.create(
                        user_id_c=User_Card.objects.get(id=user_card_id),
                        rec_product_category = product.product_category,
                        rec_product_name=product
                    )
            
            result = User_Product_Recommend_List.objects.all()
            serializer = UserProductRecListSerializer(result, many=True)  # 직렬화 클래스 사용
            
            return Response(
                {
                    'message': 'Success',
                    "code" : "0000",
                    "detail" : serializer.data
                }, 
                status=status.HTTP_200_OK
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class UserProductRecommendDetailAPIView(APIView):
    def post(self, request, product_id):
        try:
             # get 메서드를 사용하여 단일 객체를 가져옵니다.
            product = Product_List.objects.get(id=product_id)            

            # 이제 해당 제품을 직렬화하여 JSON 응답으로 반환
            serializer = ProductListSerializer(product)

            return Response(
                {
                    'message': 'Success',
                    "code" : "0000",
                    "detail" : serializer.data
                }, 
                status=status.HTTP_200_OK
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)    
        

# # 상위 2개의 food_priority 값을 가진 푸드를 찾음
#                     top_foods = user_food_list.user_food_list.order_by('food_priority')[:2]

#                     # User_Food_Recommend_List에 저장
#                     for top_food in top_foods:
#                         # 여기서 추가: user_food_use 체크 부분
#                         user_food_use = not top_food.userfoodpurchase_set.filter(user_food_use=True).exists()
#                         User_Food_Recommend_List.objects.create(
#                             user_id_c=User_Card.objects.get(id=user_card_id),
#                             user_recommend_food_category=user_food_list.food_category,
#                             user_food_list=top_food                            
#                         )

# class User_Recommend_FoodList(APIView):
#     def post(self, request):
#         try:
#             # userid = request.data.get('user_id')
#             user_card_id = request.data.get('user_card')            

#             user_incongruity = User_Card.objects.get(id=user_card_id).user_incongruity.all()
#             user_afflictions = User_Card.objects.get(id=user_card_id).user_affliction.all()

#             food_list = Food_List.objects.exclude(incongruity_info__in=user_incongruity)
#             accumulated_food_list = []

#             for affliction in user_afflictions:
#                 food_list_for_affliction = food_list.filter(affliction_info=affliction)
#                 accumulated_food_list.extend(food_list_for_affliction)

#             # 중복을 제거하고 리스트로 변환
#             accumulated_food_list = list(set(accumulated_food_list))

#             with transaction.atomic():
#                 for category_code, category_name in Food_Category:
#                     category_food_list = [food for food in accumulated_food_list if food.food_category == category_code]

#                     if category_food_list:
#                         # 기존에 추천된 푸드를 가져옴
#                         existing_user_food_list = User_Food_List.objects.filter(user_id_c=user_card_id, food_category=category_code).first()
                        
#                         if not existing_user_food_list:
#                             user_food_list = User_Food_List.objects.create(
#                                 user_id_c=User_Card.objects.get(id=user_card_id),
#                                 food_category=category_code
#                             )                            
#                             # filtered_category_food_list = [
#                             #     food for food in category_food_list 
#                             #     if not food.userfoodpurchase_set.filter(user_food_use=True).exists()
#                             # ]
#                             user_food_list.user_food_list.clear()
#                             print(category_food_list )
#                             user_food_list.user_food_list.set(category_food_list)
#                             print("New user_food_list created")
#                         else:
                            
#                             user_food_list = existing_user_food_list
#                             # 여기서 수정: 제외할 푸드 및 user_food_use가 True인 푸드를 제외하고 추가
#                             # filtered_category_food_list = [
#                             #     food for food in category_food_list
#                             #     if not food.userfoodpurchase_set.filter(user_food_use=True).exists()
#                             # ]
#                             user_food_list.user_food_list.clear()
#                             user_food_list.user_food_list.add(*category_food_list )
#                             print(user_food_list)
#                             print("Existing user_food_list updated")                            

#                         # # 상위 2개의 food_priority 값을 가진 푸드를 찾음
#                         # top_foods = user_food_list.user_food_list.order_by('food_priority')[:2]

#                         # # User_Food_Recommend_List에 저장
#                         # for top_food in top_foods:
#                         #     User_Food_Recommend_List.objects.create(
#                         #         user_id_c=User_Card.objects.get(id=user_card_id),
#                         #         user_recommend_food_category=category_code,
#                         #         user_food_list=top_food
#                         #     )
                        
#             user_food_lists = User_Food_List.objects.filter(user_id_c=user_card_id)
#             # serializer = UserFoodListSerializer(user_food_lists, many=True)
            
#             return Response({'message': 'Success'}, status=status.HTTP_200_OK)
#             # return Response({'message': 'Success', 'user_food_lists': serializer.data}, status=status.HTTP_200_OK)
            
#         except KeyError:
#             return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)