from django.contrib import admin
from django.db.models.functions import Length
from .models import Customer, Boat, Berth, Booking, PriceRate, Service, Invoice, InvoiceItem, Block, BookingService, Country, ServiceProvider

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('iso_code', 'name')
    search_fields = ('iso_code', 'name')

@admin.register(BookingService)
class BookingServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'quantity', 'status', 'total_price', 'booking', 'customer', 'boat', 'date')
    list_filter = ('status', 'service', 'date')
    search_fields = ('notes', 'booking__boat__name', 'customer__name', 'boat__name')

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name',)

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'color', 'description')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')

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
    list_filter = ('booking_type', 'status', 'berth__block', 'is_at_sea')
    search_fields = ('boat__name', 'notes')
    date_hierarchy = 'start_date'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'unit', 'price_per_unit', 'tax_rate', 'provider')
    list_filter = ('service_type', 'provider', 'unit')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'status', 'total_amount')
    list_filter = ('status', 'payment_method')
    inlines = [InvoiceItemInline]
