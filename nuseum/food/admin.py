from django.contrib import admin
from .models import Food_List, Nutro_Name,Food_Market, Product_List, User_Food_List
from .models import UserFoodPurchase, User_Food_Recommend_List, User_Product_Recommend_List
from user_info.models import User_Incongruity, User_Affliction

class FoodList(admin.ModelAdmin):
    list_display = (
        'food_category',
        'food_name',
        'food_info',
        'food_code',
        'food_priority',
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
    
    search_fields = ('food_category','food_name','food_info','food_code','food_priority','incongruity_info','display_afflictions','display_nutrokind')

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
        'user_id_c', 'food_category', 'display_user_food_list',
    )
    search_fields = ('user_id_c', 'food_category', 'user_food_list__food_name', 'user_food_use')

    inlines = [UserFoodPurchaseInline]

    def display_user_food_list(self, obj):
        return ", ".join([str(food) for food in obj.user_food_list.all()])

    display_user_food_list.short_description = 'User Food List'

class UserFoodRecommendListAdmin(admin.ModelAdmin):
    list_display = ('user_id_c', 'user_recommend_food_category', 'get_user_food_list')
    list_filter = ('user_recommend_food_category', )
    search_fields = ('user_id_c__username', 'user_recommend_food_category')
    ordering = ('user_id_c', 'user_recommend_food_category')

    def get_user_food_list(self, obj):
        return ', '.join([food.food_name for food in obj.user_food_list.all()])
    get_user_food_list.short_description = 'User Food List'

@admin.register(User_Product_Recommend_List)
class UserProductRecommendListAdmin(admin.ModelAdmin):
    list_display = ('user_id_c', 'rec_product_name')
    search_fields = ('user_id_c__username', 'rec_product_name__product_name')

admin.site.register(Nutro_Name, NutroName)
admin.site.register(Food_Market, MarketName)
admin.site.register(Product_List, ProductList)
admin.site.register(Food_List, FoodList)
admin.site.register(User_Food_List, UserFoodList)
admin.site.register(User_Food_Recommend_List, UserFoodRecommendListAdmin)
# admin.site.register(User_Product_Recommend_List)

