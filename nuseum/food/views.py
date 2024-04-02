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
from user_info.models import User_Card, User_Affliction, User_Incongruity, User_Allergy
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
            user_id = request.data.get('user_id')
            user_card_id = request.data.get('user_card')

            if not user_card_id:
                return JsonResponse({'message': 'user_card is required'}, status=status.HTTP_400_BAD_REQUEST)
        
            try:
                user_card_id = int(user_card_id)  # user_card_id를 정수로 변환
            except ValueError:
                return JsonResponse({'message': 'Invalid user_card_id'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # User_Card 객체를 한 번만 조회하며, 해당 사용자에게 속해 있는지 확인
                user_card = User_Card.objects.prefetch_related(
                    'user_allergy',
                    'user_incongruity',
                    'user_affliction'
                ).get(id=user_card_id, user_id_c=user)
            except User_Card.DoesNotExist:
                return JsonResponse({'message': 'Unauthorized: Card does not belong to the specified user'}, status=status.HTTP_400_BAD_REQUEST)

            user_allergy = user_card.user_allergy.all()
            user_incongruity = user_card.user_incongruity.all()
            user_afflictions = user_card.user_affliction.all()

            # 필터링된 Food_List 객체 생성
            food_list = Food_List.objects.exclude(
                nutro_name__in=Nutro_Name.objects.filter(incongruity_info__in=user_incongruity)
            ).exclude(
                nutro_name__in=Nutro_Name.objects.filter(allergy_info__in=user_allergy)
            )
            
            # 사용자에게 affliction 정보가 없다면, 모든 식품을 포함하도록 food_list를 조정합니다.
            if not user_afflictions.exists():
                accumulated_food_list = list(food_list)
            else:
                # 사용자에게 affliction이 있는 경우에는 해당 affliction에 맞는 식품을 필터링합니다.
                accumulated_food_set = []
                for affliction in user_afflictions:
                    food_list_for_affliction = food_list.filter(nutro_name__affliction_info=affliction)
                    accumulated_food_set.extend(food_list_for_affliction)
                
                # 중복을 제거하고 최종 리스트 생성
                accumulated_food_list = list(set(accumulated_food_set))

            # 카테고리별 푸드 개수와 전체 푸드 개수를 저장할 딕셔너리
            category_food_counts = {}
            total_food_count = len(accumulated_food_list)

            with transaction.atomic():
                # 기존에 저장된 사용자의 모든 푸드리스트를 제거
                User_Food_List.objects.filter(user_id_c=user_card_id).delete()

                # 카테고리별 푸드 정보를 저장할 딕셔너리 초기화
                category_food_info = {}

                for category_code, category_name in Food_Category:
                    category_food_list = [food for food in accumulated_food_list if food.food_category == category_code]
                    category_food_counts[category_code] = len(category_food_list)

                    # 해당 카테고리의 푸드 정보를 담을 리스트 초기화
                    food_info_list = []

                    for food in category_food_list:
                        # 각 푸드의 정보(이름과 ID)를 딕셔너리 형태로 추가
                        food_info = {
                            'food_id': food.id,
                            'food_name': food.food_name
                        }
                        food_info_list.append(food_info)
                    
                    # 카테고리별로 푸드 정보 저장
                    category_food_info[category_code] = {
                        'total_food_count': len(category_food_list),
                        'foods': food_info_list
                    }

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

            # 카테고리별 푸드 정보를 응답 데이터에 포함
            response_data = {
                'message': 'Success',
                'user_card_id': user_card_id,
                'category_food_info': category_food_info
            }

            # # 카테고리별 푸드 개수와 전체 푸드 개수 반환
            # response_data = {
            #     'message': 'Success',
            #     'user_card_id' : user_card_id,
            #     'total_food_count': total_food_count,
            #     'category_food_counts': category_food_counts
            # }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

MAX_RECOMMENDATIONS_PER_PRIORITY = 4

class User_Food_Recommend(APIView):
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            user_card_id = request.data.get('user_card')

            if not user_card_id:
                return JsonResponse({'message': 'user_card is required'}, status=status.HTTP_400_BAD_REQUEST)        

            try:
                user_card_id = int(user_card_id)  # user_card_id를 정수로 변환
            except ValueError:
                return JsonResponse({'message': 'Invalid user_card_id'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

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
            # 기존 Food_Effect 인스턴스 삭제
            Food_Effect.objects.all().delete()

            # Food_List 모델에서 모든 데이터 가져오기
            food_list_items = Food_List.objects.all()

            # Food_Effect를 저장할 리스트
            food_effect_instances = []

            # 각 Food_List 아이템에 대해 Food_Effect 인스턴스 생성 및 리스트에 추가
            for food_list_item in food_list_items:

               # 변수 초기화
                affliction_effects_raw = list(food_list_item.nutro_name.all().values_list('affliction_info', flat=True))
                incongruity_effects_raw = list(food_list_item.nutro_name.all().values_list('incongruity_info', flat=True))
                allergy_effects_raw = list(food_list_item.nutro_name.all().values_list('allergy_info', flat=True))  # 알러지 정보 추가

                 # 디버깅을 위한 출력
                print(f"Affliction Effects Raw: {affliction_effects_raw}")
                print(f"Incongruity Effects Raw: {incongruity_effects_raw}")
                print(f"Allergy Effects Raw: {allergy_effects_raw}")  # 알러지 정보 출력

                # 중첩된 리스트를 펼쳐서 flatten
                affliction_effects = [item for sublist in affliction_effects_raw for item in (sublist if isinstance(sublist, (list, tuple)) else [sublist]) if item is not None]
                incongruity_effects = [item for sublist in incongruity_effects_raw for item in (sublist if isinstance(sublist, (list, tuple)) else [sublist]) if item is not None]
                allergy_effects = [item for sublist in allergy_effects_raw for item in (sublist if isinstance(sublist, (list, tuple)) else [sublist]) if item is not None]  # 알러지 정보 처리
                
                food_effect_instance = Food_Effect(
                    food_name=food_list_item,
                    affliction_effect_kind=list(affliction_effects),
                    incongruity_effect_kind=list(incongruity_effects),
                    allergy_effect_kind=list(allergy_effects)  # 알러지 효과 추가
                )
                food_effect_instances.append(food_effect_instance)

            # Bulk create를 사용하여 여러 Food_Effect 인스턴스를 한 번에 저장
            Food_Effect.objects.bulk_create(food_effect_instances)

            # # ManyToMany 관계 설정
            # # 예시: User_Affliction, User_Incongruity, User_Allergy 모델 인스턴스를 얻는 방법
            # # 실제로는 affliction_effects, incongruity_effects, allergy_effects를 기반으로 적절한 모델 인스턴스를 조회해야 함
            # # 예를 들어, affliction_effects가 모델의 ID 목록이라고 가정
            # affliction_instances = User_Affliction.objects.filter(id__in=affliction_effects)
            # incongruity_instances = User_Incongruity.objects.filter(id__in=incongruity_effects)
            # allergy_instances = User_Allergy.objects.filter(id__in=allergy_effects)

            # # ManyToManyField에 인스턴스 추가
            # food_effect_instance.affliction_kind.set(affliction_instances)
            # food_effect_instance.incongruity_kind.set(incongruity_instances)
            # food_effect_instance.allergy_kind.set(allergy_instances)

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
            user_id = request.data.get('user_id')
            user_card_id = request.data.get('user_card')

            if not user_card_id:
                return JsonResponse({'message': 'user_card is required'}, status=status.HTTP_400_BAD_REQUEST)        

            try:
                user_card_id = int(user_card_id)  # user_card_id를 정수로 변환
            except ValueError:
                return JsonResponse({'message': 'Invalid user_card_id'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

            # 조회된 사용자 객체와 카드 ID를 사용하여 User_Card 객체 조회
            if not User_Card.objects.filter(id=user_card_id, user_id_c=user).exists():
                return JsonResponse({'message': 'Unauthorized: Card does not belong to the specified user'}, status=status.HTTP_403_FORBIDDEN)

            with transaction.atomic():
                # User_Food_Recommend_List에서 해당 사용자의 추천 음식 리스트 조회
                food_recommendations = User_Food_Recommend_List.objects.filter(
                    user_id_c=user_card_id
                ).prefetch_related('user_food_list')

                # User_Product_Recommend_List의 기존 추천을 삭제
                User_Product_Recommend_List.objects.filter(user_id_c=user_card_id).delete()

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
                            print("user_card_id",user_card_id)
                            User_Product_Recommend_List.objects.create(
                                user_id_c=User_Card.objects.get(id=user_card_id),
                                rec_product_category= food_category,
                                # rec_product_category=selected_product.product_category
                                rec_product_name=selected_product
                            )
            # 사용자의 카드 ID에 맞는 제품 추천 목록만 조회합니다.
            recommendations = User_Product_Recommend_List.objects.filter(user_id_c=user_card_id).select_related('rec_product_name').prefetch_related('rec_product_name__food_id')

            detail = []
            for rec in recommendations:
                product = rec.rec_product_name
                if product:
                    # 연결된 모든 식품명을 조회합니다.
                    food_names = [food.food_name for food in product.food_id.all()]  # 여기서 수정됨
                    product_detail = {
                        'id': rec.id,
                        'rec_product_category': rec.rec_product_category,
                        'user_id_c': rec.user_id_c_id,
                        'rec_product_id': product.id,
                        'rec_product_name': product.product_name,
                        'rec_product_url': product.product_url,
                        'food_names': food_names,  # 제품에 연결된 식품명 목록을 응답에 추가
                    }
                    detail.append(product_detail)
            
            return JsonResponse(
                {
                    'message': 'Success',
                    "code": "0000",
                    "detail": detail
                },
                status=status.HTTP_200_OK
            )
        
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class UserProductRecommendDetailAPIView(APIView):
    def post(self, request, product_id):
        try:
            try:
                product = Product_List.objects.get(id=product_id)
                # 제품에 연결된 식품명을 가져옵니다.
                food_names = product.food_id.all().values_list('food_name', flat=True)
            except Product_List.DoesNotExist:
                return JsonResponse(
                    {
                        'message': 'Product not found',
                        "code": "0001"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 제품 정보와 연결된 식품명을 응답 데이터로 구성합니다.
            product_detail = {
                'product_id': product.id,
                'product_name': product.product_name,
                'product_url': product.product_url,
                'product_kind': product.product_kind,
                'product_category': product.product_category,
                'market_id': product.market_id,
                'food_names': list(food_names),  # 식품명 목록을 리스트로 변환하여 추가
            }

            return JsonResponse(
                {
                    'message': 'Success',
                    "code" : "0000",
                    "detail" : product_detail
                }, 
                status=status.HTTP_200_OK
            )

        except KeyError:
            return JsonResponse({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
    # def post(self, request, product_id):
    #     try:
    #          # try 블록 내에서 Product_List 객체를 가져옵니다.
    #         try:
    #             product = Product_List.objects.get(id=product_id)
    #         except Product_List.DoesNotExist:
    #             # Product_List 객체가 존재하지 않으면 오류 메시지를 반환합니다.
    #             return Response(
    #                 {
    #                     'message': 'Product not found',
    #                     "code": "0001"  # 적절한 오류 코드를 지정합니다.
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         # 이제 해당 제품을 직렬화하여 JSON 응답으로 반환
    #         serializer = ProductListSerializer(product)

    #         return Response(
    #             {
    #                 'message': 'Success',
    #                 "code" : "0000",
    #                 "detail" : serializer.data
    #             }, 
    #             status=status.HTTP_200_OK
    #         )

    #     except KeyError:
    #         return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)    
