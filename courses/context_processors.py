from .models import PlayerProfile
from django.utils import timezone

def active_effects(request):
    """Add active effects to template context"""
    if request.user.is_authenticated:
        try:
            player_profile = PlayerProfile.objects.get(user=request.user)
            effects = []
            now = timezone.now()
            
            # Check for active effects
            if player_profile.streak_freeze_count > 0:
                effects.append('❄️')
            
            if (player_profile.fired_up_streak_until and 
                now < player_profile.fired_up_streak_until):
                effects.append('🔥')
            
            if (player_profile.experience_festival_until and 
                now < player_profile.experience_festival_until):
                effects.append('🎉')
            
            return {'active_effects': effects}
        except PlayerProfile.DoesNotExist:
            pass
    
    return {'active_effects': []}
