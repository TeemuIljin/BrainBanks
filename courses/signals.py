from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, PlayerProfile

# Create or update the user's profile when User is saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        PlayerProfile.objects.create(user=instance)
    else:
        instance.profile.save()
        # Update PlayerProfile if it exists
        if hasattr(instance, 'playerprofile'):
            instance.playerprofile.save()
