from django.core.management.base import BaseCommand
from marina.models import Berth, Block

class Command(BaseCommand):
    help = 'Seeds 75 berths across 5 blocks'

    def handle(self, *args, **options):
        # Create Blocks
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
            
            # Create 15 berths per block
            for i in range(1, 16):
                Berth.objects.get_or_create(
                    block=block,
                    number=str(i),
                    defaults={
                        'max_length': 15.0 + (i % 5) * 5,
                        'max_weight': 20.0 + (i % 5) * 10
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded blocks and berths'))
