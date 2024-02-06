from rest_framework import serializers
from django.db import transaction
from .models import User_Record_list, Food_List, User_Card
from django.shortcuts import get_object_or_404

class FoodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food_List
        fields = ['id', 'food_name']  # 음식 목록에 포함할 필드를 정의
        
class UserRecordListSerializer(serializers.ModelSerializer):
    user_card_id = serializers.IntegerField(write_only=True)
    foods = FoodListSerializer(many=True, read_only=True)  # 여러 음식 객체를 포함하므로 many=True

    class Meta:
        model = User_Record_list
        fields = ['user_card_id', 'record_date', 'foods']

    def validate_user_card_id(self, value):
        # 사용자 카드 ID의 존재 여부를 검증합니다.
        if not User_Card.objects.filter(pk=value).exists():
            raise serializers.ValidationError("User card not found.")
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user_card_id = validated_data.pop('user_card_id')
            foods_data = validated_data.pop('foods')

            # 안전한 방식으로 User_Card 인스턴스를 조회합니다.
            try:
                user_card = User_Card.objects.get(pk=user_card_id)
            except User_Card.DoesNotExist:
                # User_Card 인스턴스가 없는 경우 ValidationError를 발생시킵니다.
                raise serializers.ValidationError({"user_card_id": "User card not found."})
            
            user_record = User_Record_list.objects.create(user_card_id_c=user_card, **validated_data)
            user_record.foods.set(foods_data)
            
        return user_record
