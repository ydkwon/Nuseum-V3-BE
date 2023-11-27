from django.contrib import admin
from .models import User_Card, User_Affliction, User_Incongruity

class UserInfoAdmin(admin.ModelAdmin):
    list_display = (
        'user_id_c',
        'card_nickname',
        'user_birthday',
        'user_gender',
        'user_height',
        'user_weight',
        'display_incongruity',
        'display_afflictions',
        )
    def display_incongruity(self, obj):
        return ', '.join([str(allergy) for allergy in obj.user_incongruity.all()])
    display_incongruity.short_description = '부적절'  # 필드 이름
    
    def display_afflictions(self, obj):
        return ', '.join([str(affliction) for affliction in obj.user_affliction.all()])
    display_afflictions.short_description = '고민'  # 필드 이름

    search_fields = ('user_id_c','card_nickname','user_birthday','user_gender','user_height',
        'user_weight', 'display_incongruity', 'display_afflictions')

class UserAfflictionAdmin(UserInfoAdmin):
    list_display = (
        'affliction',
        'affliction_detail',
    )
    search_fields = ('affliction', 'afflictioafflictionn_type',)

class UserIncongruityAdmin(UserInfoAdmin):
    list_display = (
        'incongruity',        
    )
    search_fields = ('incongruity',)

admin.site.register(User_Affliction, UserAfflictionAdmin)
admin.site.register(User_Incongruity, UserIncongruityAdmin)
admin.site.register(User_Card, UserInfoAdmin)
