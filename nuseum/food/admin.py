from django.contrib import admin
from .models import Food_List, Nutro_Name,Food_Market, Product_List, User_Food_List, UserFoodPurchase
from user_info.models import User_Incongruity, User_Affliction

class FoodList(admin.ModelAdmin):
    list_display = (
        'food_category',
        'food_name',
        'food_info',
        'incongruity_info',
        'display_afflictions',
        'display_nutrokind',
        
    )
    def display_afflictions(self, obj):
        return ', '.join([str(affliction) for affliction in obj.affliction_info.all()])
    display_afflictions.short_description = '고민'  # 필드 이름

    def display_nutrokind(self, obj):
        return ', '.join([str(nutro_kind) for nutro_kind in obj.nutro_name.all()])
    display_nutrokind.short_description = '영양성분'  # 필드 이름
    
    search_fields = ('food_category','food_name','food_info','incongruity_info','display_afflictions','display_nutrokind')

class NutroName(admin.ModelAdmin):
    list_display = (
        'nutro_name',
    )
    search_fields = ('nutro_name',)

class MarketName(admin.ModelAdmin):
    list_display = (
        'market_name',
    )
    search_fields = ('market_name',)

class ProductList(admin.ModelAdmin):
    list_display =(
        'product_name',
        'product_url',
        'market_id',
        'display_foodid',
    )
    def display_foodid(self, obj):
        return ', '.join([str(foodid) for foodid in obj.food_id.all()])
    display_foodid.short_description = '식품명'  # 필드 이름

    search_fields = ('product_name','product_url','market_id','display_foodid')

class UserFoodPurchaseInline(admin.TabularInline):
    model = UserFoodPurchase
    extra = 1

class UserFoodList(admin.ModelAdmin):
    list_display = (
        'user_id_c',
        'food_category',
        'list_rank',
        'display_user_food_list',
        # 'display_user_food_use',  # 이 부분은 더 이상 필요하지 않습니다.
    )
    search_fields = ('user_id_c', 'food_category', 'list_rank', 'user_food_list__food_name', 'user_food_use')

    inlines = [UserFoodPurchaseInline]

    def display_user_food_list(self, obj):
        return ", ".join([str(food) for food in obj.user_food_list.all()])

    display_user_food_list.short_description = 'User Food List'



admin.site.register(Nutro_Name, NutroName)
admin.site.register(Food_Market, MarketName)
admin.site.register(Product_List, ProductList)
admin.site.register(Food_List, FoodList)
admin.site.register(User_Food_List, UserFoodList)

# class FoodList(admin.ModelAdmin):
#     list_display = (
#         'food_category',
#         'food_name',
#         'food_info',
#         'allergy_info',
#         'display_afflictions',
#         'display_nutro',        
#     )
    
#     def display_afflictions(self, obj):
#         return ', '.join([str(affliction) for affliction in obj.affliction_info.all()])
#     display_afflictions.short_description = '사용자 고민'  # 필드 이름
    
#     def display_nutro(self, obj):
#         nutro_info = [f'{content.nutro.nutro_name}: {content.contents}' for content in obj.nutro_info.all()]
#         return ', '.join(nutro_info)
#     display_nutro.short_description = '영양성분 정보'  # 필드 이름

#     search_fields = ('food_category','food_name','food_info','allergy_info','display_afflictions', 'display_nutro',)
