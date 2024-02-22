from django.contrib import admin
from .models import User_Card, User_Affliction, User_Incongruity, User_Allergy

class UserInfoAdmin(admin.ModelAdmin):
    list_display = (
        'user_id_c',
        'card_nickname',
        'card_id',
        'user_birthday',
        'user_gender',
        'user_height',
        'user_weight',
        'display_allergy',
        'display_incongruity',
        'display_afflictions',
        )
    
    def display_allergy(self, obj):
        return ', '.join([str(allergy) for allergy in obj.user_allergy.all()])
    display_allergy.short_description = '알러지'  # 필드 이름

    def display_incongruity(self, obj):
        return ', '.join([str(incongruity) for incongruity in obj.user_incongruity.all()])
    display_incongruity.short_description = '부적절'  # 필드 이름
    
    def display_afflictions(self, obj):
        return ', '.join([str(affliction) for affliction in obj.user_affliction.all()])
    display_afflictions.short_description = '고민'  # 필드 이름

    search_fields = ('user_id_c','card_nickname','card_id','user_birthday','user_gender','user_height',
        'user_weight', 'display_allergy', 'display_incongruity', 'display_afflictions')

class UserAfflictionAdmin(UserInfoAdmin):
    list_display = (
        'affliction',
        'affliction_id',
        'affliction_detail',
    )
    search_fields = ('affliction', 'afflictioafflictionn_type', 'affliction_id')

class UserIncongruityAdmin(UserInfoAdmin):
    list_display = (
        'incongruity',
        'incongruity_id',
        'incongruity_detail',
    )
    search_fields = ('incongruity','incongruity_id', 'incongruity_detail',)

class UserAllergyAdmin(UserInfoAdmin):
    list_display = (
        'allergy',
        'allergy_id',
        'allergy_detail',
    )
    search_fields = ('allergy','allergy_detail', 'allergy_id')

admin.site.register(User_Affliction, UserAfflictionAdmin)
admin.site.register(User_Incongruity, UserIncongruityAdmin)
admin.site.register(User_Allergy, UserAllergyAdmin)
admin.site.register(User_Card, UserInfoAdmin)
