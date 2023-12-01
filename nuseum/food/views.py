import jwt, json
import os, hmac, time, base64, requests

# from .serializers import *
# from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

# choices.py 파일에서 Food_Category 가져오기
from .choices import Food_Category

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User_Food_List, Food_List
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

class User_Recommend(APIView):

    def post(self, request):
        try:
            # 사용자 ID 및 PK 가져오기
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)

            user_card = request.data.get('user_card')            

            # 부적합한 항목 가져오기
            user_incongruity = User_Card.objects.get(id=user_card).user_incongruity.all()

            # 사용자의 고민 항목 가져오기
            user_afflictions = User_Card.objects.get(id=user_card).user_affliction.all()

            # 부적합한 항목을 제외한 푸드 리스트 가져오기
            food_list = Food_List.objects.exclude(incongruity_info__in=user_incongruity)

            # 사용자의 푸드 리스트를 담을 변수 초기화
            accumulated_food_list = []

            # 각 고민에 대한 푸드 리스트 누적
            for affliction in user_afflictions:
                # # 부적합한 항목을 제외한 푸드 리스트 가져오기
                # food_list = Food_List.objects.exclude(incongruity_info__in=user_incongruity)

                # 사용자의 고민에 맞는 푸드 리스트 필터링
                food_list = food_list.filter(affliction_info=affliction)
                print(food_list)

                # 누적된 푸드 리스트에 추가
                accumulated_food_list.extend(food_list)
            
            # 여기서 사용자 푸드 리스트 모델에 저장하는 부분 추가
            with transaction.atomic():
                # 각 고민에 대한 푸드 리스트를 저장할 빈 리스트
                user_food_lists = []

                # 각 고민에 대한 푸드 리스트 누적
                for affliction in user_afflictions:
                    # 부적합한 항목을 제외한 푸드 리스트 가져오기
                    filtered_food_list = Food_List.objects.exclude(incongruity_info__in=user_incongruity)

                    # 사용자의 고민에 맞는 푸드 리스트 필터링
                    filtered_food_list = filtered_food_list.filter(affliction_info=affliction)

                    # 누적된 푸드 리스트를 따로 저장
                    user_food_lists.append(filtered_food_list)

                # 각 카테고리별로 User_Food_List 생성 및 ManyToMany 필드에 푸드 리스트 추가
                for category_code, category_name in Food_Category:
                    # 각 고민에 대한 푸드 리스트에서 해당 카테고리의 푸드 리스트를 가져오기
                    category_food_list = [food_list.filter(food_category=category_code) for food_list in user_food_lists]

                    # 빈 리스트가 아닌 경우에만 저장
                    if any(category_food_list):
                        # 각 고민에 대한 User_Food_List 생성
                        for food_list in category_food_list:
                            if food_list.exists():
                                user_food_list = User_Food_List.objects.create(
                                    user_id_c=User_Card.objects.get(id=user_card),
                                    food_category=category_code,
                                    list_rank=1  # 순위 설정 (예시로 1 사용)
                                    
                                )
                                user_food_list.user_food_list.set(food_list)


            return Response({'message': 'Success', 'filtered_food_list': food_list}, status=status.HTTP_200_OK)
            
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

 
