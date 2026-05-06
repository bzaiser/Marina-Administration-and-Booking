from django.core.management.base import BaseCommand
from marina.models import Country

class Command(BaseCommand):
    help = 'Seeds the initial country/flag list'

    def handle(self, *args, **kwargs):
        countries = [
            ('de', 'Germany'), ('do', 'Dominican Republic'), ('es', 'Spain'),
            ('fi', 'Finland'), ('fr', 'France'), ('gr', 'Greece'),
            ('il', 'Israel'), ('it', 'Italy'), ('mt', 'Malta'),
            ('nl', 'Netherlands'), ('nz', 'New Zealand'), ('pl', 'Poland'),
            ('sm', 'San Marino'), ('se', 'Sweden'), ('tr', 'Turkey'),
            ('ua', 'Ukraine'), ('gb', 'United Kingdom'), ('us', 'United States'),
            ('no', 'Norway'), ('mc', 'Monaco'), ('dk', 'Denmark'),
            ('mh', 'Marshall Islands'), ('lu', 'Luxembourg'), ('ch', 'Switzerland'),
            ('xx', 'Other/Unknown'),
        ]

        count = 0
        for iso, name in countries:
            obj, created = Country.objects.get_or_create(iso_code=iso, defaults={'name': name})
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} new countries.'))
