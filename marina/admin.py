from django.contrib import admin
from django.db.models.functions import Length
from .models import Customer, Boat, Berth, Booking, PriceRate, Service, ServiceCategory, Invoice, InvoiceItem, Block, WorkOrder, WorkOrderItem, Country, ServiceProvider, BookingSupply, TenantConfig, UserMenuPreference, Tenant

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('iso_code', 'name')
    search_fields = ('iso_code', 'name')

@admin.register(BookingSupply)
class BookingSupplyAdmin(admin.ModelAdmin):
    list_display = ('booking', 'service', 'quantity', 'date')
    list_filter = ('date', 'service')

class WorkOrderItemInline(admin.TabularInline):
    model = WorkOrderItem
    extra = 1

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'boat', 'customer', 'status', 'start_date', 'end_date')
    list_display_links = ('id', 'boat', 'customer')
    list_filter = ('status', 'start_date')
    search_fields = ('boat__name', 'customer__name')
    inlines = [WorkOrderItemInline]

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name',)

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'color', 'description')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'vat_number', 'passport_number')
    search_fields = ('name', 'email', 'vat_number', 'passport_number')

@admin.register(Boat)
class BoatAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'flag', 'length', 'weight')
    list_filter = ('flag',)
    search_fields = ('name', 'owner__name')

@admin.register(Berth)
class BerthAdmin(admin.ModelAdmin):
    list_display = ('block', 'number', 'max_length', 'max_weight')
    list_filter = ('block',)
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    ordering = ('block', Length('number').asc(), 'number')

@admin.register(PriceRate)
class PriceRateAdmin(admin.ModelAdmin):
    list_display = ('from_meters', 'to_meters', 'price')

class BookingSubLeaseInline(admin.TabularInline):
    model = Booking
    fk_name = 'berth'
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('boat', 'berth', 'start_date', 'end_date', 'booking_type', 'status', 'is_at_sea')
    list_display_links = ('boat', 'berth')
    list_filter = ('booking_type', 'status', 'berth__block', 'is_at_sea')
    search_fields = ('boat__name', 'notes')
    date_hierarchy = 'start_date'

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_for_marina', 'is_for_yard')
    list_filter = ('is_for_marina', 'is_for_yard')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'price_per_unit', 'tax_rate', 'provider')
    list_filter = ('category', 'provider', 'unit')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'document_type', 'date', 'status', 'total_amount')
    list_display_links = ('id', 'customer')
    list_filter = ('status', 'document_type', 'payment_method')
    inlines = [InvoiceItemInline]


@admin.register(TenantConfig)
class TenantConfigAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone', 'vat_number')
    search_fields = ('company_name', 'email')


@admin.register(UserMenuPreference)
class UserMenuPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'show_dashboard', 'allow_dashboard', 'show_calendar', 'allow_calendar', 'allow_admin')
    list_filter = ('allow_admin', 'show_dashboard', 'allow_dashboard')
    search_fields = ('user__username', 'user__email')


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner_email', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'owner_email')
    list_filter = ('is_active',)
