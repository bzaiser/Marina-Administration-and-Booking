from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Length
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
    vat_number = models.CharField(_("VAT Number / AFM"), max_length=50, blank=True, null=True)
    tax_office = models.CharField(_("Tax Office / DOY"), max_length=100, blank=True, null=True)
    passport_number = models.CharField(_("Passport Number"), max_length=50, blank=True, null=True)
    nationality = models.CharField(_("Nationality"), max_length=2, default='DE', help_text="ISO Country Code (DE, GR, US, etc.)")
    language = models.CharField(_("Preferred Language"), max_length=2, default='DE', help_text="ISO Language Code (DE, EN, etc.)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ['name']

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

    def get_flag_code(self):
        """Returns the correct ISO code for flag-icons library."""
        if not self.flag:
            return "xx"
        code = self.flag.lower().strip()
        mapping = {
            'uk': 'gb',
            'el': 'gr',
        }
        return mapping.get(code, code)

    class Meta:
        verbose_name = _("Boat")
        verbose_name_plural = _("Boats")
        ordering = ['name']

class Block(models.Model):
    TYPE_CHOICES = [
        ('WATER', 'Water Berth'),
        ('SERVICE', 'Service / Dry-Dock'),
        ('LAND', 'Land Storage'),
    ]
    name = models.CharField(max_length=50, unique=True)
    block_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='WATER')
    key = models.CharField(max_length=10, blank=True, null=True, help_text="Mapping key for SVG coordinates (e.g., 'A', 'B', 'C')")
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
        ordering = ['block', Length('number').asc(), 'number']

class PriceRate(models.Model):
    from_meters = models.DecimalField(_("From Meters"), max_digits=5, decimal_places=2, default=0.0)
    to_meters = models.DecimalField(_("To Meters"), max_digits=5, decimal_places=2, default=0.0)
    price = models.DecimalField(_("Price per Day"), max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.from_meters}m - {self.to_meters}m: €{self.price}/d"

    class Meta:
        verbose_name = _("Price Rate")
        verbose_name_plural = _("Price Rates")
        ordering = ['from_meters']

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

    @property
    def supply_total(self):
        return sum(s.total_price for s in self.supplies.all())

    def calculate_price(self):
        """Calculates the price based on boat length and the PriceRate table."""
        rate = PriceRate.objects.filter(
            from_meters__lte=self.boat.length,
            to_meters__gte=self.boat.length
        ).first()
        
        if rate:
            return float(rate.price) * self.duration_days
        return 0.0

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

class ServiceProvider(models.Model):
    name = models.CharField(_("Provider Name"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=50, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Service Provider")
        verbose_name_plural = _("Service Providers")

class ServiceCategory(models.Model):
    name = models.CharField(_("Category Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    is_for_marina = models.BooleanField(_("Available for Marina (Supplies)"), default=True)
    is_for_yard = models.BooleanField(_("Available for Yard (Work Orders)"), default=False)

    class Meta:
        verbose_name = _("Service Category")
        verbose_name_plural = _("Service Categories")

    def __str__(self):
        return self.name

class Service(models.Model):
    UNIT_CHOICES = [
        ('LITER', 'Liter'),
        ('KG', 'Kilogram'),
        ('KWH', 'kWh'),
        ('HOUR', 'Hour'),
        ('DAY', 'Day(s)'),
        ('PIECE', 'Piece / Unit'),
    ]

    name = models.CharField(_("Service Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="services", verbose_name=_("Category"))
    unit = models.CharField(_("Unit"), max_length=10, choices=UNIT_CHOICES, default='PIECE')
    price_per_unit = models.DecimalField(_("Price per Unit"), max_digits=10, decimal_places=2, default=0.0)
    tax_rate = models.DecimalField(_("Tax Rate (%)"), max_digits=5, decimal_places=2, default=19.00)
    image = models.ImageField(_("Image"), upload_to='services/', blank=True, null=True)
    color = ColorField(_("Color"), default='#3498db')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Provider / Supplier"))

    def __str__(self):
        cat_name = self.category.name if self.category else "No Category"
        return f"{self.name} ({cat_name})"

    class Meta:
        verbose_name = _("Service Catalog")
        verbose_name_plural = _("Service Catalog")

class BookingSupply(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='supplies')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.FloatField(_("Quantity / Units"), default=1.0)
    unit_price = models.DecimalField(_("Price per Unit"), max_digits=10, decimal_places=2, blank=True, null=True)
    tax_rate = models.DecimalField(_("Tax Rate (%)"), max_digits=5, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(_("Date Added"), auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.unit_price and self.service_id:
            self.unit_price = self.service.price_per_unit
        if not self.tax_rate and self.service_id:
            self.tax_rate = self.service.tax_rate
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.quantity * float(self.unit_price)

    def __str__(self):
        return f"{self.quantity} {self.service.get_unit_display()} {self.service.name} for Booking #{self.booking_id}"

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    boat = models.ForeignKey('Boat', on_delete=models.CASCADE, related_name='work_orders')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='work_orders', null=True, blank=True)
    berth = models.ForeignKey('Berth', on_delete=models.SET_NULL, related_name='work_orders', null=True, blank=True, help_text="Dry dock or work place")
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(_("Notes"), blank=True, null=True)
    
    # Scheduling for Planning View
    start_date = models.DateField(_("Start Date"), null=True, blank=True)
    end_date = models.DateField(_("End Date"), null=True, blank=True)
    
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    @property
    def total_value(self):
        return sum(item.total_price for item in self.items.all())

    def save(self, *args, **kwargs):
        if not self.customer and self.boat:
            self.customer = self.boat.owner
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Work Order #{self.id} - {self.boat.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Work Order")
        verbose_name_plural = _("Work Orders")

class WorkOrderItem(models.Model):
    order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.FloatField(_("Quantity / Units"), default=1.0)
    
    unit_price = models.DecimalField(_("Price per Unit (At Order)"), max_digits=10, decimal_places=2, blank=True, null=True)
    tax_rate = models.DecimalField(_("Tax Rate (%)"), max_digits=5, decimal_places=2, blank=True, null=True)
    
    notes = models.TextField(_("Notes"), blank=True, null=True)
    date_added = models.DateTimeField(_("Date Added"), auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.unit_price and self.service_id:
            self.unit_price = self.service.price_per_unit
        if not self.tax_rate and self.service_id:
            self.tax_rate = self.service.tax_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.service.name}"

    @property
    def total_price(self):
        return self.quantity * float(self.unit_price)

    class Meta:
        verbose_name = _("Work Order Item")
        verbose_name_plural = _("Work Order Items")

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
    DOCUMENT_TYPES = [
        ('RECEIPT', 'Retail Sales Receipt'),
        ('TAXFREE', 'Retail Receipt - Tax Free'),
        ('INVOICE', 'Service Invoice (B2B)'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="invoices")
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='OPEN')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD, blank=True, null=True)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, default='RECEIPT')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # myDATA (Greece) Fields
    mydata_mark = models.CharField(max_length=100, null=True, blank=True)
    mydata_uid = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.customer.name}"

    def recalculate_total(self):
        item_total = sum(item.subtotal for item in self.items.all())
        self.total_amount = float(item_total) - float(self.discount)
        self.save()

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    quantity = models.FloatField(default=1.0)
    unit = models.CharField(max_length=10, choices=Service.UNIT_CHOICES, default='PIECE')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return float(self.quantity) * float(self.unit_price)

    def __str__(self):
        return f"{self.description} ({self.quantity} {self.get_unit_display()})"
