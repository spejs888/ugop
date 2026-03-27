import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ugop.settings')
django.setup()

from django.contrib.auth import get_user_model

U = get_user_model()

u, created = U.objects.get_or_create(username='marko')
# ensure staff/superuser
u.is_staff = True
u.is_superuser = True
u.set_password('marko')
u.save()
print('created' if created else 'updated')
