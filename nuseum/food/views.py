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
from .models import User_Food_List, Food_List, User_Food_Recommend_List, UserFoodPurchase, Product_List, User_Product_Recommend_List, Nutro_Name, Food_Effect
from user_info.models import User_Card, User_Affliction, User_Incongruity
from account.models import User

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

# 사용자 푸드 리스트 생성 API
class User_Recommend_FoodList(APIView):
    def post(self, request):
        try:
            # userid = request.data.get('user_id')
            user_card_id = request.data.get('user_card')            

            user_incongruity = User_Card.objects.get(id=user_card_id).user_incongruity.all()
            user_afflictions = User_Card.objects.get(id=user_card_id).user_affliction.all()
 
            # 부정적 정보가 없는 Food_List 필터링
            # 부정적 정보가 있는 Nutro_Name을 제외하도록 필터링
            # food_list = Food_List.objects.exclude(incongruity_info__in=user_incongruity)
            food_list = Food_List.objects.exclude(nutro_name__in=Nutro_Name.objects.filter(incongruity_info__in=user_incongruity))

            # 필터링된 Food_List를 리스트에 추가
            # accumulated_food_list = []
            accumulated_food_list = [food for food in food_list]  # 수정된 부분: food 객체 자체를 누적하도록 수정

            for affliction in user_afflictions:
                print(f'Checking affliction: {affliction}')
                
                # food_list_for_affliction = food_list.filter(affliction_info=affliction)
                # 사용자의 affliction에 해당하는 Food_List 필터링
                food_list_for_affliction = food_list.filter(nutro_name__affliction_info=affliction)    
                
                print(f'Food list for affliction {affliction}:')
                
                # 확인: Food_List에 저장된 데이터를 확인
                for food_item in food_list_for_affliction:
                    print(f'Food Item: {food_item.food_name}, Nutro Kind: {[nutro.nutro_name for nutro in food_item.nutro_name.all()]}')

                print(f'Accumulated Food List before extension: {accumulated_food_list}')
                accumulated_food_list.extend(food_list_for_affliction)
                print(f'Accumulated Food List after extension: {accumulated_food_list}')

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

            # user_recommend_foods 초기화
            user_recommend_foods = None

            with transaction.atomic():

                # level 1, level2에서 각 하나씩 선택(food_priority)
                # 특정 카테고리에서는 level3도 하나 선택(food_priority)
                # 기존에 추천된 푸드를 삭제하기
                existing_user_recommend_list = User_Food_Recommend_List.objects.filter(
                    user_id_c=user_card_id
                ).delete()

                for category_code, category_name in Food_Category:
                    category_food_list = []

                    for user_food_list in user_food_lists:                       

                        if user_food_list.food_category == category_code:
                            
                            total_food_list = len(user_food_list.user_food_list.all())
                            # 결과 출력
                            print(f"user_food_list의 전체 갯수: {total_food_list}")
                            for food_list in user_food_list.user_food_list.all():
                                food_item_count = len(food_list.nutro_name.all())
                                print(f"{food_list.food_name}의 식품 갯수: {food_item_count}")

                            # 사용자가 사용한 음식 중에서 user_food_use가 True인 음식 가져오기
                            used_foods = user_food_list.user_food_list.filter(userfoodpurchase__user_food_use=True)
                            num_used_foods = len(used_foods)
                            # 결과 출력
                            print(f"사용자가 사용한 음식의 갯수: {num_used_foods}")

                            #  dislike food 가져오기
                            dislike_food = user_food_list.user_food_list.filter(userfoodpurchase__user_food_dislike=True)
                            num_dislike_food = len(dislike_food)
                            # 결과 출력
                            print(f"사용자가 싫어하는 음식의 갯수: {num_dislike_food}")
                            
                            # 사용한 음식을 제외한 음식 가져오기
                            available_foods = user_food_list.user_food_list.exclude(id__in=used_foods.values_list('id', flat=True)).exclude(id__in=dislike_food.values_list('id', flat=True))
                            
                            category_food_list.extend(available_foods)
                    
                    user_recommend_foods = User_Food_Recommend_List.objects.create(
                        user_id_c=User_Card.objects.get(id=user_card_id),
                        user_recommend_food_category=category_code,
                    )
                    print(f"food available for category {category_food_list}")
                    
                    if category_food_list and user_recommend_foods:
                        user_recommend_foods.user_food_list.set(category_food_list)
                        print(f"Food available for category {category_code}")  
                    else:
                        print(f"No food available for category {category_code}")                    

            result = User_Food_Recommend_List.objects.filter(user_id_c=user_card_id)

            # 응답할 데이터 생성
            response_data = {
                'message': 'Success',
                'code': '0000',
                'detail': [{'food_name': food_item.food_name, 'nutro_kind': [nutro.nutro_name for nutro in food_item.nutro_name.all()]} for food_list in result for food_item in food_list.user_food_list.all()]
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
        


