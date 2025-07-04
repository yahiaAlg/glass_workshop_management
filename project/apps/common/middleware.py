from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class WorkerAccessMiddleware(MiddlewareMixin):
    """
    Middleware to restrict worker access to specific apps only.
    Workers can only access: invoices, orders, inventory, customers
    """
    
    def process_request(self, request):
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None
        
        # Admin users have full access
        if request.user.is_admin():
            return None
            
        # Check if user is a worker
        if request.user.is_worker():
            current_path = request.path
            
            # Allowed URL patterns for workers
            allowed_patterns = [
                '/invoices/',
                '/orders/',
                '/inventory/',
                '/customers/',
                '/dashboard/',
                '/auth/logout/',
                # '/admin/',  # Add if needed
            ]
            
            # Check if current path starts with any allowed pattern
            is_allowed = (
                current_path == '/' or  # Root redirect
                any(current_path.startswith(pattern) for pattern in allowed_patterns)
            )
            
            if not is_allowed:
                messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
                return redirect('customers:list')
        
        return None