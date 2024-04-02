import jwt, json
import os, hmac, time, base64, requests

from .serializers import *
from datetime import datetime, timedelta
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User_Record_list
from food.models import Food_List
from user_info.models import User_Card, User_Affliction, User_Incongruity

from collections import defaultdict
from django.db.models import Prefetch

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
            return Response(
                    {
                        "message" : "User card ID, year, and month are required",
                        "code" : "1010",
                        # "detail" : serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )
        
         # 날짜 형식을 확인하고, 유효하지 않은 경우 에러 응답을 반환합니다.
        try:
            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                    {
                        "message" : "Invalid date format. Use YYYY-MM-DD.",
                        "code" : "1010",
                        # "detail" : serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )
        
        # 사용자 ID와 기록 날짜에 해당하는 모든 기록을 조회합니다.
        user_records = User_Record_list.objects.filter(
            user_card_id_c=user_card_id, 
            record_date=record_date
        ).prefetch_related(
            Prefetch('foods', queryset=Food_List.objects.all())
        )

        if not user_records.exists():
             return Response(
                    {
                        "message" : "No records found for the given user card ID and date",
                        "code" : "1010",
                        # "detail" : serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )
        
        # 같은 날짜의 데이터를 합치기 위한 구조
        combined_details = []
        food_categories = set()
        all_nutro_kinds = set()

        for user_record in user_records:
            for food_item in user_record.foods.all():
                food_categories.add(food_item.food_category)
                nutro_kinds = [nutro.nutro_name for nutro in food_item.nutro_name.all()]
                combined_details.append({
                    'food_id': food_item.id,
                    'food_category': food_item.food_category,
                    'food_priority': food_item.food_priority,
                    'food_name': food_item.food_name,
                    'nutro_kind': nutro_kinds
                })
                all_nutro_kinds.update(nutro_kinds)

        response_data = {
            'record_date': record_date.strftime('%Y-%m-%d'),
            'food_categories': list(food_categories),
            'nutro_kinds': list(all_nutro_kinds),
            'details': combined_details,
        }

        return Response(response_data, status=status.HTTP_200_OK)

class UserRecordByMonth(APIView):
    def post(self, request):
        user_card_id = request.data.get('user_card_id')
        year = request.data.get('year')
        month = request.data.get('month')

        # 입력 값 검증
        if not user_card_id or not year or not month:
            return Response(
                    {
                        "message": "User card ID, year, and month are required",
                        "code": "1010",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime(int(year), int(month), 1)
            end_date = start_date + timedelta(days=31)  # 다음 달 첫 날을 얻기 위해 31일을 추가
            end_date = end_date.replace(day=1)  # 다음 달 첫 날
        except ValueError as e:
            return Response(
                    {
                        "message": "Invalid year or month",
                        "code": "1010",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

        # 해당 기간 동안의 기록을 검색
        user_records = User_Record_list.objects.filter(
            user_card_id_c=user_card_id,
            record_date__range=[start_date, end_date - timedelta(days=1)]  # end_date는 다음 달 첫 날이므로, 하루를 빼서 이번 달 마지막 날로 설정
        ).prefetch_related('foods')

        if not user_records.exists():
            return Response(
                    {
                        "message": "No records found for the given period",
                        "code": "1010",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )
        
        # 동일 날짜의 데이터를 합치고 중복된 데이터를 제거합니다.
        records_by_date = defaultdict(dict)
        for record in user_records:
            record_date_str = record.record_date.strftime('%Y-%m-%d')
            foods_dict = records_by_date[record_date_str]
            
            for food in record.foods.all():
                # 중복되지 않는 경우에만 추가합니다.
                if food.id not in foods_dict:
                    foods_dict[food.id] = {
                        'food_id': food.id,
                        'food_name': food.food_name,
                    }
        
        # 결과 데이터를 리스트로 변환합니다.
        combined_records = [{
            'record_date': record_date,
            'foods': list(foods.values())
        } for record_date, foods in records_by_date.items()]

        return Response(combined_records, status=status.HTTP_200_OK)

        # # 동일 날짜의 데이터를 합치기, 동시에 food_id의 중복을 제거
        # records_by_date = defaultdict(list)
        # for record in user_records:
        #     record_date_str = record.record_date.strftime('%Y-%m-%d')
        #     # 중복 검사를 위한 임시 세트
        #     unique_foods = set()
        #     for food in record.foods.all():
        #         if food.id not in unique_foods:
        #             unique_foods.add(food.id)
        #             records_by_date[record_date_str].append({
        #                 'food_id': food.id,
        #                 'food_name': food.food_name,
        #             })

        # # 결과 데이터 구성
        # combined_records = [{
        #     'record_date': record_date,
        #     'foods': foods
        # } for record_date, foods in records_by_date.items()]

        # return Response(combined_records, status=status.HTTP_200_OK)
    
# class UserRecordByMonth(APIView):
#     def post(self, request):
#         user_card_id = request.data.get('user_card_id')
#         year = request.data.get('year')
#         month = request.data.get('month')

#         if not user_card_id or not year or not month:
#             return Response(
#                     {
#                         "message" : "User card ID, year, and month are required",
#                         "code" : "1010",
#                         # "detail" : serializer.errors,
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             # 날짜 범위를 설정하여 해당 월의 시작과 끝을 파악합니다.
#             start_date = datetime(int(year), int(month), 1)
#             # 해당 월의 마지막 날짜를 계산하기 위해 다음 달의 첫 날에서 하루를 빼줍니다.
#             if int(month) == 12:  # 12월인 경우 다음 해의 첫 날로 처리
#                 end_date = datetime(int(year) + 1, 1, 1)
#             else:
#                 end_date = datetime(int(year), int(month) + 1, 1)
#         except ValueError:
#             return Response(
#                     {
#                         "message" : "Invalid year or month",
#                         "code" : "1010",
#                         # "detail" : serializer.errors,
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#             )

#         # 해당 기간 동안의 기록을 검색합니다.
#         user_records = User_Record_list.objects.filter(
#             user_card_id_c=user_card_id,
#             record_date__range=[start_date, end_date]
#         )

#         if not user_records:
#             return Response(
#                     {
#                         "message" : "No records found for the given period",
#                         "code" : "1010",
#                         # "detail" : serializer.errors,
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#             )

#         serializer = UserRecordListGetSerializer(user_records, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
class User_Day_Analysis_get(APIView):

    def post(self, request):
        user_card_id = request.data.get('user_card_id')
        record_date = request.data.get('record_date')

        if not user_card_id or not record_date:
            return Response(
                    {
                        "message": "User card ID and record date are required",
                        "code": "1010",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                    {
                        "message": "Invalid date format. Use YYYY-MM-DD.",
                        "code": "1010",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

        user_records = User_Record_list.objects.filter(user_card_id_c=user_card_id, record_date=record_date)
        if not user_records.exists():
            return Response(
                    {
                        "message": "No records found for the given user card ID and date",
                        "code": "1010",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

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
            return Response(
                    {
                        "message": "User card ID, year, and month are required",
                        "code": "1010",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 해당 월의 시작일과 마지막일을 계산합니다.
            start_date = datetime(int(year), int(month), 1)
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
        except ValueError:
            return Response(
                    {
                        "message" : "Invalid year or month",
                        "code" : "1010",
                        # "detail" : serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

        user_records = User_Record_list.objects.filter(
            user_card_id_c=user_card_id,
            record_date__range=[start_date, end_date]
        )

        if not user_records.exists():
            return Response(
                    {
                        "message" : "User Record Not Exists",
                        "code" : "1010",
                        # "detail" : serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
            )

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