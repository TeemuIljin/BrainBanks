from django.core.management.base import BaseCommand
from courses.models import PlayerProfile, LeaderboardEntry


class Command(BaseCommand):
    help = 'Sync leaderboard entries with current PlayerProfile data'

    def handle(self, *args, **options):
        self.stdout.write('Starting leaderboard sync...')
        
        # Count before sync
        before_count = LeaderboardEntry.objects.count()
        
        # Sync leaderboard
        for profile in PlayerProfile.objects.all():
            if profile.points > 0:  # Only include users with points
                entry, created = LeaderboardEntry.objects.get_or_create(
                    name=profile.user.username,
                    defaults={'score': 0}
                )
                # Update score to match current points
                if entry.score != profile.points:
                    entry.score = profile.points
                    entry.save()
                    if created:
                        self.stdout.write(f'Created entry for {profile.user.username}: {profile.points} points')
                    else:
                        self.stdout.write(f'Updated entry for {profile.user.username}: {profile.points} points')
        
        # Remove entries for users who no longer exist or have 0 points
        removed_count = LeaderboardEntry.objects.exclude(
            name__in=PlayerProfile.objects.filter(points__gt=0).values_list('user__username', flat=True)
        ).count()
        
        LeaderboardEntry.objects.exclude(
            name__in=PlayerProfile.objects.filter(points__gt=0).values_list('user__username', flat=True)
        ).delete()
        
        after_count = LeaderboardEntry.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Leaderboard sync completed! '
                f'Before: {before_count}, After: {after_count}, Removed: {removed_count}'
            )
        )
