# api/management/commands/create_missing_profiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile

class Command(BaseCommand):
    help = 'Create missing user profiles'

    def handle(self, *args, **options):
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write(f'Profile created/verified for user: {user.username}')