from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# Signals are used to automatically create profiles for users

# Once a user is created, a signal is sent to automatically create a profile for that user

# receiver as decorator
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance) 

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()