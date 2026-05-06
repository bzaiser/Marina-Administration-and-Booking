from django.contrib import admin
from .models import Customer, Boat, Berth, PriceRate, Booking, Service, Invoice, InvoiceItem

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
    list_display = ('block', 'number', 'color', 'max_length', 'max_weight')
    list_filter = ('block',)
    ordering = ('block', 'number')

@admin.register(PriceRate)
class PriceRateAdmin(admin.ModelAdmin):
    list_display = ('price_per_meter_day', 'effective_from')

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
    list_display = ('name', 'price')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'status', 'total_amount')
    list_filter = ('status', 'payment_method')
    inlines = [InvoiceItemInline]
