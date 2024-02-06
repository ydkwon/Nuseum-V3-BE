# from collections.abc import Iterable
from django.conf import settings
from django.db import models
from user_info.models import User_Affliction, User_Incongruity, User_Card, User_Allergy
from food.models import Food_List
from django.utils import timezone

class User_Record_list(models.Model):
    user_card_id_c = models.ForeignKey(User_Card, on_delete=models.SET_NULL, null=True, verbose_name='사용자')
    record_date = models.DateField(blank=True, null=True, default=timezone.now)
    foods = models.ManyToManyField(Food_List, blank=True, verbose_name='푸드명')  # 다대다 관계 설정

    def __str__(self):
        return f'{self.user_card_id_c} - {", ".join(food.food_name for food in self.foods.all())}'
    
    class Meta:
        db_table = "USERRECORD_TB"
        verbose_name = "사용자기록"
        verbose_name_plural = "사용자기록" 
        managed = True 
