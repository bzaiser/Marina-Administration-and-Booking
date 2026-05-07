import os
import requests
import django
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Download and update local vendor libraries from CDNs'

    # Comprehensive list of ISO country codes for flag-icons
    ALL_COUNTRIES = [
        'ad', 'ae', 'af', 'ag', 'ai', 'al', 'am', 'ao', 'aq', 'ar', 'as', 'at', 'au', 'aw', 'ax', 'az',
        'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bl', 'bm', 'bn', 'bo', 'bq', 'br', 'bs',
        'bt', 'bv', 'bw', 'by', 'bz', 'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn',
        'co', 'cr', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'ee',
        'eg', 'eh', 'er', 'es', 'et', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf',
        'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm',
        'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm',
        'jo', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc',
        'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 'mk',
        'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz', 'na',
        'nc', 'ne', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'pa', 'pe', 'pf', 'pg',
        'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw',
        'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'ss',
        'st', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to',
        'tr', 'tt', 'tv', 'tw', 'tz', 'ua', 'ug', 'um', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi',
        'vn', 'vu', 'wf', 'ws', 'ye', 'yt', 'za', 'zm', 'zw', 'xx'
    ]

    LIBS = {
        'bootstrap': [
            ('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css', 'bootstrap.min.css'),
            ('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js', 'bootstrap.bundle.min.js'),
        ],
        'bootstrap-icons': [
            ('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css', 'bootstrap-icons.css'),
            ('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/fonts/bootstrap-icons.woff', 'fonts/bootstrap-icons.woff'),
            ('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/fonts/bootstrap-icons.woff2', 'fonts/bootstrap-icons.woff2'),
        ],
        'flag-icons': [
            ('https://cdn.jsdelivr.net/gh/lipis/flag-icons@6.11.0/css/flag-icons.min.css', 'css/flag-icons.min.css'),
        ],
        'htmx': [
            ('https://unpkg.com/htmx.org@1.9.4/dist/htmx.min.js', 'htmx.min.js'),
        ],
        'alpinejs': [
            ('https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js', 'alpine.min.js'),
        ],
        'ag-grid': [
            ('https://cdn.jsdelivr.net/npm/ag-grid-community/dist/ag-grid-community.min.js', 'ag-grid-community.min.js'),
        ],
        'chartjs': [
            ('https://cdn.jsdelivr.net/npm/chart.js', 'chart.min.js'),
        ],
        'visjs': [
            ('https://unpkg.com/vis-timeline@latest/standalone/umd/vis-timeline-graph2d.min.js', 'vis-timeline-graph2d.min.js'),
            ('https://unpkg.com/vis-timeline@latest/styles/vis-timeline-graph2d.min.css', 'vis-timeline-graph2d.min.css'),
        ]
    }

    def handle(self, *args, **options):
        vendor_dir = os.path.join(settings.BASE_DIR, 'static', 'vendor')
        
        from marina.models import Country
        common_countries = list(Country.objects.values_list('iso_code', flat=True))

        for lib_name, files in self.LIBS.items():
            self.stdout.write(f'Updating {lib_name}...')
            lib_dir = os.path.join(vendor_dir, lib_name)
            os.makedirs(lib_dir, exist_ok=True)
            
            # Special handling for flag-icons to download ALL SVGs for offline completeness
            current_files = list(files)
            if lib_name == 'flag-icons':
                for country in self.ALL_COUNTRIES:
                    current_files.append((f'https://cdn.jsdelivr.net/gh/lipis/flag-icons@6.11.0/flags/4x3/{country}.svg', f'flags/4x3/{country}.svg'))
                    current_files.append((f'https://cdn.jsdelivr.net/gh/lipis/flag-icons@6.11.0/flags/1x1/{country}.svg', f'flags/1x1/{country}.svg'))

            for url, filename in current_files:
                dest_path = os.path.join(lib_dir, filename)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                    self.stdout.write(f'  Skipping {filename} (already exists)')
                    continue
                
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    with open(dest_path, 'wb') as f:
                        f.write(response.content)
                    self.stdout.write(self.style.SUCCESS(f'  Downloaded {filename}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Failed to download {filename}: {e}'))

        self.stdout.write(self.style.SUCCESS('Vendor libraries updated successfully.'))
