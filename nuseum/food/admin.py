from django.contrib import admin
from .models import Food_List, Nutro_Name, Food_Effect, Food_Market, Product_List, User_Food_List
from .models import UserFoodPurchase, User_Food_Recommend_List, User_Product_Recommend_List
from user_info.models import User_Incongruity, User_Affliction, User_Allergy

class FoodList(admin.ModelAdmin):
    list_display = (
        'food_category',
        'food_priority',
        'food_name',
        'food_info',
        'food_ingredient',        
        'display_nutrokind',        
        # 'food_code',
    )
    
    def display_nutrokind(self, obj):
        return ', '.join([str(nutro_kind) for nutro_kind in obj.nutro_name.all()])
    display_nutrokind.short_description = '성분내용'  # 필드 이름    
    
    # search_fields = ('food_category','food_name','food_info','food_priority','display_nutrokind','food_ingredient')
    search_fields = ('food_name','food_info')

class NutroName(admin.ModelAdmin):
    list_display = (
        'nutro_name',
        'display_afflictions',
        'display_incongruity',
        'display_allergy',
        'nutro_detail'
    )

    def display_afflictions(self, obj):
        return ', '.join([str(affliction) for affliction in obj.affliction_info.all()])
    display_afflictions.short_description = '긍정'  # 필드 이름

    def display_incongruity(self, obj):
        return ', '.join([str(incongruity) for incongruity in obj.incongruity_info.all()])
    display_incongruity.short_description = '부정'  # 필드 이름

    def display_allergy(self, obj):
        return ', '.join([str(allergy) for allergy in obj.allergy_info.all()])
    display_allergy.short_description = '알러지'  # 필드 이름

    search_fields = ('nutro_name','display_afflictions', 'display_incongruity', 'display_allergy','nutro_detail')

@admin.register(Food_Effect)
class FoodEffectAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'display_afflictions_kind', 'display_incongruity_kind','display_allergy_kind')

    def display_afflictions_kind(self, obj):
        return ', '.join([str(affliction) for affliction in obj.affliction_kind.all()])
    display_afflictions_kind.short_description = '긍정 효과 종류'  # 필드 이름

    def display_incongruity_kind(self, obj):
        return ', '.join([str(incongruity) for incongruity in obj.incongruity_kind.all()])
    display_incongruity_kind.short_description = '부정 효과 종류'  # 필드 이름

    def display_allergy_kind(self, obj):
        return ', '.join([str(allergy) for allergy in obj.allergy_kind.all()])
    display_allergy_kind.short_description = '알러지 종류'  # 필드 이름

    search_fields = ('food_name','display_afflictions_kind', 'display_incongruity_kind', 'display_allergy_kind')

    # def display_affliction_effect_kind(self, obj):
    #     return ', '.join(map(str, obj.affliction_effect_kind))
    # display_affliction_effect_kind.short_description = '긍정 효과 종류'

    # def display_incongruity_effect_kind(self, obj):
    #     return ', '.join(map(str, obj.incongruity_effect_kind))
    # display_incongruity_effect_kind.short_description = '부정 효과 종류'

    # search_fields = ('food_name', 'display_affliction_effect_kind', 'display_incongruity_effect_kind')

class MarketName(admin.ModelAdmin):
    list_display = (
        'market_name',
    )
    search_fields = ('market_name',)

class ProductList(admin.ModelAdmin):
    list_display =(
        'product_name',
        'product_url',
        'product_kind',
        'product_category',
        'market_id',
        'display_foodid',
    )
    def display_foodid(self, obj):
        return ', '.join([str(foodid) for foodid in obj.food_id.all()])
    display_foodid.short_description = '식품명'  # 필드 이름

    search_fields = ('product_name','product_url','product_kind','product_category','market_id','display_foodid')

class UserFoodPurchaseInline(admin.TabularInline):
    model = UserFoodPurchase
    extra = 1

class UserFoodList(admin.ModelAdmin):
    list_display = (
        'user_id_c', 'food_category', 'display_user_food_list',
    )
    search_fields = ('user_id_c', 'food_category', 'user_food_list__food_name', 'user_food_use')

    inlines = [UserFoodPurchaseInline]

    def display_user_food_list(self, obj):
        return ", ".join([str(food) for food in obj.user_food_list.all()])

    display_user_food_list.short_description = '사용자 푸드 리스트'

class UserFoodRecommendListAdmin(admin.ModelAdmin):
    list_display = ('user_id_c', 'user_recommend_food_category', 'get_user_food_list')
    list_filter = ('user_recommend_food_category', )
    search_fields = ('user_id_c__username', 'user_recommend_food_category')
    ordering = ('user_id_c', 'user_recommend_food_category')

    def get_user_food_list(self, obj):
        return ', '.join([food.food_name for food in obj.user_food_list.all()])
    get_user_food_list.short_description = '사용자 추천 푸드 리스트'

@admin.register(User_Product_Recommend_List)
class UserProductRecommendListAdmin(admin.ModelAdmin):
    list_display = ('user_id_c', 'rec_product_category', 'rec_product_name')
    search_fields = ('user_id_c__username', 'rec_product_category', 'rec_product_name__product_name')
    # list_display = ('user_id_c', 'rec_product_name', 'food_id')
    # search_fields = ('user_id_c__username', 'rec_product_name__product_name', 'food_id__product_name')

admin.site.register(Nutro_Name, NutroName)
admin.site.register(Food_Market, MarketName)
admin.site.register(Product_List, ProductList)
admin.site.register(Food_List, FoodList)
admin.site.register(User_Food_List, UserFoodList)
admin.site.register(User_Food_Recommend_List, UserFoodRecommendListAdmin)
# admin.site.register(User_Product_Recommend_List)

