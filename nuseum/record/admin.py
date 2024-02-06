from django.contrib import admin
from .models import User_Record_list, User_Card, Food_List  # 필요한 모델을 임포트합니다.

# User_Record_list 모델을 위한 관리자 클래스를 정의합니다.
class UserRecordListAdmin(admin.ModelAdmin):
    list_display = ('user_card_id_c', 'record_date', 'list_foods')  # Admin 목록에서 보여줄 필드
    search_fields = ('user_card_id_c__name',)  # 검색 기능을 위한 필드 설정. User_Card 모델의 name 필드를 참조한다고 가정
    list_filter = ('record_date',)  # 필터 기능을 위한 필드

    def list_foods(self, obj):
        """Admin 목록 페이지에서 foods 필드를 표시하기 위한 메서드"""
        return ", ".join([food.food_name for food in obj.foods.all()])
    list_foods.short_description = 'Foods'  # Admin 페이지에서 해당 필드의 헤더명 설정

# Django admin 사이트에 User_Record_list 모델을 UserRecordListAdmin 옵션과 함께 등록
admin.site.register(User_Record_list, UserRecordListAdmin)
