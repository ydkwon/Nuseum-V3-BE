from .models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            user_id = validated_data['user_id'],
            password = validated_data['password'],
        )
        return user

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'password', 'user_email', 'hp', 'auth','recipe_recommend', 'agree_UserInfo','agree_Marketing']

    def create(self, validated_data):
        user = User.objects.create_user(
            user_id = validated_data['user_id'],
            password = validated_data['password'],
            user_email = validated_data['user_email'],
            hp = validated_data['hp'],
            auth = validated_data['auth'],
            recipe_recommend = validated_data['recipe_recommend'],            
            agree_UserInfo = validated_data['agree_UserInfo'],
            agree_Marketing = validated_data['agree_Marketing']
        )

        return user
    
class HpAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['hp', 'auth']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            hp = validated_data['hp'],
            auth = validated_data['auth'],
        )
        return user
    
'''
        if user.user_type == "2":
            NormalUser.objects.create(
                user = user
            )
        elif user.user_type == "3":
            Pharmacist.objects.create(
                user = user
            )
        elif user.user_type == "4":
            ParmStaff.objects.create(
                user = user
            )
'''
        