from .choices import *
from django.conf import settings
from django.db import models

class User_Affliction(models.Model):
    affliction = models.CharField(max_length=200, default='None', verbose_name='고민')
    affliction_detail = models.CharField(max_length=200, verbose_name='고민상세',default='None') 

    def __str__(self):
        return str(self.affliction)

    class Meta:
        db_table = "USERAFFLICTION_TB"
        verbose_name = "사용자 고민"
        verbose_name_plural = "사용자 고민"  
        managed = False     

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Allergy(models.Model):
    allergy = models.CharField(max_length=100, verbose_name="알러지", default='None')

    def __str__(self):
        return str(self.allergy)

    class Meta:
        db_table = "USERALLERGY_TB"
        verbose_name = "알러지"
        verbose_name_plural = "알러지"       

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Card(models.Model):
    user_id_c = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='아이디')
    
    card_nickname = models.CharField(max_length=10, verbose_name="카드 닉네임", null=True)
    user_birthday = models.CharField(max_length=10, verbose_name="사용자 생년월일", null=True)
    user_gender = models.CharField(choices=USER_GENDER, max_length=10, verbose_name="사용자 성별", null=True)

    user_height = models.CharField(max_length=3, verbose_name="사용자 신장", null=True)
    user_weight = models.CharField(max_length=3, verbose_name="사용자 몸무게", null=True)

    user_allergy = models.ManyToManyField(User_Allergy, blank=True, verbose_name='사용자 알러지')
    user_affliction = models.ManyToManyField(User_Affliction, blank=True, verbose_name='사용자 고민')

    def __str__(self):
        allergies = ', '.join([str(allergy) for allergy in self.user_allergy.all()])
        afflictions = ', '.join([str(affliction) for affliction in self.user_affliction.all()])
        return f'{self.card_nickname} (Allergies: {allergies}, Afflictions: {afflictions})'
    
    class Meta:
        db_table = "USERCARD_TB"
        verbose_name = "사용자 카드"
        verbose_name_plural = "사용자 카드"       

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()