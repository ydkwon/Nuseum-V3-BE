import jwt, random, json

import os
import hmac
import time
import base64
import datetime
import hashlib
import requests
from .serializers import *


from .models import User, AuthSMS
from . import models as m
from django.conf import settings

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from nuseum.settings import SECRET_KEY

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

### 소셜 로그인 사용 위한 url 변수 설정 ###
BASE_URL = '/'
KAKAO_CALLBACK_URI = BASE_URL + 'kakao/callback/'
NAVER_CALLBACK_URI = BASE_URL + 'naver/callback/'

def test_view(request):
    return render(request, 'account/test.html')

class AuthAPIView(APIView):
    # 유저 정보 확인
    def get(self, request):
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            access = request.COOKIES['access']
            payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('user_id')
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            data = {'refresh': request.COOKIES.get('refresh', None)}
            serializer = TokenRefreshSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access', None)
                refresh = serializer.data.get('refresh', None)
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                user = get_object_or_404(User, pk=pk)
                serializer = UserSerializer(instance=user)
                res = Response(serializer.data, status=status.HTTP_200_OK)
                res.set_cookie('access', access)
                res.set_cookie('refresh', refresh)
                return res
            raise jwt.exceptions.InvalidTokenError

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그인
    def post(self, request):
    	# 유저 인증 self.request, username=user_id, password=password
        user = authenticate(username=request.data.get("user_id"), password=request.data.get("password"))
        # 이미 회원가입 된 유저일 때
        if user is not None:
            serializer = UserSerializer(user)
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "code" : "0000",
                    "message": "Login success",
                    "user": serializer.data,                    
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        else:
            return Response(
                {
                    "message" : "Login Fail",
                    "code" : "1000",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    # 로그아웃
    def delete(self, request):
        # 쿠키에 저장된 토큰 삭제 => 로그아웃 처리
        response = Response({
            "code" : "0000",
            "message": "Logout success"
            }, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response

class RegisterAPIView(APIView):
    # 회원가입
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "code" : "0000",
                    "message": "register successs",
                    "user": serializer.data,                    
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            
            return res
        else:
            return Response(
                {
                    "message" : "Registration Fail",
                    "code" : "1001",
                    "detail" : serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )    

class IdValidation(APIView):
    '''
    중복 아이디가 있는지 검증하는 API
    jquery blur로 AJAX통해 제출.
    '''
    def post(self, request):
        try:
            user_id = request.data['user_id']
            try:
                user = User.objects.get(user_id=user_id)
            except Exception as e:
                user = None
            
            if user is None:
                res =  Response(
                    {
                        "code" : "0001",
                        "message": "id not exist",
                    }                    
                )
            else:
                res =  Response(
                    {
                        "code" : "0002",
                        "message": "id exist",
                    }
                )

#            context = {
#                'data' : "not exist" 
#                if user is None 
#                else "exist"
#            }
            
        except KeyError:
            return Response(
                {
                    "message" : "Bad Request",
                    "code" : "1002",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        else:
#            return JsonResponse(context)
            return res
        
class HPValidation(APIView):
    '''
    중복 휴대폰 번호가 있는지 검증하는 API
    jquery blur로 AJAX통해 제출.
    '''
    def post(self, request):
        try:
            hp = request.data['hp']
            try:
                user = User.objects.get(hp=hp)
            except Exception as e:
                user = None
            
            if user is None:
                res =  Response(
                    {
                        "code" : "0003",
                        "message": "hp not exist",
                    }                    
                )
            else:
                res =  Response(
                    {
                        "code" : "0004",
                        "message": "hp exist",
                    }
                )

#            context = {
#                'data' : "not exist" if user is None else "exist"
#            }

        except KeyError:
            return Response(
                {
                    "message" : "Bad Request",
                    "code" : "1003",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        else:
#            return JsonResponse(context)
            return res

class AuthView(APIView):
    '''
    받은 request data로 휴대폰번호를 통해 AuthSMS에 update_or_create
    인증번호 난수 생성및 저장은 모델 안에 존재.
    '''
    def post(self, request):
        try:
            p_num = request.data['hp']
                  
        except KeyError:
            return Response(
                {
                    "message" : "Bad Request",
                    "code" : "1004",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            AuthSMS.objects.update_or_create(hp=p_num)
            #return Response({'message': 'OK', 'phone#':request.data['hp'], "auth_code":auth_code})
            return Response(
                {
                    'message': 'OK', 
                    "code" : "0000",
                    'phone#':request.data['hp']
                }
            )

    #휴대폰번호를 쿼리로 인증번호가 매치되는지 찾는 함수
    #hp, auth 매개변수
    def get(self, request):
        try:    
            p_number = request.data['hp']
            a_number = request.data['auth']
                        
        except KeyError:
            return Response(
                {
                    "message" : "Bad Request",
                    "code" : "1005",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            result = AuthSMS.objects.check_auth_number(p_number, a_number)
            return Response({"message":"ok", "result":result})
        

class Check_auth(APIView):

    #휴대폰번호를 쿼리로 인증번호가 매치되는지 찾는 함수
    #hp, auth 매개변수

    def post(self, request):
        try:
            user_hp = request.data['hp']
            user_auth = request.data['auth']

            auth = AuthSMS.objects.get(hp=user_hp).auth
            c_auth = str(auth)

            if c_auth == user_auth:
                res =  Response(
                            {
                                "code" : "0000",
                                "message": "hp Auth success",
                                "user_auth" : user_auth ,
                                "auth" : auth
                            }                    
                ) 
            elif c_auth != user_auth:
                res =  Response(
                            {
                                "code" : "1005",
                                "message": "hp Auth fail",
                                "user_auth" : user_auth ,
                                "auth" : auth
                            }                    
                        )
        except KeyError:
             return Response(
                {
                    "message" : "Bad Request",
                    "code" : "1005",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return res

        return res

def send_sms(request):    
    phone_number = request        

    BASE_DIR = getattr(settings, 'BASE_DIR', None)
    file_path = "naver_cloud_sens.json" # 네이버 sens api key 파일

    with open(os.path.join(BASE_DIR,file_path), encoding='utf-8') as f:
        nc_sens_key = json.load(f)

    # Generate and store an authentication code (for later verification)
    # You can use libraries like random or secrets to generate a code
    authentication_code =  random.randint(100000, 1000000) # 난수로 6자리 문자 인증 번호 생성

    ##### 네이버 sens 서비스 이용 위한 json request 형식 #####
    timestamp = str(int(time.time() * 1000))

    url = "https://sens.apigw.ntruss.com"
    uri = "/sms/v2/services/ncp:sms:kr:306737371424:quickself/messages"
    apiUrl = url + uri

    access_key = nc_sens_key['NAVER_SENS_ACCESS_KEY']
    secret_key = bytes(nc_sens_key['NAVER_SENS_SECRET_KEY'], 'UTF-8')
    message = bytes("POST" + " " + uri + "\n" + timestamp + "\n" + access_key, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    
    body = {
        "type" : "SMS",
        "contentType" : "COMM",
        "from" : "01052802707",
        "subject" : "subject",
        "content" : "[뉴지엄] 인증 번호 [{}]를 입력해주세요.".format(authentication_code),
        "messages" : [{"to" : phone_number}]
    }
    
    body2 = json.dumps(body)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": access_key,
        "x-ncp-apigw-signature-v2": signingKey
    }

    response = requests.post(apiUrl, headers=headers, data=body2)

    if response.status_code == 202:
        return authentication_code
    else:
        return response.status_code
        
def verify_code(request):
    if request.method == 'POST':
        user_input_code = request.POST.get('code')
        stored_code = request.session.get('authentication_code')
        phone_number = request.session.get('phone_number')
        
        if user_input_code == stored_code:
            # Code matches, do something like marking the phone number as verified
            return JsonResponse({"message": "Verification successful"})
        else:
            return JsonResponse({"message": "Verification failed"}, status=400)
