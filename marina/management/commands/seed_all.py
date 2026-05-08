from django.core.management.base import BaseCommand
from marina.models import Customer, Boat, Berth, Block, Booking, PriceRate, Service, Invoice, InvoiceItem, Country, ServiceProvider
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds all initial data for a professional Marina startup'

    def handle(self, *args, **options):
        self.stdout.write("Starting full seed...")

        # 1. Countries
        countries = [
            ('GR', 'Greece'),
            ('DE', 'Germany'),
            ('AT', 'Austria'),
            ('CH', 'Switzerland'),
            ('IT', 'Italy'),
            ('FR', 'France'),
            ('UK', 'United Kingdom'),
            ('US', 'United States'),
            ('SE', 'Sweden'),
            ('NL', 'Netherlands'),
        ]
        for code, name in countries:
            Country.objects.get_or_create(iso_code=code, defaults={'name': name})
        self.stdout.write("- Countries seeded.")

        # 2. Blocks & Berths
        blocks_data = [
            {'name': 'A', 'color': '#3498db', 'desc': 'Main Pier - North'},
            {'name': 'B', 'color': '#2ecc71', 'desc': 'Main Pier - South'},
            {'name': 'C', 'color': '#f1c40f', 'desc': 'Outer Breakwater'},
            {'name': 'D', 'color': '#e67e22', 'desc': 'Transient Dock'},
            {'name': 'E', 'color': '#9b59b6', 'desc': 'Mega Yacht Slips'},
        ]
        
        for b_data in blocks_data:
            block, _ = Block.objects.get_or_create(
                name=b_data['name'],
                defaults={'color': b_data['color'], 'description': b_data['desc']}
            )
            for i in range(1, 16):
                Berth.objects.get_or_create(
                    block=block,
                    number=str(i),
                    defaults={
                        'max_length': 15.0 + (i % 5) * 5,
                        'max_weight': 20.0 + (i % 5) * 10
                    }
                )
        self.stdout.write("- Blocks and Berths seeded.")

        # 3. Price Rates
        rates = [
            (0, 10, 15.00),
            (10, 12, 22.50),
            (12, 15, 35.00),
            (15, 20, 55.00),
            (20, 100, 120.00),
        ]
        for start, end, price in rates:
            PriceRate.objects.get_or_create(
                from_meters=start,
                to_meters=end,
                defaults={'price': price}
            )
        self.stdout.write("- Price Rates seeded.")

        # 4. Services & Providers
        provider, _ = ServiceProvider.objects.get_or_create(
            name="Marina Port Services",
            defaults={'email': 'services@marina-samos.com', 'phone': '+30 123 456789'}
        )
        services = [
            ("Water Supply", 5.00, 'SUPPLY', 'LITER'),
            ("Electricity 16A", 12.00, 'SUPPLY', 'KWH'),
            ("WiFi Premium", 10.00, 'OTHER', 'DAY'),
            ("Laundry Service", 15.00, 'CLEANING', 'PIECE'),
        ]
        for s_name, s_price, s_type, s_unit in services:
            Service.objects.get_or_create(
                name=s_name, 
                defaults={
                    'price_per_unit': s_price, 
                    'service_type': s_type, 
                    'unit': s_unit,
                    'provider': provider
                }
            )
        self.stdout.write("- Services and Providers seeded.")

        # 5. Customers & Boats
        customers_data = [
            ("Hansi Müller", "DE", "DE", "S/Y Albatros", "SAIL", 12.5, 18.0),
            ("John Smith", "UK", "EN", "M/Y Blue Horizon", "MOTOR", 14.2, 22.0),
            ("Sven Svensson", "SE", "EN", "Cat Baltic", "CAT", 15.0, 30.0),
            ("Dimitris K.", "GR", "GR", "Aegean Wind", "SAIL", 10.8, 12.0),
            ("Marco Rossi", "IT", "IT", "Bella Vita", "MOTOR", 18.5, 45.0),
            ("Sarah Jones", "US", "EN", "Ocean Star", "SAIL", 13.0, 15.0),
            ("Pieter de Jong", "NL", "EN", "Flying Dutchman", "SAIL", 11.5, 14.0),
        ]

        today = timezone.now().date()
        berths = list(Berth.objects.all())
        
        for c_name, nat, lang, b_name, b_type, length, weight in customers_data:
            cust, _ = Customer.objects.get_or_create(
                name=c_name, 
                defaults={'email': f"{c_name.lower().replace(' ', '.')}@example.com", 'nationality': nat, 'language': lang}
            )
            boat, _ = Boat.objects.get_or_create(
                name=b_name,
                owner=cust,
                defaults={
                    'boat_type': b_type,
                    'length': length,
                    'weight': weight,
                    'flag': nat,
                    'color': random.choice(['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6'])
                }
            )
            
            # Create a booking
            if berths:
                berth = berths.pop(random.randint(0, len(berths)-1))
                Booking.objects.get_or_create(
                    boat=boat,
                    berth=berth,
                    defaults={
                        'start_date': today - timedelta(days=random.randint(1, 10)),
                        'end_date': today + timedelta(days=random.randint(5, 30)),
                        'status': random.choice(['ACTIVE', 'PLANNED']),
                        'booking_type': random.choice(['SHORT', 'LONG']),
                        'reference': 'DIRECT'
                    }
                )
        self.stdout.write("- Customers, Boats and Bookings seeded.")

        # 6. Historical Data (Last 6 Months)
        self.stdout.write("Generating historical data...")
        for m in range(1, 7):
            past_date = today - timedelta(days=30*m)
            # Create 2-3 historical bookings per month
            for _ in range(random.randint(2, 3)):
                h_cust = random.choice(Customer.objects.filter(boats__isnull=False))
                h_boat = random.choice(h_cust.boats.all())
                h_berth = random.choice(Berth.objects.all())
                
                h_booking = Booking.objects.create(
                    boat=h_boat,
                    berth=h_berth,
                    start_date=past_date - timedelta(days=random.randint(5, 10)),
                    end_date=past_date - timedelta(days=random.randint(1, 4)),
                    status='COMPLETED',
                    booking_type='SHORT'
                )
                
                # Create corresponding PAID invoice
                h_inv = Invoice.objects.create(
                    customer=h_cust,
                    booking=h_booking,
                    status='PAID',
                    total_amount=random.randint(150, 600),
                    date=past_date,
                    payment_method=random.choice(['CASH', 'CARD', 'TRANSFER'])
                )
                # Add a service item to some historical invoices
                if random.random() > 0.3:
                    h_service = random.choice(Service.objects.all())
                    qty = random.randint(1, 5)
                    InvoiceItem.objects.create(
                        invoice=h_inv,
                        description=f"Service: {h_service.name}",
                        quantity=qty,
                        unit_price=h_service.price_per_unit
                    )
                    h_inv.total_amount += h_service.price_per_unit * qty
                    h_inv.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded all marina data including history and services.'))
