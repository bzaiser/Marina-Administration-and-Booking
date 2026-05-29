from .models import UserMenuPreference

def menu_preferences(request):
    if request.user and request.user.is_authenticated:
        # Get or create the preferences for the user
        prefs, created = UserMenuPreference.objects.get_or_create(user=request.user)
        
        # Superusers/Admins automatically have all "allow_" permissions
        if request.user.is_superuser or request.user.is_staff:
            changed = False
            for field in [
                'allow_dashboard', 'allow_calendar', 'allow_berths', 
                'allow_customers', 'allow_bookings', 'allow_planning', 
                'allow_service', 'allow_invoices', 'allow_reports', 'allow_admin'
            ]:
                if not getattr(prefs, field):
                    setattr(prefs, field, True)
                    changed = True
            if changed:
                prefs.save()
        
        return {
            'menu_prefs': prefs
        }
    return {}
