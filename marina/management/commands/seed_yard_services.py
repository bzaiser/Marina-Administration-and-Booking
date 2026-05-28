from django.core.management.base import BaseCommand
from marina.models import Service, ServiceCategory, ServiceProvider

class Command(BaseCommand):
    help = 'Seeds professional Yard Service Catalog (Maintenance Tasks & Spare Parts)'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Yard Service Catalog...")
        
        # 1. Get or Create Service Provider
        provider, _ = ServiceProvider.objects.get_or_create(
            name="Samos Yacht Service & Repair",
            defaults={
                'phone': '+30 22730 12345',
                'email': 'yard@marina-samos.com'
            }
        )
        self.stdout.write(f"- Provider '{provider.name}' ready.")

        # 2. Create Service Categories
        categories = {
            'Hull & Bottom Treatment': {
                'desc': 'Antifouling, high-pressure washing, anode replacement, gelcoat repairs, osmosis treatment.',
                'is_for_marina': False,
                'is_for_yard': True
            },
            'Engine & Mechanical': {
                'desc': 'Engine annual services, shaft & propeller maintenance, gearbox repair, impeller replacements.',
                'is_for_marina': False,
                'is_for_yard': True
            },
            'Rigging & Sail Care': {
                'desc': 'Rigging inspections, mast stepping, sail repairs, winch servicing.',
                'is_for_marina': False,
                'is_for_yard': True
            },
            'Electrical & Electronics': {
                'desc': 'Battery replacements, wiring, VHF, autopilot, depth sounder installs.',
                'is_for_marina': False,
                'is_for_yard': True
            },
            'Cleaning & Detailing': {
                'desc': 'Polishing, waxing, teak care, interior cleaning.',
                'is_for_marina': True,  # Available for both
                'is_for_yard': True
            },
            'Spare Parts & Consumables': {
                'desc': 'Filters, oils, anodes, paints, ropes, stainless steel hardware.',
                'is_for_marina': False,
                'is_for_yard': True
            }
        }

        cat_objs = {}
        for cat_name, info in categories.items():
            cat, created = ServiceCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': info['desc'],
                    'is_for_marina': info['is_for_marina'],
                    'is_for_yard': info['is_for_yard']
                }
            )
            cat_objs[cat_name] = cat
            if created:
                self.stdout.write(f"  + Created Category: {cat_name}")
            else:
                # Ensure the flags are correct
                cat.is_for_yard = info['is_for_yard']
                cat.save()
                self.stdout.write(f"  ~ Updated Category: {cat_name}")

        # 3. Create Services (Tasks and Parts)
        services_data = [
            # Hull & Bottom Treatment
            ("Antifouling Application (Labor)", "Professional sanding and 2 coats of antifouling paint.", 'Hull & Bottom Treatment', 'HOUR', 45.00, '#1abc9c'),
            ("High-Pressure Hull Washing", "Removal of marine growth, algae, and barnacles.", 'Hull & Bottom Treatment', 'HOUR', 15.00, '#16a085'),
            ("Gelcoat & Fiberglass Repair", "Professional gelcoat scratch and structural fiberglass repair.", 'Hull & Bottom Treatment', 'HOUR', 70.00, '#2ecc71'),
            ("Osmosis Treatment & Barrier", "Blister stripping, drying, and multi-layer epoxy barrier application.", 'Hull & Bottom Treatment', 'HOUR', 85.00, '#27ae60'),
            ("Anode Replacement (Labor)", "Removal and installation of new sacrificial anodes on shaft, rudder, and thruster.", 'Hull & Bottom Treatment', 'HOUR', 40.00, '#11806a'),
            
            # Engine & Mechanical
            ("Engine Annual Service (Labor)", "Oil change, filters, impeller inspection, belt check, transmission oil.", 'Engine & Mechanical', 'HOUR', 65.00, '#e74c3c'),
            ("Propeller & Shaft Maintenance", "Polishing propeller, checking cutlass bearing, shaft alignment.", 'Engine & Mechanical', 'HOUR', 50.00, '#c0392b'),
            ("Outboard Motor Service", "Servicing of dinghy outboard engines (spark plugs, lube, impeller).", 'Engine & Mechanical', 'HOUR', 45.00, '#d35400'),
            ("Bow Thruster Maintenance", "Cleaning propeller tunnel, checking motor connection, replacing internal anodes.", 'Engine & Mechanical', 'HOUR', 55.00, '#e67e22'),

            # Rigging & Sail Care
            ("Rigging Inspection & Tuning", "Visual inspection of standing and running rigging, tension adjustment.", 'Rigging & Sail Care', 'HOUR', 60.00, '#3498db'),
            ("Winch Servicing (Labor)", "Disassembly, cleaning, greasing, and reassembly of deck winches.", 'Rigging & Sail Care', 'HOUR', 45.00, '#2980b9'),
            ("Mast Stepping / Unstepping", "Crane operation and labor to step/unstep sailboat mast.", 'Rigging & Sail Care', 'PIECE', 250.00, '#34495e'),

            # Electrical & Electronics
            ("Electrical Diagnostics & Wiring", "Troubleshooting short circuits, bilge pumps, solar panels, and shore power.", 'Electrical & Electronics', 'HOUR', 60.00, '#9b59b6'),
            ("Marine Electronics Install", "Installation and configuration of GPS, Autopilot, VHF, or Radar systems.", 'Electrical & Electronics', 'HOUR', 65.00, '#8e44ad'),

            # Cleaning & Detailing
            ("Hull Side Polish & Waxing", "Compounding, polishing, and high-gloss waxing of hull gelcoat.", 'Cleaning & Detailing', 'HOUR', 45.00, '#f1c40f'),
            ("Teak Deck Sanding & Oil", "Gentle sanding of teak decks and application of premium teak sealer/oil.", 'Cleaning & Detailing', 'HOUR', 55.00, '#f39c12'),
            ("Superstructure Cleaning", "Washing deck, cabin sides, windows, and stainless steel fittings.", 'Cleaning & Detailing', 'HOUR', 30.00, '#f5d342'),

            # Spare Parts & Consumables
            ("Premium Antifouling Paint (Navy Blue)", "5-Liter bucket of self-polishing antifouling paint.", 'Spare Parts & Consumables', 'PIECE', 185.00, '#34495e'),
            ("Sacrificial Zinc Anode (Shaft)", "Standard sacrificial anode for prop shaft.", 'Spare Parts & Consumables', 'PIECE', 25.00, '#7f8c8d'),
            ("Sacrificial Zinc Anode (Hull)", "Standard teardrop sacrificial anode for hull grounding.", 'Spare Parts & Consumables', 'PIECE', 35.00, '#95a5a6'),
            ("Marine Engine Oil 15W-40", "Premium engine oil for diesel marine engines.", 'Spare Parts & Consumables', 'LITER', 12.00, '#bdc3c7'),
            ("Yanmar Fuel Filter Element", "Secondary fuel filter insert for Yanmar engines.", 'Spare Parts & Consumables', 'PIECE', 22.50, '#34495e'),
            ("Volvo Impeller Kit", "Raw water pump impeller including O-ring and lube.", 'Spare Parts & Consumables', 'PIECE', 48.00, '#2ecc71'),
            ("Heavy Duty Dock Line (16mm)", "Braided polyester dock line with spliced eye, per meter.", 'Spare Parts & Consumables', 'PIECE', 3.50, '#95a5a6'),
        ]

        for s_name, s_desc, cat_name, s_unit, s_price, s_color in services_data:
            service, created = Service.objects.get_or_create(
                name=s_name,
                defaults={
                    'description': s_desc,
                    'category': cat_objs[cat_name],
                    'unit': s_unit,
                    'price_per_unit': s_price,
                    'color': s_color,
                    'provider': provider
                }
            )
            if created:
                self.stdout.write(f"  + Created Service: {s_name} (€{s_price}/{s_unit})")
            else:
                self.stdout.write(f"  ~ Service already exists: {s_name}")

        self.stdout.write(self.style.SUCCESS("Successfully seeded Yard Service Catalog!"))
