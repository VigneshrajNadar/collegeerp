from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')

        if not email or not password:
            self.stdout.write(self.style.WARNING('ADMIN_EMAIL or ADMIN_PASSWORD not set in environment variables. Skipping superuser creation.'))
            return

        if not User.objects.filter(email=email).exists():
            self.stdout.write(f'Creating superuser {email}...')
            User.objects.create_superuser(email=email, password=password, user_type='1')
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} created successfully!'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {email} already exists.'))
