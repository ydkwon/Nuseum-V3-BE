from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User_Food_List, Food_List
from user_info.models import User_Affliction
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

@csrf_exempt  # For simplicity. Consider using CSRF protection in a real project.
@require_POST
def save_food_to_user_list(request):
    try:
        # Get food_id from the request, adjust as needed
        food_id = request.POST.get('food_id')
        
        # Get the Food_List object
        food = get_object_or_404(Food_List, id=food_id)
        
        # Get the authenticated user, assuming you have user authentication in place
        user = request.user
        
        # Check if the user already has this food in their list
        existing_user_food = User_Food_List.objects.filter(user_id_c=user, user_food_list=food).exists()
        
        if not existing_user_food:
            # Create a new User_Food_List entry
            user_food = User_Food_List(user_id_c=user, user_food_list=food, user_food_use=False)
            user_food.save()
            
            return JsonResponse({'success': True, 'message': 'Food added to user list successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Food already exists in the user list'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def create_user_food_list(request, affliction_info_ids):
    try:
        # Get the User object
        user = request.user
        
        # Get the Affliction_Info objects
        affliction_infos = User_Affliction.objects.filter(id__in=affliction_info_ids)
        
        for affliction_info in affliction_infos:
            # Get the Food_List objects with matching affliction_info
            matching_foods = Food_List.objects.filter(affliction_info=affliction_info)
            
            # Check if the user already has these foods in their list
            existing_user_foods = User_Food_List.objects.filter(user_id_c=user, user_food_list__in=matching_foods).exists()
            
            if not existing_user_foods:
                # Create User_Food_List entries for each matching food
                for food in matching_foods:
                    user_food = User_Food_List(
                        user_id_c=user,
                        food_category=food.food_category,
                        user_food_list=food,
                        user_food_use=False
                    )
                    user_food.save()
                
                return JsonResponse({'success': True, 'message': 'User food list created successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'These foods already exist in the user list'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

