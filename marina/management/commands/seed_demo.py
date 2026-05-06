from django.core.management.base import BaseCommand
from marina.models import Customer, Boat, Berth, Booking, PriceRate, Service, Invoice, InvoiceItem
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds demo data for the Marina'

    def handle(self, *args, **options):
        # 1. Price Rate
        PriceRate.objects.get_or_create(
            price_per_meter_day=2.50,
            effective_from=timezone.now().date() - timedelta(days=365)
        )

        # 2. Customers & Boats
        customers_data = [
            ("John Doe", "USA", 15.5, 30.0),
            ("Hansi Müller", "GER", 12.0, 18.0),
            ("Sven Svensson", "SWE", 14.2, 22.0),
            ("Dimitris Papadopoulos", "GRE", 10.5, 12.0),
            ("Alice Smith", "AUS", 18.0, 45.0),
        ]

        customers = []
        for name, flag, length, weight in customers_data:
            c, _ = Customer.objects.get_or_create(name=name, email=f"{name.lower().replace(' ', '.')}@example.com")
            b, _ = Boat.objects.get_or_create(name=f"S/Y {name.split()[1]}", owner=c, defaults={
                'flag': flag,
                'length': length,
                'weight': weight
            })
            customers.append((c, b))

        # 3. Services
        services = ["Water Supply", "Electricity 16A", "WiFi Premium", "Waste Disposal"]
        for s_name in services:
            Service.objects.get_or_create(name=s_name, defaults={'price': random.choice([5.0, 10.0, 15.0])})

        # 4. Bookings
        berths = list(Berth.objects.all())
        today = timezone.now().date()

        # Active Long-term
        for i in range(3):
            customer, boat = customers[i]
            berth = berths.pop(0)
            Booking.objects.get_or_create(
                boat=boat,
                berth=berth,
                start_date=today - timedelta(days=30),
                end_date=today + timedelta(days=330),
                defaults={
                    'booking_type': 'LONG',
                    'status': 'ACTIVE',
                    'is_at_sea': (i == 1) # Hansi is at sea
                }
            )

        # Short-term / Transient
        for i in range(3, 5):
            customer, boat = customers[i]
            berth = berths.pop(random.randint(0, 10))
            Booking.objects.get_or_create(
                boat=boat,
                berth=berth,
                start_date=today - timedelta(days=2),
                end_date=today + timedelta(days=5),
                defaults={
                    'booking_type': 'SHORT',
                    'status': 'ACTIVE',
                }
            )

        # 5. Booking Services (Add some demo usage)
        from marina.models import BookingService
        active_bookings_objs = Booking.objects.filter(status='ACTIVE')
        all_services = list(Service.objects.all())
        for b in active_bookings_objs:
            if all_services:
                BookingService.objects.create(
                    booking=b,
                    service=random.choice(all_services),
                    quantity=random.uniform(1, 10)
                )

        # 6. Invoices
        for c, b in customers:
            inv = Invoice.objects.create(customer=c, status='PAID', total_amount=150.00, payment_method='CARD')
            InvoiceItem.objects.create(invoice=inv, description="Berth Fee", quantity=1, unit_price=100.00)
            InvoiceItem.objects.create(invoice=inv, description="Electricity", quantity=5, unit_price=10.00)

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data.'))
