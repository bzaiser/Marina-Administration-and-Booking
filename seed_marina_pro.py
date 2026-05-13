import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marina_project.settings')
django.setup()

from marina.models import Customer, Boat, Block, Berth, Booking

def seed_data():
    print("Cleaning old data...")
    Booking.objects.all().delete()
    Boat.objects.all().delete()
    Customer.objects.all().delete()
    Berth.objects.all().delete()
    Block.objects.all().delete()

    print("Creating Blocks...")
    blocks = [
        Block.objects.create(name='A', color='#3498db', block_type='WATER'),
        Block.objects.create(name='B', color='#9b59b6', block_type='WATER'),
        Block.objects.create(name='C', color='#e67e22', block_type='WATER'),
        Block.objects.create(name='D', color='#2ecc71', block_type='WATER'),
        Block.objects.create(name='E', color='#e74c3c', block_type='WATER'),
        Block.objects.create(name='F', color='#f39c12', block_type='SERVICE'),
    ]

    print("Creating Berths...")
    all_berths = []
    service_berths = []
    for block in blocks:
        if block.block_type == 'SERVICE':
            for i in range(1, 6):
                b = Berth.objects.create(
                    block=block,
                    number=f"DOCK {i}",
                    max_length=25.0,
                    max_weight=100.0
                )
                all_berths.append(b)
                service_berths.append(b)
        else:
            for i in range(1, 16):
                all_berths.append(Berth.objects.create(
                    block=block,
                    number=i,
                    max_length=random.choice([10, 12, 15, 20]),
                    max_weight=random.choice([5, 10, 20, 40])
                ))

    print("Creating Customers...")
    customers_data = [
        ('Michael Schmidt', 'DE', 'DE'),
        ('John Miller', 'US', 'EN'),
        ('Giorgos Stephanopoulos', 'GR', 'GR'),
        ('James Bennett', 'GB', 'EN'),
        ('Pierre Dubois', 'FR', 'FR'),
        ('Giuseppe Rossi', 'IT', 'IT'),
    ]
    
    # Store customers in a dict by nationality for easier matching
    customers_by_nat = {}
    for name, nat, lang in customers_data:
        c = Customer.objects.create(
            name=name,
            email=f"{name.lower().replace(' ', '.')}@example.com",
            phone=f"+{random.randint(10, 99)} 12345678",
            nationality=nat,
            language=lang
        )
        customers_by_nat[nat] = c

    print("Creating Boats...")
    boat_names = [
        ('Alsterperle', 'SAIL', 'DE', '#3498db'),
        ('Liberty Star', 'MOTOR', 'US', '#e74c3c'),
        ('Odyssey', 'SAIL', 'GR', '#2ecc71'),
        ('Royal Flush', 'MOTOR', 'GB', '#95a5a6'),
        ('La Belle Vie', 'CAT', 'FR', '#e67e22'),
        ('Dolce Vita', 'SAIL', 'IT', '#8e44ad'),
        ('Aegean Dream', 'CAT', 'GR', '#f1c40f'),
        ('Northern Light', 'SAIL', 'GB', '#1abc9c'),
    ]

    boats = []
    for name, btype, flag, color in boat_names:
        boats.append(Boat.objects.create(
            name=name,
            owner=customers_by_nat.get(flag, random.choice(list(customers_by_nat.values()))),
            boat_type=btype,
            length=random.randint(8, 18),
            weight=random.randint(2, 25),
            flag=flag,
            color=color,
            year_built=random.randint(1990, 2023),
            diesel_tank=random.randint(100, 1000),
            water_tank=random.randint(100, 800),
            notes="Ready for the season"
        ))

    print("Creating Bookings...")
    today = date.today()
    
    # 1. Long term bookings
    for i in range(5):
        boat = boats[i]
        berth = all_berths[i]
        Booking.objects.create(
            boat=boat,
            berth=berth,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=180),
            booking_type='LONG',
            status='ACTIVE'
        )

    # 2. At Sea (Long term boat away)
    at_sea_boat = boats[5]
    at_sea_berth = all_berths[5]
    Booking.objects.create(
        boat=at_sea_boat,
        berth=at_sea_berth,
        start_date=today - timedelta(days=20),
        end_date=today + timedelta(days=100),
        booking_type='LONG',
        is_at_sea=True,
        status='ACTIVE'
    )

    # 3. Guest occupying the "At Sea" spot
    guest_boat = boats[6]
    Booking.objects.create(
        boat=guest_boat,
        berth=at_sea_berth,
        start_date=today - timedelta(days=2),
        end_date=today + timedelta(days=5),
        booking_type='SHORT',
        status='ACTIVE'
    )

    # 4. Some short term bookings
    for i in range(7, 15):
        boat = random.choice(boats)
        berth = random.choice(all_berths[10:])
        Booking.objects.create(
            boat=boat,
            berth=berth,
            start_date=today + timedelta(days=random.randint(-5, 5)),
            end_date=today + timedelta(days=random.randint(10, 20)),
            booking_type='SHORT',
            status='ACTIVE'
        )

    print("Creating Services and Orders...")
    from marina.models import Service, BookingService, ServiceProvider
    
    BookingService.objects.all().delete()
    Service.objects.all().delete()
    ServiceProvider.objects.all().delete()
    
    provider = ServiceProvider.objects.create(
        name="Samos Marine Services",
        phone="+30 22730 12345",
        email="info@samos-marine.gr"
    )
    
    services = [
        Service.objects.create(name="Engine Maintenance", service_type='MAINTENANCE', unit='HOUR', price_per_unit=65, color='#f39c12', provider=provider),
        Service.objects.create(name="Hull Cleaning", service_type='CLEANING', unit='PIECE', price_per_unit=150, color='#3498db', provider=provider),
        Service.objects.create(name="Antifouling", service_type='MAINTENANCE', unit='PIECE', price_per_unit=450, color='#e67e22', provider=provider),
    ]
    
    # Create some scheduled service orders for the planning view
    for i in range(4):
        boat = boats[i]
        service = random.choice(services)
        # Randomly assign a service berth to some services
        chosen_berth = random.choice(service_berths) if random.random() > 0.5 else None
        
        BookingService.objects.create(
            boat=boat,
            service=service,
            berth=chosen_berth,
            scheduled_start=today + timedelta(days=random.randint(-2, 5)),
            scheduled_end=today + timedelta(days=random.randint(6, 12)),
            status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED']),
            workload_hours=random.randint(2, 20),
            notes="Standard seasonal checkup"
        )

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
