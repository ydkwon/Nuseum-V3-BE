from .models import User_Card, User_Affliction, User_Incongruity, User_Allergy
from rest_framework import serializers


class UserIncongruitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Incongruity        
        fields = ['incongruity_id', 'incongruity', 'incongruity_detail']

class UserInfoSerializer(serializers.ModelSerializer):
    user_incongruity = UserIncongruitySerializer(many=True, read_only=True)

    class Meta:
        model = User_Card        
        fields = '__all__'
        depth = 1  # This ensures nested serialization for related fields
   
class USerAfflictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Affliction        
        fields = '__all__'

class UserAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Allergy
        fields = '__all__'