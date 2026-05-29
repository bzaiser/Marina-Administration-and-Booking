from django.shortcuts import render
from marina.router import set_active_tenant
from marina.models import Tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        
        # 1. Determine subdomain slug
        tenant_slug = self.get_subdomain(host)
        
        if tenant_slug:
            # 2. Check if the tenant exists in the registry DB
            tenant = Tenant.objects.using('default').filter(slug=tenant_slug, is_active=True).first()
            if tenant:
                # Activate the tenant database context for this thread/request
                set_active_tenant(tenant_slug)
                request.tenant = tenant
            else:
                # Tenant does not exist -> Render a premium "Tenant Not Found" page
                set_active_tenant(None)
                
                # Fetch port suffix for local development
                full_host = request.get_host()
                port_suffix = ""
                if ":" in full_host:
                    port_suffix = ":" + full_host.split(":")[1]
                
                # Main host mapping
                if host.endswith('localhost'):
                    main_host = f"localhost{port_suffix}"
                else:
                    main_host = f"marina.zaisers.myds.me{port_suffix}"
                
                home_url = f"{request.scheme}://{main_host}/"
                
                return render(request, 'marina/tenant_not_found.html', {
                    'home_url': home_url,
                    'invalid_slug': tenant_slug
                }, status=404)
        else:
            # Main / Global site (Registry default database)
            set_active_tenant(None)
            request.tenant = None

        response = self.get_response(request)
        
        # Reset active tenant after response finishes
        set_active_tenant(None)
        
        return response

    def get_subdomain(self, host):
        if host.replace('.', '').isdigit():
            return None
            
        parts = host.split('.')
        
        # Local development on localhost (e.g. ormos.localhost:8004)
        if parts[-1] == 'localhost':
            if len(parts) > 1:
                return parts[0]
            return None

        # Wildcard recognition for *.marina.zaisers.myds.me
        if host.endswith('marina.zaisers.myds.me'):
            if len(parts) > 4:
                return parts[0]
            return None

        # General fallback
        if len(parts) > 3:
            if parts[0] == 'www':
                return None
            return parts[0]
            
        return None
