from django.contrib import admin
from .models import User_Card, User_Affliction, User_Allergy

class UserInfo(admin.ModelAdmin):
    list_display = (
        'user_id_c',
        'card_nickname',
        'user_birthday',
        'user_gender',
        'user_height',
        'user_weight',
        'display_allergies',
        'display_afflictions',
        )
    def display_allergies(self, obj):
        return ', '.join([str(allergy) for allergy in obj.user_allergy.all()])
    display_allergies.short_description = '알러지'  # 필드 이름
    
    def display_afflictions(self, obj):
        return ', '.join([str(affliction) for affliction in obj.user_affliction.all()])
    display_afflictions.short_description = '고민'  # 필드 이름

    search_fields = ('user_id_c','card_nickname','user_birthday','user_gender','user_height',
        'user_weight', 'user_allergy__allergy', 'user_affliction__affliction')

class UserAfflictionAdmin(UserInfo):
    list_display = (
        'affliction',
        'affliction_detail',
    )
    search_fields = ('affliction', 'afflictioafflictionn_type',)

class UserAllergyAdmin(UserInfo):
    list_display = (
        'allergy',        
    )
    search_fields = ('allergy',)

admin.site.register(User_Affliction, UserAfflictionAdmin)
admin.site.register(User_Allergy, UserAllergyAdmin)
admin.site.register(User_Card, UserInfo)
