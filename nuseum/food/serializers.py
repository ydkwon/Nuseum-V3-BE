# serializers.py

from rest_framework import serializers
from .models import User_Food_List, UserFoodPurchase, Food_List, User_Product_Recommend_List, Product_List

class FoodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food_List
        fields = '__all__'

class UserFoodPurchaseSerializer(serializers.ModelSerializer):
    food = FoodListSerializer()

    class Meta:
        model = UserFoodPurchase
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        food_instance = instance.food  # 수정된 부분
        representation['food'] = FoodListSerializer(food_instance).data
        return representation

    def to_internal_value(self, data):
        # Reverse the serialization process for the 'food' field
        food_data = data.get('food')
        if food_data:
            food_instance = Food_List.objects.get_or_create(**food_data)[0]
            data['food'] = food_instance
        return super().to_internal_value(data)



class UserFoodListSerializer(serializers.ModelSerializer):
    user_food_list = UserFoodPurchaseSerializer(many=True, read_only=True)

    class Meta:
        model = User_Food_List
        fields = ['user_id_c', 'food_category', 'user_food_list']

    def create(self, validated_data):
        user_food_purchases_data = validated_data.pop('user_food_list')
        user_food_list = User_Food_List.objects.create(**validated_data)
        for user_food_purchase_data in user_food_purchases_data:
            food_data = user_food_purchase_data.pop('food')
            food_instance, _ = Food_List.objects.get_or_create(**food_data)
            UserFoodPurchase.objects.create(user_food_list=user_food_list, food=food_instance, **user_food_purchase_data)
        return user_food_list
    
class UserProductRecListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Product_Recommend_List
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_List
        fields = '__all__'