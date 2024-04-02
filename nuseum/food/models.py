from collections.abc import Iterable
from .choices import *
from django.conf import settings
from django.db import models
from user_info.models import User_Affliction, User_Incongruity, User_Card, User_Allergy

class Nutro_Name(models.Model):
    nutro_name = models.CharField(max_length=200, verbose_name='성분내용')
    incongruity_info = models.ManyToManyField(User_Incongruity, blank=True, verbose_name='부정')
    allergy_info = models.ManyToManyField(User_Allergy, blank=True, verbose_name='알러지')
    affliction_info = models.ManyToManyField(User_Affliction, blank=True, verbose_name='긍정')
    nutro_detail = models.CharField(max_length=200, verbose_name='영양정보 상세',default='None')

    def __str__(self):
        return str(self.nutro_name)

    class Meta:
        db_table = "Nutro_Name"
        verbose_name = "영양성분"
        verbose_name_plural = "영양성분"   
        managed = True     

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Food_List(models.Model):
    food_category = models.CharField(choices=Food_Category, max_length=50, verbose_name='식품군', null=True)
    food_name = models.CharField(max_length=100, verbose_name="식약처식품명", null=True)    
    food_info = models.CharField(max_length=255, verbose_name="대표식품명", null=True)
    food_ingredient = models.CharField(choices = Food_Ingredient, max_length=5, verbose_name='재료분류', null=True)
    food_code = models.CharField(max_length=7, verbose_name="식품코드", blank=True, null=True)
    food_priority = models.CharField(max_length=5, verbose_name="분류", blank=True, null=True)
    food_nutro = models.CharField(max_length=100, verbose_name=" 식품성분내용", null=True, default='None')    
    nutro_name = models.ManyToManyField(Nutro_Name, blank=True, verbose_name='성분내용')    

    def __str__(self):
        nutro_kind = ', '.join([str(nutro_kind) for nutro_kind in self.nutro_name.all()])
        return f'{self.food_name} (Nutro_Kind:{nutro_kind})'
    
    class Meta:
        db_table = "FOODLIST_TB"
        verbose_name = "푸드리스트"
        verbose_name_plural = "푸드리스트"    
        managed = True    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()

class Food_Effect(models.Model):
    food_name = models.ForeignKey(Food_List, on_delete=models.CASCADE, related_name='food_effects', verbose_name='푸드명')
    affliction_effect_kind = models.JSONField(default=list, blank=True, null=True, verbose_name="긍정 효과 종류")
    incongruity_effect_kind = models.JSONField(default=list, blank=True, null=True, verbose_name="부정 효과 종류")
    allergy_effect_kind = models.JSONField(default=list, blank=True, null=True, verbose_name="부정 효과 종류")
    incongruity_kind = models.ManyToManyField(User_Incongruity, blank=True, verbose_name='부정효과 종류')
    allergy_kind = models.ManyToManyField(User_Allergy, blank=True, verbose_name='알러지 종류')
    affliction_kind = models.ManyToManyField(User_Affliction, blank=True, verbose_name='긍정효과 종류')
    
    def __str__(self):
        return str(self.food_name)
        # food_affliction_effect_kind = ', '.join([str(effect_kind) for effect_kind in self.affliction_effect_kind])
        # food_incongruity_effect_kind = ', '.join([str(effect_kind) for effect_kind in self.incongruity_effect_kind])
        # food_allergy_kind = ', '.join([str(effect_kind) for effect_kind in self.allergy_kind])
        # return f'{self.food_name} (Food_Effect_Kind:{food_affliction_effect_kind})'
    
    class Meta:
        db_table = "FOODEFFECT_TB"
        verbose_name = "푸드효과"
        verbose_name_plural = "푸드효과"    
        managed = True    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
class Food_Market(models.Model):
    market_name = models.CharField(max_length=100, verbose_name="마켓명", blank=True, null=True)

    def __str__(self):
        return str(self.market_name)
    
    class Meta:
        db_table = "MARKETNAME_TB"
        verbose_name = "마켓리스트"
        verbose_name_plural = "마켓리스트"
        managed = True 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Food_List(models.Model):
    user_id_c = models.ForeignKey(User_Card, on_delete=models.CASCADE, null=True, verbose_name='사용자')
    food_category = models.CharField(choices=Food_Category, max_length=50, verbose_name='식품군', null=True)
    
    user_food_list = models.ManyToManyField(Food_List, through='UserFoodPurchase', blank=True, verbose_name='사용자 푸드 리스트')
    
    def __str__(self):
        return str(self.user_id_c)
    
    class Meta:
        db_table = "USERFOOD_TB"
        verbose_name = "사용자푸드"
        verbose_name_plural = "사용자푸드" 
        managed = True 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()

class UserFoodPurchase(models.Model):
    user_food_list = models.ForeignKey(User_Food_List, on_delete=models.CASCADE, verbose_name='사용자 푸드 리스트')
    food = models.ForeignKey(Food_List, on_delete=models.CASCADE, verbose_name='푸드')
    # use flag체크 조건 : 사용자 구매 후 used 체크
    user_food_use = models.BooleanField(default=False, verbose_name='사용자 푸드 구매 여부')
    # 선호 체크 조건 : 사용자 구매 시 선호 체크
    user_food_like = models.BooleanField(default=False, verbose_name='사용자 푸드 선호')
    # 비선호 체크 조건 : 비선호 카운트가 일정 카운트에 도달 시.
    user_food_dislike = models.BooleanField(default=False, verbose_name='사용자 푸드 비선호')
    
    user_food_like_cnt = models.DecimalField(max_digits=5,decimal_places=0, null=True, blank=True, default=None, verbose_name='사용자 푸드 선호 카운트')
    user_food_dislike_cnt = models.DecimalField(max_digits=5,decimal_places=0, null=True, blank=True, default=None, verbose_name='사용자 푸드 비선호 카운트')

    class Meta:
        db_table = "USERFOODPURCHASE_TB"  # 테이블 이름 설정
        verbose_name = "사용자 푸드 구매"  # 단일 항목 표시 이름``
        verbose_name_plural = "사용자 푸드 구매 리스트"  # 복수 항목 표시 이름
        managed = True 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Food_Recommend_List(models.Model):
    user_id_c = models.ForeignKey(User_Card, on_delete=models.CASCADE, null=True, verbose_name='사용자')
    user_recommend_food_category = models.CharField(choices=Food_Category, max_length=50, verbose_name='식품군', null=True)
    user_food_list = models.ManyToManyField(Food_List, blank=True, verbose_name='사용자 추천 푸드 리스트')                                       

    class Meta:
        db_table = "USERRECFOOD_TB"
        verbose_name = "사용자추천푸드"
        verbose_name_plural = "사용자추천푸드" 
        managed = True 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()

class Product_List(models.Model):
    product_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='제품이름')
    product_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='제품주소')
    product_kind = models.CharField(choices=Product_Kind, max_length=10, default='Null', verbose_name="제품종류" )
    product_category = models.CharField(choices=Food_Category, max_length=50, verbose_name='카테고리', null=True)
    market_id = models.CharField(choices=Product_Market, max_length=20,
                                    null=True, blank=True, verbose_name='마켓명')
    food_id = models.ManyToManyField(Food_List, blank=True, verbose_name='식품명')
    food_incongruity_info = models.ManyToManyField(User_Incongruity, blank=True, verbose_name='제품 부정 성분')
    food_allergy_info = models.ManyToManyField(User_Allergy, blank=True, verbose_name='제품 알러지')

    def __str__(self):
        return str(self.product_name)
    
    class Meta:
        db_table = "PRODUCTLIST_TB"
        verbose_name = "제품리스트"
        verbose_name_plural = "제품리스트"
        managed = True 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Product_Recommend_List(models.Model):
    user_id_c = models.ForeignKey(User_Card, on_delete=models.CASCADE, null=True, verbose_name='사용자')
    rec_product_category = models.CharField(choices=Food_Category, max_length=50, verbose_name='카테고리', null=True)
    rec_product_name = models.ForeignKey(Product_List, on_delete=models.SET_NULL, 
                                       null=True, blank=True, verbose_name='사용자 추천 제품 리스트')
    # food_id = models.ForeignKey(Product_List, on_delete=models.SET_NULL,
    #                             null=True, blank=True, verbose_name='식품명')

    class Meta:
        db_table = "USERRECPRODUCT_TB"
        verbose_name = "사용자추천제품"
        verbose_name_plural = "사용자추천제품" 
        managed = True 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()