from .choices import *
from django.conf import settings
from django.db import models

class User_Affliction(models.Model):
    affliction = models.CharField(max_length=200, default='None', verbose_name='긍정')
    affliction_id = models.CharField(max_length=10, verbose_name = '긍정항목 id', default='None')
    affliction_detail = models.CharField(max_length=1000, verbose_name='긍정 상세',default='None') 

    def __str__(self):
        return str(self.affliction)

    class Meta:
        db_table = "USERAFFLICTION_TB"
        verbose_name = "긍정"
        verbose_name_plural = "긍정"  
        managed = True     

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Incongruity(models.Model):
    incongruity = models.CharField(max_length=100, verbose_name="부정", default='None')
    incongruity_id = models.CharField(max_length=10, verbose_name = '부정항목 id', default='None')
    incongruity_detail = models.CharField(max_length=1000, verbose_name='부정 상세',default='None') 

    def __str__(self):
        return str(self.incongruity)

    class Meta:
        db_table = "USERINCONGRUITY_TB"
        verbose_name = "부정"
        verbose_name_plural = "부정"       
        managed = True     

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Allergy(models.Model):
    allergy = models.CharField(max_length=100, verbose_name="알러지", default='None')
    allergy_id = models.CharField(max_length=10, verbose_name = '알러지 id', default='None')
    allergy_detail = models.CharField(max_length=1000, verbose_name='알러지 상세',default='None') 

    def __str__(self):
        return str(self.allergy)

    class Meta:
        db_table = "USERALLERGY_TB"
        verbose_name = "알러지"
        verbose_name_plural = "알러지"       
        managed = True     

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User_Card(models.Model):
    user_id_c = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name='아이디')
    
    card_nickname = models.CharField(max_length=10, verbose_name="카드 닉네임", null=True)
    card_id = models.CharField(max_length=10, verbose_name = '카드 id', default='None')
    user_birthday = models.CharField(max_length=10, verbose_name="사용자 생년월일", null=True)
    user_gender = models.CharField(choices=USER_GENDER, max_length=10, verbose_name="사용자 성별", null=True)

    user_height = models.CharField(max_length=3, verbose_name="사용자 신장", null=True)
    user_weight = models.CharField(max_length=3, verbose_name="사용자 몸무게", null=True)

    user_allergy = models.ManyToManyField(User_Allergy, blank=True, verbose_name='사용자 알러지')
    user_incongruity = models.ManyToManyField(User_Incongruity, blank=True, verbose_name='사용자 부적합')
    user_affliction = models.ManyToManyField(User_Affliction, blank=True, verbose_name='사용자 고민')

    def __str__(self):
        allergys = ', '.join([str(allergy) for allergy in self.user_allergy.all()])
        incongruity = ', '.join([str(incongruity)for incongruity in self.user_incongruity.all()])
        afflictions = ', '.join([str(affliction) for affliction in self.user_affliction.all()])
        return f'{self.card_nickname} (Allergy: {allergys}, Incongruity: {incongruity}, Afflictions: {afflictions})'
    
    class Meta:
        db_table = "USERCARD_TB"
        verbose_name = "사용자 카드"
        verbose_name_plural = "사용자 카드"       
        managed = True     

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete_card(self):
        self.delete()