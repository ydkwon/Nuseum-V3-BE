import jwt, json
import os, hmac, time, base64, requests

from .serializers import *

from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
        if not user_card_id:
            return Response({'error': 'User card ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_records = User_Record_list.objects.filter(user_card_id_c=user_card_id)
        if not user_records.exists():
            return Response({'error': 'No records found for the given user card ID'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRecordListGetSerializer(user_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class User_Day_Analysis_get(APIView):
    def post(self, request):


class User_Month_Analysis_get(APIView):
    def post(self, request):

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

