from django.core.management.base import BaseCommand
from marina.models import Berth

class Command(BaseCommand):
    help = 'Seeds the initial berths for the Marina'

    def handle(self, *args, **options):
        blocks = [
            ('A', '#3498db'), # Blue
            ('B', '#e74c3c'), # Red
            ('C', '#2ecc71'), # Green
            ('D', '#f1c40f'), # Yellow
            ('E', '#9b59b6'), # Purple
        ]
        
        count = 0
        for block_code, color in blocks:
            for i in range(1, 16):
                berth, created = Berth.objects.get_or_create(
                    block=block_code,
                    number=i,
                    defaults={
                        'color': color,
                        'max_length': 20.0,
                        'max_weight': 50.0
                    }
                )
                if created:
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} berths.'))
