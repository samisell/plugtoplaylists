from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """
    Decorator to ensure only admin users (staff or superusers) can access the view
    """
    def check_admin(user):
        return user.is_authenticated and (user.is_staff or user.is_superuser)
    
    decorated_view = user_passes_test(check_admin, login_url='admin_dashboard:login')(view_func)
    
    def wrapper(request, *args, **kwargs):
        if not check_admin(request.user):
            messages.error(request, "You don't have permission to access the admin dashboard.")
            return redirect('admin_dashboard:login')
        return decorated_view(request, *args, **kwargs)
    
    return wrapper