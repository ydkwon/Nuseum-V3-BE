from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'hp', 'user_email','date_joined', 
                    'recipe_recommend', 'agree_UserInfo', 'agree_Marketing')
admin.site.register(User, UserAdmin)

# Register your models here.
