"""
EarnWave Leaderboard Update Command
Run daily via cron: python manage.py update_leaderboard
Cron example: 0 0 * * * /path/to/venv/bin/python /path/to/manage.py update_leaderboard
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
import datetime


class Command(BaseCommand):
    help = 'Update leaderboard rankings'

    def handle(self, *args, **kwargs):
        from accounts.models import User
        from rewards.models import PointTransaction
        from quizzes.models import Leaderboard

        self.stdout.write('Updating leaderboard...')
        today = timezone.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        periods = {
            'daily': today,
            'weekly': week_start,
            'monthly': month_start,
        }

        for period_name, period_start in periods.items():
            if period_name == 'daily':
                filter_kwargs = {'created_at__date': today}
            elif period_name == 'weekly':
                filter_kwargs = {'created_at__date__gte': week_start}
            else:
                filter_kwargs = {'created_at__date__gte': month_start}

            rankings = PointTransaction.objects.filter(
                transaction_type='credit', **filter_kwargs
            ).values('user').annotate(
                total=Sum('points')
            ).order_by('-total')[:100]

            for rank, entry in enumerate(rankings, 1):
                Leaderboard.objects.update_or_create(
                    user_id=entry['user'],
                    period=period_name,
                    period_start=period_start,
                    defaults={'points': entry['total'], 'rank': rank}
                )

        # All-time
        alltime = PointTransaction.objects.filter(
            transaction_type='credit'
        ).values('user').annotate(
            total=Sum('points')
        ).order_by('-total')[:100]

        for rank, entry in enumerate(alltime, 1):
            Leaderboard.objects.update_or_create(
                user_id=entry['user'],
                period='alltime',
                period_start=today,
                defaults={'points': entry['total'], 'rank': rank}
            )

        self.stdout.write(self.style.SUCCESS(f'✅ Leaderboard updated for {len(periods)+1} periods'))
