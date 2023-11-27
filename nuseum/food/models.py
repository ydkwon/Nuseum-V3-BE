from collections.abc import Iterable
from .choices import *
from django.conf import settings
from django.db import models
from user_info.models import User_Affliction, User_Incongruity, User_Card

class Nutro_Name(models.Model):
    nutro_name = models.CharField(max_length=200, verbose_name='영양성분')

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
    food_category = models.CharField(choices=Food_Category, max_length=10, verbose_name='카테고리', null=True)
    food_name = models.CharField(max_length=100, verbose_name="식품명", null=True)    
    food_info = models.CharField(max_length=255, verbose_name="식품정보", null=True)

    incongruity_info = models.ForeignKey(User_Incongruity, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='부적합')
    affliction_info = models.ManyToManyField(User_Affliction, blank=True, verbose_name='고민')

    nutro_name = models.ManyToManyField(Nutro_Name, blank=True, verbose_name='영양성분')
    
    def __str__(self):
        afflictions = ', '.join([str(affliction) for affliction in self.affliction_info.all()])
        nutro_kind = ', '.join([str(nutro_kind) for nutro_kind in self.nutro_name.all()])
        return f'{self.food_name} (Afflictions: {afflictions}, Nutro_Kind:{nutro_kind})'
    
    class Meta:
        db_table = "FOODLIST_TB"
        verbose_name = "푸드리스트"
        verbose_name_plural = "푸드리스트"    
        managed = True    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()

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

    user_id_c = models.ForeignKey(User_Card, on_delete=models.SET_NULL, null=True, verbose_name='사용자')
    food_category = models.CharField(choices=Food_Category, max_length=10, verbose_name='카테고리', null=True)
    
    list_rank = models.DecimalField(max_digits=5, decimal_places=0, null=True, 
                                    blank=True, verbose_name='푸드리스트 순위', help_text='사용자 카드의 고민에 따른 푸드의 전체 리스트')
    
    user_food_list = models.ForeignKey(Food_List, on_delete=models.SET_NULL, 
                                       null=True, blank=True, verbose_name='사용자 푸드 리스트')
    user_food_use = models.BooleanField(default=False, verbose_name='사용자 푸드 구매 여부')

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

class User_Food_Recommend_List(models.Model):
    user_id_c = models.ForeignKey(User_Card, on_delete=models.SET_NULL, null=True, verbose_name='사용자')
    user_recommend_food_category = models.CharField(choices=Food_Category, max_length=10, verbose_name='카테고리', null=True)
    user_food_list = models.ForeignKey(Food_List, on_delete=models.SET_NULL, 
                                       null=True, blank=True, verbose_name='사용자 추천 푸드 리스트')

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
    market_id = models.ForeignKey(Food_Market, on_delete=models.SET_NULL,
                                    null=True, blank=True, verbose_name='마켓명')
    food_id = models.ManyToManyField(Food_List, blank=True, verbose_name='식품명')

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
    user_id_c = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='아이디')


    class Meta:
        db_table = "USERRECPRODUCT_TB"
        verbose_name = "사용자추천제품"
        verbose_name_plural = "사용자추천제품" 
        managed = True 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()


# class Food_List(models.Model):
#     food_category = models.CharField(choices=Food_Category, max_length=10, verbose_name='카테고리', null=True)
#     food_name = models.CharField(max_length=100, verbose_name="식품명", null=True)    
#     food_info = models.CharField(max_length=255, verbose_name="식품정보", null=True)

#     allergy_info = models.ForeignKey(User_Allergy, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='알러지포함여부')
#     affliction_info = models.ManyToManyField(User_Affliction, blank=True, verbose_name='고민해당식품여부')
#     nutro_info = models.ManyToManyField(Nutro_Name, through='NutroContent', blank=True, verbose_name='영양성분 정보')

#     def __str__(self):
#         afflictions = ', '.join([str(affliction) for affliction in self.affliction_info.all()])
#         nutro_infos = ', '.join([str(nutro) for nutro in self.nutro_info.all()])
#         return f'{self.food_name} (Afflictions: {afflictions}, Nutro_infos : {nutro_infos})'
    
#     class Meta:
#         db_table = "FOODLIST_TB"
#         verbose_name = "푸드리스트"
#         verbose_name_plural = "푸드리스트"       

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)

# class NutroContent(models.Model):
#     food = models.ForeignKey(Food_List, on_delete=models.CASCADE)
#     nutro = models.ForeignKey(Nutro_Name, on_delete=models.CASCADE)
#     contents = models.CharField(max_length=5, verbose_name='영양성분의 함량')

#     class Meta:
#         db_table = "NutroContent"
#         verbose_name = "영양성분내용"
#         verbose_name_plural = "영양성분내용"       