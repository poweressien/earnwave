"""
EarnWave Badge Check Command
Run hourly via cron: python manage.py check_badges
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Check and award badges to eligible users'

    def handle(self, *args, **kwargs):
        from accounts.models import User
        from rewards.views import check_and_award_badges

        users = User.objects.filter(is_active=True)
        awarded = 0
        for user in users:
            try:
                from rewards.models import UserBadge
                before = UserBadge.objects.filter(user=user).count()
                check_and_award_badges(user)
                after = UserBadge.objects.filter(user=user).count()
                awarded += (after - before)
            except Exception as e:
                self.stderr.write(f'Error for user {user.email}: {e}')

        self.stdout.write(self.style.SUCCESS(f'✅ Badge check complete. {awarded} badges awarded to {users.count()} users.'))
