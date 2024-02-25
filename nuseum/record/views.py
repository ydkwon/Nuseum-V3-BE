import jwt, json
import os, hmac, time, base64, requests

from .serializers import *
from datetime import datetime
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User_Record_list
from food.models import Food_List
from user_info.models import User_Card, User_Affliction, User_Incongruity

class User_Record_set(APIView):
# USER Food Record Set

    def post(self, request):
        user_card_id = request.data.get('user_card_id')
        serializer = UserRecordListSaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class User_Record_get(APIView):
    def post(self, request):
        user_card_id = request.data.get('user_card_id')
        record_date = request.data.get('record_date')

        # 사용자 카드 ID와 기록 날짜가 필수입니다.
        if not user_card_id or not record_date:
            return Response({'error': 'User card ID and record date are required'}, status=status.HTTP_400_BAD_REQUEST)
        
         # 날짜 형식을 확인하고, 유효하지 않은 경우 에러 응답을 반환합니다.
        try:
            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        # 특정 날짜와 일치하는 기록을 검색합니다.
        user_records = User_Record_list.objects.filter(user_card_id_c=user_card_id, record_date=record_date)
        if not user_records.exists():
            return Response({'error': 'No records found for the given user card ID and date'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRecordListGetSerializer(user_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
        # if not user_card_id:
        #     return Response({'error': 'User card ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # user_records = User_Record_list.objects.filter(user_card_id_c=user_card_id)
        # if not user_records.exists():
        #     return Response({'error': 'No records found for the given user card ID'}, status=status.HTTP_404_NOT_FOUND)

        # serializer = UserRecordListGetSerializer(user_records, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)

class UserRecordByMonth(APIView):
    def post(self, request):
        user_card_id = request.data.get('user_card_id')
        year = request.data.get('year')
        month = request.data.get('month')

        if not user_card_id or not year or not month:
            return Response({'error': 'User card ID, year, and month are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 날짜 범위를 설정하여 해당 월의 시작과 끝을 파악합니다.
            start_date = datetime(int(year), int(month), 1)
            # 해당 월의 마지막 날짜를 계산하기 위해 다음 달의 첫 날에서 하루를 빼줍니다.
            if int(month) == 12:  # 12월인 경우 다음 해의 첫 날로 처리
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
        except ValueError:
            return Response({'error': 'Invalid year or month'}, status=status.HTTP_400_BAD_REQUEST)

        # 해당 기간 동안의 기록을 검색합니다.
        user_records = User_Record_list.objects.filter(
            user_card_id_c=user_card_id,
            record_date__range=[start_date, end_date]
        )

        if not user_records:
            return Response({'error': 'No records found for the given period'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRecordListGetSerializer(user_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class User_Day_Analysis_get(APIView):

    def post(self, request):
        user_card_id = request.data.get('user_card_id')
        record_date = request.data.get('record_date')

        if not user_card_id or not record_date:
            return Response({'error': 'User card ID and record date are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        user_records = User_Record_list.objects.filter(user_card_id_c=user_card_id, record_date=record_date)
        if not user_records.exists():
            return Response({'error': 'No records found for the given user card ID and date'}, status=status.HTTP_404_NOT_FOUND)

        # 분석을 위한 데이터 수집
        food_categories = set()
        details = []
        all_nutro_kinds = set()  # 모든 영양성분을 저장할 집합

        for user_record in user_records:
            for food_item in user_record.foods.all():
                food_categories.add(food_item.food_category)  # 수정된 부분
                nutro_kinds = [nutro.nutro_name for nutro in food_item.nutro_name.all()]
                details.append({
                    'food_id': food_item.id,
                    'food_category': food_item.food_category,
                    'food_priority': food_item.food_priority,
                    'food_name': food_item.food_name,
                    'nutro_kind': nutro_kinds
                })
                all_nutro_kinds.update(nutro_kinds)  # 영양성분 집합에 추가

        response_data = {
            'categories': list(food_categories),
            'all_nutro_kinds': list(all_nutro_kinds),  # 모든 영양성분을 리스트로 변환하여 추가
            'nutrition_info': details
        }

        return Response(response_data, status=status.HTTP_200_OK)

class User_Month_Analysis_get(APIView):
    def post(self, request):
        user_card_id = request.data.get('user_card_id')
        year = request.data.get('year')
        month = request.data.get('month')

        if not user_card_id or not year or not month:
            return Response({'error': 'User card ID, year, and month are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 해당 월의 시작일과 마지막일을 계산합니다.
            start_date = datetime(int(year), int(month), 1)
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
        except ValueError:
            return Response({'error': 'Invalid year or month'}, status=status.HTTP_400_BAD_REQUEST)

        user_records = User_Record_list.objects.filter(
            user_card_id_c=user_card_id,
            record_date__range=[start_date, end_date]
        )

        if not user_records.exists():
            return Response({'error': 'No records found for the given user card ID and date range'}, status=status.HTTP_404_NOT_FOUND)

        food_categories = set()
        all_nutro_kinds = set()
        details = []

        for user_record in user_records:
            for food_item in user_record.foods.all():
                food_categories.add(food_item.food_category)
                nutro_kinds = [nutro.nutro_name for nutro in food_item.nutro_name.all()]
                details.append({
                    'food_id': food_item.id,
                    'food_category': food_item.food_category,
                    'food_priority': food_item.food_priority,
                    'food_name': food_item.food_name,
                    'nutro_kind': nutro_kinds
                })
                all_nutro_kinds.update(nutro_kinds)

        response_data = {
            'categories': list(food_categories),
            'all_nutro_kinds': list(all_nutro_kinds),
            'nutrition_info': details            
        }

        return Response(response_data, status=status.HTTP_200_OK)
        
#     def post(self, request):

        #     # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
        #     userid = request.data.get('user_id')
        #     user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.

        #     if user_pk is not None:
        #         # 사용자 인스턴스를 가져옵니다.
        #         User = get_user_model()
        #         user_instance = User.objects.get(pk=user_pk)

        #         serializer = UserInfoSerializer(data=request.data)

        #         if serializer.is_valid():                    
        #             # 사용자 인스턴스 연결
        #             user_info = serializer.save(user_id_c=user_instance)

        #             # user_allergy 및 user_affliction 데이터 처리
        #             user_allergy_data = request.data.get('user_allergy', [])
        #             user_affliction_data = request.data.get('user_affliction', [])
                    
        #             # user_allergy 및 user_affliction를 user_info에 연결
        #             user_info.user_allergy.set(user_allergy_data)
        #             user_info.user_affliction.set(user_affliction_data)

        #             return Response(
        #                 {
        #                     "user_card": UserInfoSerializer(user_info).data,
        #                     "code" : "0000",
        #                     "message": "User card save OK",
        #                 },
        #                 status=status.HTTP_200_OK,
        #             )          
                
        #         else:
        #             return Response(
        #                 {
        #                     "code" : "1012",
        #                     "message": "User card save NG",
        #                 },
        #                 status=status.HTTP_400_BAD_REQUEST,
        #             )                   
            
        #     return Response(
        #         { 
        #             "code" : "1013",
        #             "message": "User not found",
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )         
        
        # except KeyError:
        #     return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

