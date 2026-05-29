import os
import contextvars
from django.conf import settings
from django.db import connections

# Thread/Coroutine-safe storage of the active tenant (subdomain slug)
_active_tenant = contextvars.ContextVar('active_tenant', default=None)

def get_active_tenant():
    return _active_tenant.get()

def set_active_tenant(tenant_slug):
    _active_tenant.set(tenant_slug)

def register_tenant_db(tenant_slug):
    """
    Registers a dynamic SQLite connection in Django's ConnectionHandler
    if it hasn't been initialized already.
    """
    db_alias = f"tenant_{tenant_slug}"
    if db_alias not in connections.databases:
        # Get directory path of the default registry DB
        default_db_path = settings.DATABASES['default']['NAME']
        db_dir = os.path.dirname(default_db_path)
        
        # Build path for this tenant's SQLite file
        tenant_db_path = os.path.join(db_dir, f"db_tenant_{tenant_slug}.sqlite3")
        
        # Duplicate the default connection settings and update the file path
        db_config = settings.DATABASES['default'].copy()
        db_config['NAME'] = tenant_db_path
        
        connections.databases[db_alias] = db_config
        
    return db_alias

class TenantRouter:
    """
    A Django database router that seamlessly directs reading and writing operations
    to the active tenant's SQLite file, while keeping the Tenant registry in the global DB.
    """
    def db_for_read(self, model, **hints):
        if model.__name__ == 'Tenant':
            return 'default'
        active_tenant = get_active_tenant()
        if active_tenant:
            return register_tenant_db(active_tenant)
        return 'default'

    def db_for_write(self, model, **hints):
        if model.__name__ == 'Tenant':
            return 'default'
        active_tenant = get_active_tenant()
        if active_tenant:
            return register_tenant_db(active_tenant)
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Relations are allowed only within the same database
        db1 = getattr(obj1, '_state', None) and obj1._state.db
        db2 = getattr(obj2, '_state', None) and obj2._state.db
        if db1 and db2:
            return db1 == db2
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # migrations are allowed on all databases
        return True
