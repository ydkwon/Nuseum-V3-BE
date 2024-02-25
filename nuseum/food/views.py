import jwt, json
import os, hmac, time, base64, requests
import random

from django.contrib.auth import authenticate, get_user_model

# choices.py 파일에서 Food_Category 가져오기
from .choices import Food_Category, priority_rules
from .serializers import UserFoodListSerializer, UserFoodPurchaseSerializer, UserProductRecListSerializer, ProductListSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User_Food_List, Food_List, User_Food_Recommend_List, UserFoodPurchase, Product_List, User_Product_Recommend_List, Nutro_Name, Food_Effect
from user_info.models import User_Card, User_Affliction, User_Incongruity
from account.models import User
from django.db.models import Prefetch
from django.db.models import Q

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction  # 트랜잭션 처리를 위한 import 추가
from django.core.serializers.json import DjangoJSONEncoder

def get_user_pk_by_userid(userid):
    User = get_user_model()
    try:
        user = User.objects.get(user_id=userid)
        return user.pk
    except User.DoesNotExist:
        return None
        
class User_Recommend_FoodList(APIView):
    def post(self, request):
        try:
            user_card_id = request.data.get('user_card')

            # User_Card 객체를 한 번만 조회
            user_card = User_Card.objects.prefetch_related(
                Prefetch('user_allergy'),
                Prefetch('user_incongruity'),
                Prefetch('user_affliction')
            ).get(id=user_card_id)

            user_allergy = user_card.user_allergy.all()
            user_incongruity = user_card.user_incongruity.all()
            user_afflictions = user_card.user_affliction.all()

            # 필터링된 Food_List 객체 생성
            food_list = Food_List.objects.exclude(
                nutro_name__in=Nutro_Name.objects.filter(incongruity_info__in=user_incongruity)
            ).exclude(
                nutro_name__in=Nutro_Name.objects.filter(allergy_info__in=user_allergy)
            )

            # 식품 리스트 관리를 위한 리스트 사용
            accumulated_food_set = []

            for affliction in user_afflictions:
                food_list_for_affliction = food_list.filter(nutro_name__affliction_info=affliction)
                # 중복 없이 추가하기 위해 extend 사용
                # 이전에 accumulated_food_set이 리스트이므로, extend 메서드를 사용
                accumulated_food_set.extend(food_list_for_affliction)

            # 중복을 제거하고 최종 리스트 생성
            # 리스트에서 중복 제거를 위해 set으로 변환 후 다시 list로 변환
            accumulated_food_list = list(set(accumulated_food_set))
            
            # 카테고리별 푸드 개수와 전체 푸드 개수를 저장할 딕셔너리
            category_food_counts = {}
            total_food_count = len(accumulated_food_list)

            with transaction.atomic():

                for category_code, category_name in Food_Category:
                    category_food_list = [food for food in accumulated_food_list if food.food_category == category_code]
                    category_food_counts[category_code] = len(category_food_list)

                    if category_food_list:
                        existing_user_food_list = User_Food_List.objects.filter(
                            user_id_c=user_card_id, 
                            food_category=category_code
                        ).first()
                        
                        if not existing_user_food_list:
                            user_food_list = User_Food_List.objects.create(
                                user_id_c=user_card,
                                food_category=category_code
                            )                                                        
                            user_food_list.user_food_list.set(category_food_list)
                        else:
                            existing_user_food_list.user_food_list.clear()
                            existing_user_food_list.user_food_list.add(*category_food_list)

            # 카테고리별 푸드 개수와 전체 푸드 개수 반환
            response_data = {
                'message': 'Success',
                'total_food_count': total_food_count,
                'category_food_counts': category_food_counts
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

# class User_Food_Recommend(APIView):
#     def post(self, request):
#         try:
#             user_card_id = request.data.get('user_card')
#             user_food_lists = User_Food_List.objects.filter(user_id_c=user_card_id)

#             with transaction.atomic():
#                  # 사용자에 대한 기존의 모든 추천을 삭제합니다.
#                 User_Food_Recommend_List.objects.filter(user_id_c=user_card_id).delete()

#                 # 각 카테고리별로 랜덤하게 식품 추천
#                 for category_code, category_name in Food_Category:
#                     # 각 카테고리별 우선순위에 따라 랜덤 선택 로직
#                     priorities = priority_rules.get(category_code, [])
#                     selected_food_id = None

#                     for priority in priorities:
#                         priority_foods = UserFoodPurchase.objects.filter(
#                             user_food_list__user_id_c=user_card_id,
#                             food__food_priority=priority,
#                             user_food_use=False  # 사용되지 않은 푸드만 고려
#                         ).values_list('food_id', flat=True).distinct()

#                         if priority_foods:
#                             selected_food_id = random.choice(priority_foods)
#                             break  # 하나만 선택

#                     if selected_food_id:
#                         # 새로운 추천 리스트를 생성하고 선택된 식품 ID를 추가합니다.
#                         recommend_list = User_Food_Recommend_List.objects.create(
#                             user_id_c=User_Card.objects.get(id=user_card_id),
#                             user_recommend_food_category=category_code,
#                         )
#                         recommend_list.user_food_list.add(selected_food_id)

#             # 최종 추천된 식품 리스트 반환
#             result = User_Food_Recommend_List.objects.filter(user_id_c=user_card_id)
#             response_data = {
#                 'message': 'Success',
#                 'detail': [{'food_name': food_item.food_name, 'nutro_kind': [nutro.nutro_name for nutro in food_item.nutro_name.all()]} for food_list in result for food_item in food_list.user_food_list.all()]
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except KeyError:
#             return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

MAX_RECOMMENDATIONS_PER_PRIORITY = 4

class User_Food_Recommend(APIView):
    def post(self, request):
        try:
            user_card_id = request.data.get('user_card')
            # user_food_lists = User_Food_List.objects.filter(user_id_c=user_card_id)

            with transaction.atomic():
                # 사용자에 대한 기존의 모든 추천을 삭제합니다.
                User_Food_Recommend_List.objects.filter(user_id_c=user_card_id).delete()

                # 각 카테고리별로 랜덤하게 식품 추천
                for category_code, category_name in Food_Category:
                    print("category_code", category_code)
                    # 각 우선순위별로 추천할 식품 목록을 담을 리스트를 초기화합니다.
                    recommended_food_ids = []

                    # 각 카테고리별 우선순위에 따라 가능한 모든 식품을 찾습니다.
                    for priority in priority_rules.get(category_code, []):
                        priority_food_ids = UserFoodPurchase.objects.filter(
                            user_food_list__user_id_c=user_card_id,
                            user_food_list__food_category=category_code,
                            food__food_priority=priority,
                            user_food_use=False
                        ).values_list('food_id', flat=True).distinct()

                        # 가능한 식품이 있고 추천 목록에 아직 추가하지 않았다면 추천 목록에 추가합니다.
                        if priority_food_ids and len(recommended_food_ids) < MAX_RECOMMENDATIONS_PER_PRIORITY:
                            recommended_food_ids.append(random.choice(priority_food_ids))

                    # 추천 목록에 있는 식품을 최종 추천 리스트에 추가합니다.
                    if recommended_food_ids:
                        recommend_list = User_Food_Recommend_List.objects.create(
                            user_id_c=User_Card.objects.get(id=user_card_id),
                            user_recommend_food_category=category_code,
                        )
                        for food_id in recommended_food_ids:
                            recommend_list.user_food_list.add(food_id)

            # 최종 추천된 식품 리스트 반환
            result = User_Food_Recommend_List.objects.filter(user_id_c=user_card_id)
            response_data = {
                'message': 'Success',
                'details': [
                    {
                        'food_id': food_item.id,
                        'food_category': food_item.food_category,
                        'food_priority': food_item.food_priority,
                        'food_name': food_item.food_name,
                        'nutro_names': [
                            {
                                'name': nutro.nutro_name,
                                'incongruity': [incongruity.incongruity for incongruity in nutro.incongruity_info.all()],
                                'allergy': [allergy.allergy for allergy in nutro.allergy_info.all()],
                                'affliction': [affliction.affliction for affliction in nutro.affliction_info.all()],
                                'detail': nutro.nutro_detail
                            } for nutro in food_item.nutro_name.all()
                        ]
                    } 
                    for food_list in result
                    for food_item in food_list.user_food_list.all()
                ]
                # 'detail': [
                #     {
                #         'food_id' : food_item.id,
                #         'food_category' : food_item.food_category,
                #         'food_priority' : food_item.food_priority,
                #         'food_name': food_item.food_name, 
                #         'nutro_kind': [nutro.nutro_name for nutro in food_item.nutro_name.all()]
                #     } 
                #     for food_list in result 
                #     for food_item in food_list.user_food_list.all()
                # ]
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
        
# affliction number id 가져오기 위한 함수
def get_user_affliction_by_number(number):
    try:
        return User_Affliction.objects.get(id=number)
    except User_Affliction.DoesNotExist:
        return None

# 푸드 Effect 생성 API
class Food_Effect_Set(APIView):

    def post(self, request):
        try:
            # Food_List 모델에서 모든 데이터 가져오기
            food_list_items = Food_List.objects.all()

            # Food_Effect를 저장할 리스트
            food_effect_instances = []

            # 각 Food_List 아이템에 대해 Food_Effect 인스턴스 생성 및 리스트에 추가
            for food_list_item in food_list_items:

                # 변수 초기화
                affliction_effects_raw = list(food_list_item.nutro_name.all().values_list('affliction_info', flat=True))
                incongruity_effects_raw = list(food_list_item.nutro_name.all().values_list('incongruity_info', flat=True))

                # 디버깅을 위한 출력
                print(f"Affliction Effects Raw: {affliction_effects_raw}")
                print(f"Incongruity Effects Raw: {incongruity_effects_raw}")

                # 숫자에 대응하는 User_Affliction 객체를 가져와서 리스트에 저장
                # affliction_effects = [get_user_affliction_by_number(number) for number in affliction_effects_raw if number is not None]
                
                # JSON으로 변환 가능한 형태로 데이터 변환
                # affliction_effects_data = [{'affliction': affliction.affliction, 'affliction_detail': affliction.affliction_detail} for affliction in affliction_effects if affliction is not None]
                # affliction_effects_json = json.dumps(affliction_effects_data, cls=DjangoJSONEncoder)

                # 중첩된 리스트를 펼쳐서 flatten
                affliction_effects = [item for sublist in affliction_effects_raw for item in (sublist if isinstance(sublist, (list, tuple)) else [sublist]) if item is not None]
                incongruity_effects = [item for sublist in incongruity_effects_raw for item in (sublist if isinstance(sublist, (list, tuple)) else [sublist]) if item is not None]
                
                print(f"Affliction Effects: {affliction_effects}")

                food_effect_instance = Food_Effect(
                    food_name=food_list_item,
                    affliction_effect_kind=list(affliction_effects),                    
                    incongruity_effect_kind=list(incongruity_effects)
                )
                food_effect_instances.append(food_effect_instance)

            # Bulk create를 사용하여 여러 Food_Effect 인스턴스를 한 번에 저장
            Food_Effect.objects.bulk_create(food_effect_instances)

            return Response({'message': '음식 효과가 성공적으로 생성되었습니다.'}, status=status.HTTP_201_CREATED)

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

            # user_food_like_cnt 필드가 None이면 0으로 초기화
            if user_food_purchase.user_food_like_cnt is None:
                user_food_purchase.user_food_like_cnt = 0
                
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
            user_card_id = request.data.get('user_card')   

            with transaction.atomic():
                # User_Food_Recommend_List에서 해당 사용자의 추천 음식 리스트 조회
                food_recommendations = User_Food_Recommend_List.objects.filter(
                    user_id_c=user_card_id
                ).prefetch_related('user_food_list')

                # User_Product_Recommend_List의 기존 추천을 삭제
                User_Product_Recommend_List.objects.filter(user_id_c=user_card_id).delete()

                # 각 추천된 음식에 대해 무작위로 하나의 제품을 추천
                # for food_recommendation in food_recommendations:
                #     for food in food_recommendation.user_food_list.all():
                #         # Product_List에서 해당 음식이 있는 제품을 무작위로 하나 선택
                #         product_with_food = Product_List.objects.filter(
                #             food_id=food.id
                #         ).order_by('?').first()  # 무작위로 하나의 제품만을 선택
                        
                #         # 찾은 제품을 User_Product_Recommend_List에 저장
                #         if product_with_food:
                #             User_Product_Recommend_List.objects.create(
                #                 user_id_c=User_Card.objects.get(id=user_card_id),
                #                 rec_product_category=product_with_food.product_category,
                #                 rec_product_name=product_with_food
                #             )
                
                # 각 추천된 음식에 대해 무작위로 하나의 제품을 추천
                for food_recommendation in food_recommendations:
                    food_category = food_recommendation.user_recommend_food_category  # 푸드 카테고리 정보
                    for food in food_recommendation.user_food_list.all():
                        # Product_List에서 해당 음식에 맞는 모든 제품을 리스트로 가져옴
                        products_with_food = list(Product_List.objects.filter(
                            food_id=food.id
                        ))

                        # 제품이 있으면 무작위로 하나의 제품을 선택하여 저장
                        if products_with_food:
                            selected_product = random.choice(products_with_food)
                            User_Product_Recommend_List.objects.create(
                                user_id_c=User_Card.objects.get(id=user_card_id),
                                rec_product_category= food_category,
                                # rec_product_category=selected_product.product_category
                                rec_product_name=selected_product
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
             # try 블록 내에서 Product_List 객체를 가져옵니다.
            try:
                product = Product_List.objects.get(id=product_id)
            except Product_List.DoesNotExist:
                # Product_List 객체가 존재하지 않으면 오류 메시지를 반환합니다.
                return Response(
                    {
                        'message': 'Product not found',
                        "code": "0001"  # 적절한 오류 코드를 지정합니다.
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

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
