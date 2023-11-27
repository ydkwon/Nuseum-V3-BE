import jwt, json
import os, hmac, time, base64, requests

from .serializers import *
from account.models import User
from .models import User_Card, User_Affliction, User_Incongruity

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from nuseum.settings import SECRET_KEY

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

def test_view(request):
    return render(request, 'account/test.html')


def get_user_pk_by_userid(userid):
    User = get_user_model()
    try:
        user = User.objects.get(user_id=userid)
        return user.pk
    except User.DoesNotExist:
        return None

class UserInfo_Post(APIView):
    
    # USER Card Create
    def post(self, request):
        try:            

            # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.

            if user_pk is not None:
                # 사용자 인스턴스를 가져옵니다.
                User = get_user_model()
                user_instance = User.objects.get(pk=user_pk)

                serializer = UserInfoSerializer(data=request.data)

                if serializer.is_valid():                    
                    # 사용자 인스턴스 연결
                    user_info = serializer.save(user_id_c=user_instance)

                    # user_allergy 및 user_affliction 데이터 처리
                    user_allergy_data = request.data.get('user_allergy', [])
                    user_affliction_data = request.data.get('user_affliction', [])
                    
                    # user_allergy 및 user_affliction를 user_info에 연결
                    user_info.user_allergy.set(user_allergy_data)
                    user_info.user_affliction.set(user_affliction_data)

                    return Response(
                        {
                            "user_card": UserInfoSerializer(user_info).data,
                            "code" : "0000",
                            "message": "User card save OK",
                        },
                        status=status.HTTP_200_OK,
                    )          
                
                else:
                    return Response(
                        {
                            "code" : "1012",
                            "message": "User card save NG",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )                   
            
            return Response(
                { 
                    "code" : "1013",
                    "message": "User not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )         
        
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)        
  
    # USER Card Read
    def get(self, request):    
        try:
            # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.
            print("User Card Get")
            if user_pk is not None:
                # User_Card 모델에서 해당 사용자의 모든 정보를 가져옵니다.
                user_info_list = User_Card.objects.filter(user_id_c=user_pk)

                if user_info_list:
                    # 사용자 정보를 시리얼라이즈합니다.
                    serializer = UserInfoSerializer(user_info_list, many=True)

                    return Response(
                        {
                            "user_cards": serializer.data,
                            "code" : "0000",
                            "message": "User cards read OK",
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "code" : "1014",
                            "message": "User cards read NG",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:   
                return Response(
                    {
                        "code" : "1013",
                        "message": "User not found",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
       
    # USER Card Update
    def put(self, request, card_id):
        try:
            # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.

            if user_pk is not None:
                try:
                    # 특정 카드의 정보를 가져옵니다.
                    user_card = User_Card.objects.get(user_id_c=user_pk, id=card_id)
                except User_Card.DoesNotExist:
                    return Response(
                        {
                            "code" : "1015",
                            "message": "Card not found",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 시리얼라이저를 사용하여 데이터 업데이트
                serializer = UserInfoSerializer(user_card, data=request.data)

                if serializer.is_valid():
                    user_info = serializer.save()

                    # user_allergy 및 user_affliction 데이터 처리
                    user_allergy_data = request.data.get('user_allergy', [])
                    user_affliction_data = request.data.get('user_affliction', [])
                    
                    # user_allergy 및 user_affliction를 user_info에 연결
                    user_info.user_allergy.set(user_allergy_data)
                    user_info.user_affliction.set(user_affliction_data)

                    return Response(
                        {
                            "code" : "0000",
                            "message": "Card updated successfully",
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "code" : "1016",
                            "message": "Card updated fail",
                            "errors": serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {
                    "code" : "1013",
                    "message": "User not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
    
    # USER Card Delete
    def delete(self, request, card_id):
        try:
            # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.

            if user_pk is not None:
                try:
                    # 특정 카드를 가져옵니다.
                    user_info = User_Card.objects.get(user_id_c=user_pk, id=card_id)
                    print("Delete Card")
                except User_Card.DoesNotExist:
                    print("card id is not exist")
                    return Response(
                        {
                            "code" : "1015",
                            "message": "Card not found",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 카드를 삭제합니다.
                user_info.delete_card()

                return Response(
                    {
                        "code" : "0000",
                        "message": "Card deleted successfully",
                    },
                    status=status.HTTP_200_OK,  # 삭제 요청에는 일반적으로 204 No Content 상태 코드를 사용합니다.
                )

            return Response(
                {
                    "code" : "1013",
                    "message": "User not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class UserInfo_Get(APIView):
    # USER Card Read
    def post(self, request):    
        try:
            # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.
            print("User Card Get")
            if user_pk is not None:
                # User_Card 모델에서 해당 사용자의 모든 정보를 가져옵니다.
                user_info_list = User_Card.objects.filter(user_id_c=user_pk)

                if user_info_list:
                    # 사용자 정보를 시리얼라이즈합니다.
                    serializer = UserInfoSerializer(user_info_list, many=True)

                    return Response(
                        {
                            "user_cards": serializer.data,
                            "code" : "0000",
                            "message": "User cards read OK",
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "code" : "1014",
                            "message": "User cards read NG",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:   
                return Response(
                    {
                        "code" : "1013",
                        "message": "User not found",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
        
class UserInfo_Update(APIView):
     # USER Card Update
    def post(self, request, card_id):
        try:
            # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.

            if user_pk is not None:
                try:
                    # 특정 카드의 정보를 가져옵니다.
                    user_card = User_Card.objects.get(user_id_c=user_pk, id=card_id)
                except User_Card.DoesNotExist:
                    return Response(
                        {
                            "code" : "1015",
                            "message": "Card not found",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 시리얼라이저를 사용하여 데이터 업데이트
                serializer = UserInfoSerializer(user_card, data=request.data)

                if serializer.is_valid():
                    user_info = serializer.save()

                    # user_allergy 및 user_affliction 데이터 처리
                    user_allergy_data = request.data.get('user_allergy', [])
                    user_affliction_data = request.data.get('user_affliction', [])
                    
                    # user_allergy 및 user_affliction를 user_info에 연결
                    user_info.user_allergy.set(user_allergy_data)
                    user_info.user_affliction.set(user_affliction_data)

                    return Response(
                        {
                            "code" : "0000",
                            "message": "Card updated successfully",
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "code" : "1016",
                            "message": "Card updated fail",
                            "errors": serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {
                    "code" : "1013",
                    "message": "User not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class UserInfo_Delete(APIView):
    # USER Card Delete
    def post(self, request, card_id):
        try:
            # 외부 API 함수를 호출하여 userid를 User 모델의 pk로 변환합니다.
            userid = request.data.get('user_id')
            user_pk = get_user_pk_by_userid(userid)  # get_user_pk_by_userid 함수를 호출하여 사용자의 pk를 가져옵니다.

            if user_pk is not None:
                try:
                    # 특정 카드를 가져옵니다.
                    user_info = User_Card.objects.get(user_id_c=user_pk, id=card_id)
                    print("Delete Card")
                except User_Card.DoesNotExist:
                    print("card id is not exist")
                    return Response(
                        {
                            "code" : "1015",
                            "message": "Card not found",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 카드를 삭제합니다.
                user_info.delete_card()

                return Response(
                    {
                        "code" : "0000",
                        "message": "Card deleted successfully",
                    },
                    status=status.HTTP_200_OK,  # 삭제 요청에는 일반적으로 204 No Content 상태 코드를 사용합니다.
                )

            return Response(
                {
                    "code" : "1013",
                    "message": "User not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class Incongruity_Post(APIView):
    '''
    사용자의 부적합항목을 추가하는 API
    '''
    def post(self, request):
        try:
            serializer = USerIncongruitySerializer(data=request.data)
            incongruity = request.data['incongruity']
            
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if serializer.is_valid():
                incongruity = serializer.save()
                
                return Response(
                    {
                        "code" : "0000",
                        "message": "User Allergy Save OK"
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message" : "User Allergy Save Fail",
                        "code" : "1010",
                        "detail" : serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                ) 

   
class Incongruity_Get(APIView):
    '''
    사용자의 알러지 리스트를 가져오는 API
    '''    
    def post(self,request):
        try:
            result = User_Incongruity.objects.all()
            return Response(
                {
                    "message" : "User Allergy List Get Success",
                    "code" : "0000",
                    "detail" : result.values()
                },
                status=status.HTTP_200_OK,
            )

        except KeyError:
            return Response(
                    {
                        "message" : "User Allergy List Get Fail",
                        "code" : "1011",                        
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                ) 

class Affliction_Post(APIView):
    '''
    사용자의 고민 리스트를 추가하는 API
    '''
    def post(self, request):
        try:
            serializer = USerAfflictionSerializer(data=request.data)
            affliction = request.data['affliction']
            affliction_detail = request.data['affliction_detail']
        except KeyError:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if serializer.is_valid():
                user_affliction = serializer.save()
                #User_Affliction.objects.update_or_create(affliction=affliction)
                return Response(
                    {
                        "code" : "0000",
                        "message": "User Affliction Save OK"
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message" : "User Affliction Save Fail",
                        "code" : "1010",
                        "detail" : serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                ) 

class Affliction_Get(APIView):
    '''
    사용자의 고민 리스트를 가져오는 API
    '''    
    def post(self,request):
        try:
            result = User_Affliction.objects.all()
            return Response(
                {
                    "message" : "User Affliction List Get Success",
                    "code" : "0000",
                    "detail" : result.values()
                },
                status=status.HTTP_200_OK,
            )

        except KeyError:
            return Response(
                    {
                        "message" : "User Affliction List Get Fail",
                        "code" : "1011",                        
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                ) 
        

                
 
