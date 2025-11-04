import pandas as pd
from django.core.management.base import BaseCommand
from portal.models import User

class Command(BaseCommand):
    help = 'Import students from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Path to Excel file')

    def handle(self, *args, **kwargs):
        filepath = kwargs['filepath']
        df = pd.read_excel(filepath)

        for _, row in df.iterrows():
            tr = str(row['TR Number']).strip()
            name = str(row['Name']).strip()

            if not User.objects.filter(tr_number=tr).exists():
                User.objects.create_user(tr_number=tr, name=name, role='student')
                self.stdout.write(self.style.SUCCESS(f"Added {name} ({tr})"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped {name} ({tr}) — already exists"))
