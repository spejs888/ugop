from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create sample waiter users with PINs (1-20) and an owner (gazda)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of waiter users to create (default 5)')

    def handle(self, *args, **options):
        count = options['count']
        sample_names = ['Ana', 'Borko', 'Cvetan', 'Dragan', 'Elena', 'Filip', 'Goran', 'Hana', 'Ivana', 'Jovan']
        created = 0
        pin = 1
        for i in range(count):
            username = sample_names[i % len(sample_names)].lower() + str(i+1)
            password = str(pin)
            user, created_flag = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created/updated waiter {username} with PIN {password}'))
            created += 1
            pin += 1
            if pin > 20:
                pin = 1

        # create owner/gazda with PIN 20 and staff/superuser privileges
        owner_username = 'gazda'
        owner_pin = '20'
        owner, owner_created = User.objects.get_or_create(username=owner_username)
        owner.set_password(owner_pin)
        owner.is_staff = True
        owner.is_superuser = True
        owner.save()
        self.stdout.write(self.style.SUCCESS(f'Created/updated owner {owner_username} with PIN {owner_pin}'))

        self.stdout.write(self.style.SUCCESS(f'Total waiters created/updated: {created}'))
