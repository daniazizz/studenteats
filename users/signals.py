from django.db.models.signals import post_save ## A signal that gets fired after an object gets saved
from django.contrib.auth.models import User## Sender
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)## Receiver is a decorator
def create_profile(sender, instance, created, **kwargs): ## kwargs=rest of arguments
    if created:
        Profile.objects.create(user=instance) 

@receiver(post_save, sender=User)## Receiver is a decorator
def save_profile(sender, instance, **kwargs): ## kwargs=rest of arguments
    instance.profile.save()