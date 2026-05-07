from django.db import models
from django.utils.translation import gettext_lazy as _
from colorfield.fields import ColorField

class Country(models.Model):
    iso_code = models.CharField(_("ISO Code"), max_length=2, unique=True, help_text="e.g. 'de', 'gr'")
    name = models.CharField(_("Country Name"), max_length=100, help_text="e.g. 'Germany'")
    
    def __str__(self):
        return f"{self.iso_code.upper()} - {self.name}"

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ['iso_code']

class Customer(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    email = models.EmailField(_("Email"), blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    nationality = models.CharField(_("Nationality"), max_length=2, default='DE', help_text="ISO Country Code (DE, GR, US, etc.)")
    language = models.CharField(_("Preferred Language"), max_length=2, default='DE', help_text="ISO Language Code (DE, EN, etc.)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

class Boat(models.Model):
    BOAT_TYPES = [
        ('SAIL', 'Sailing Yacht'),
        ('MOTOR', 'Motorboat'),
        ('CAT', 'Catamaran'),
        ('RIB', 'RIB / Zodiac'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(_("Boat Name"), max_length=255)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="boats")
    boat_type = models.CharField(_("Type"), max_length=10, choices=BOAT_TYPES, default='SAIL')
    weight = models.FloatField(_("Weight (tons)"), help_text="Weight in metric tons")
    length = models.FloatField(_("Length (meters)"), help_text="Length in meters")
    width = models.FloatField(_("Width (meters)"), help_text="Width in meters", default=0.0)
    draft = models.FloatField(_("Draft (meters)"), help_text="Draft in meters", default=0.0)
    engine = models.CharField(_("Engine"), max_length=255, blank=True, null=True)
    flag = models.CharField(_("Flag"), max_length=3, help_text="ISO Country Code, e.g. AUS")
    color = models.CharField(_("Color"), max_length=7, default='#3498db', help_text="Hex color for timeline")
    image = models.ImageField(_("Boat Photo"), upload_to='boats/', blank=True, null=True)
    year_built = models.IntegerField(_("Year Built"), blank=True, null=True)
    last_maintenance = models.DateField(_("Last Maintenance"), blank=True, null=True)
    diesel_tank = models.IntegerField(_("Diesel Tank (L)"), default=0)
    water_tank = models.IntegerField(_("Water Tank (L)"), default=0)
    notes = models.TextField(_("Technical Notes"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.name} - {self.name} ({self.get_boat_type_display()})"

    class Meta:
        verbose_name = _("Boat")
        verbose_name_plural = _("Boats")

class Block(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = ColorField(default='#3498db')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='blocks/', blank=True, null=True)

    def __str__(self):
        return f"Block {self.name}"

class Berth(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='berths')
    number = models.CharField(_("Number"), max_length=10)
    max_length = models.FloatField(_("Max Length (m)"), default=20.0)
    max_weight = models.FloatField(_("Max Weight (t)"), default=50.0)

    def __str__(self):
        return f"{self.block.name}{self.number}"

    class Meta:
        unique_together = ('block', 'number')
        verbose_name = _("Berth")
        verbose_name_plural = _("Berths")
        ordering = ['block', 'number']

class PriceRate(models.Model):
    price_per_meter_day = models.DecimalField(_("Price per Meter/Day"), max_digits=10, decimal_places=2)
    effective_from = models.DateField(_("Effective From"))

    class Meta:
        verbose_name = _("Price Rate")
        verbose_name_plural = _("Price Rates")
        ordering = ['-effective_from']

class Booking(models.Model):
    TYPE_CHOICES = [
        ('LONG', 'Long-term (Yearly)'),
        ('SHORT', 'Short-term (Transient)'),
        ('SUB', 'Sub-lease'),
    ]
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    REFERENCE_CHOICES = [
        ('DIRECT', 'Direct'),
        ('NAVILY', 'Navily'),
        ('GOOGLE', 'Google'),
        ('OTHER', 'Other'),
    ]
    
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name="bookings")
    berth = models.ForeignKey(Berth, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField(_("Arrival Date"))
    end_date = models.DateField(_("Departure Date"))
    booking_type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default='PLANNED')
    reference = models.CharField(_("Reference"), max_length=20, choices=REFERENCE_CHOICES, default='DIRECT')
    is_at_sea = models.BooleanField(_("At Sea"), default=False, help_text="Set to true if long-term tenant is away and berth can be sub-leased")
    notes = models.TextField(_("Notes"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.boat.name} at {self.berth} ({self.start_date} to {self.end_date})"

    @property
    def duration_days(self):
        delta = self.end_date - self.start_date
        return max(delta.days, 1) # Minimum 1 day

    def calculate_price(self):
        """Calculates the price based on boat length, days and the latest PriceRate."""
        rate = PriceRate.objects.filter(effective_from__lte=self.start_date).first()
        if not rate:
            rate = PriceRate.objects.first()
        
        if rate:
            return float(rate.price_per_meter_day) * self.boat.length * self.duration_days
        return 0.0

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

class Service(models.Model):
    name = models.CharField(_("Service Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class BookingService(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1.0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} for {self.booking}"

    @property
    def total_price(self):
        return self.quantity * self.service.price

class Invoice(models.Model):
    PAYMENT_STATUS = [
        ('OPEN', 'Open'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
    ]
    PAYMENT_METHOD = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('TRANSFER', 'Bank Transfer'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="invoices")
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='OPEN')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"Invoice {self.id} - {self.customer.name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    quantity = models.FloatField(default=1.0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return float(self.unit_price) * self.quantity
