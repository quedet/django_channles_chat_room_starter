from django.contrib.auth.models import User
from faker import Faker

fake = Faker()

# Delete all users
# User.objects.all().delete()

# Generate 30 random emails and iterate theme
for email in [fake.unique.email() for i in range(5)]:
    # Create user in database
    user = User.objects.create(fake.user_name(), email, "azerty0123456789")
    user.last_name = fake.last_name()
    user.is_active = True
    user.save()
    