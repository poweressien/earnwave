"""
EarnWave Demo Data Seeder
Creates realistic demo users with activity history.
Usage: python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import random
import datetime


NIGERIAN_FIRST_NAMES = [
    'Chidi', 'Adaeze', 'Emeka', 'Ngozi', 'Tunde', 'Kemi', 'Babatunde',
    'Chioma', 'Seun', 'Amaka', 'Bola', 'Ifeanyi', 'Yemi', 'Olusegun',
    'Fatima', 'Hauwa', 'Ibrahim', 'Zainab', 'Musa', 'Aisha', 'Dayo',
    'Funmilayo', 'Gbenga', 'Ifeoma', 'Jide', 'Kunle', 'Lanre', 'Moji'
]

NIGERIAN_LAST_NAMES = [
    'Okonkwo', 'Adeyemi', 'Nwosu', 'Bello', 'Okafor', 'Adeleke', 'Eze',
    'Adesanya', 'Okeke', 'Babatunde', 'Nwachukwu', 'Abubakar', 'Dankwa',
    'Olawale', 'Chukwu', 'Abdullahi', 'Obi', 'Fashola', 'Musa', 'Yakubu'
]

NETWORKS = ['MTN', 'Airtel', 'Glo', '9mobile']
STATES = ['Lagos', 'Abuja', 'Kano', 'Rivers', 'Oyo', 'Anambra', 'Kaduna', 'Delta']


class Command(BaseCommand):
    help = 'Seed EarnWave with realistic demo users and activity'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=20, help='Number of demo users')
        parser.add_argument('--clear', action='store_true', help='Clear demo users first')

    def handle(self, *args, **options):
        from accounts.models import User, UserProfile
        from rewards.models import PointTransaction, AirtimeRedemption, Notification
        from referrals.models import ReferralRecord

        count = options['users']
        self.stdout.write(self.style.WARNING(f'🌊 Creating {count} demo users...'))

        if options['clear']:
            User.objects.filter(email__endswith='@demo.earnwave.ng').delete()
            self.stdout.write('  Cleared existing demo users')

        users = []
        for i in range(count):
            first = random.choice(NIGERIAN_FIRST_NAMES)
            last = random.choice(NIGERIAN_LAST_NAMES)
            email = f'{first.lower()}.{last.lower()}{i}@demo.earnwave.ng'

            if User.objects.filter(email=email).exists():
                continue

            user = User.objects.create_user(
                email=email,
                password='Demo@1234',
                first_name=first,
                last_name=last,
                is_verified=True,
            )
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.state = random.choice(STATES)
            profile.preferred_network = random.choice(NETWORKS)
            profile.airtime_phone = f'080{random.randint(10000000, 99999999)}'
            profile.login_streak = random.randint(0, 30)
            profile.longest_streak = profile.login_streak + random.randint(0, 10)

            # Give each user random points history
            activity_count = random.randint(5, 50)
            total_pts = 0
            sources = [
                ('survey', 'Completed survey: Nigerian Internet Habits', 50),
                ('survey', 'Completed survey: Mobile Money Research', 100),
                ('quiz', 'Quiz: Nigeria Basics — 4/5 correct', 40),
                ('quiz', 'Quiz: Tech & Internet — 3/4 correct', 30),
                ('game', 'Memory Match Classic — completed', 25),
                ('game', 'Speed Math Blitz — score: 12', 35),
                ('ad_watch', 'Ad watch #1 — daily bonus', 10),
                ('ad_watch', 'Ad watch #2 — daily bonus', 10),
                ('daily_login', 'Daily login streak — Day 3!', 15),
                ('referral', 'Referral bonus: friend joined', 100),
                ('signup_bonus', 'Welcome bonus for joining EarnWave!', 50),
            ]
            for _ in range(activity_count):
                src, desc, pts = random.choice(sources)
                pts_var = pts + random.randint(-5, 15)
                days_ago = random.randint(0, 60)
                tx = PointTransaction.objects.create(
                    user=user, points=pts_var, transaction_type='credit',
                    source=src, description=desc,
                )
                tx.created_at = timezone.now() - datetime.timedelta(days=days_ago)
                tx.save(update_fields=['created_at'])
                total_pts += pts_var

            profile.total_points_earned = total_pts
            profile.surveys_completed = random.randint(0, 10)
            profile.quizzes_completed = random.randint(0, 15)
            profile.games_completed = random.randint(0, 8)
            profile.total_airtime_earned = random.randint(0, 500)
            profile.save()

            # Some users have redemptions
            if random.random() > 0.5 and total_pts > 1000:
                redeem_amt = random.choice([50, 100, 200, 500])
                pts_needed = redeem_amt * 100
                if total_pts >= pts_needed:
                    PointTransaction.objects.create(
                        user=user, points=pts_needed, transaction_type='debit',
                        source='redemption',
                        description=f'Airtime redemption: ₦{redeem_amt} {profile.preferred_network}'
                    )
                    AirtimeRedemption.objects.create(
                        user=user, points_used=pts_needed,
                        airtime_amount=redeem_amt,
                        network=profile.preferred_network,
                        phone_number=profile.airtime_phone,
                        status=random.choice(['completed', 'completed', 'pending']),
                    )

            users.append(user)

        # Create some referral chains
        if len(users) >= 4:
            for i in range(min(8, len(users) // 2)):
                try:
                    referrer = random.choice(users[:len(users)//2])
                    referred = random.choice(users[len(users)//2:])
                    if not ReferralRecord.objects.filter(referrer=referrer, referred=referred).exists():
                        ref = ReferralRecord.objects.create(
                            referrer=referrer, referred=referred
                        )
                        ref.qualify_and_reward()
                except Exception:
                    pass

        # Update leaderboard
        self._update_leaderboard(users)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Created {len(users)} demo users with realistic activity data!'
        ))
        self.stdout.write(f'  Login with any demo account: password = Demo@1234')
        self.stdout.write(f'  Sample: {users[0].email if users else "none"}')

    def _update_leaderboard(self, users):
        from quizzes.models import Leaderboard
        from django.db.models import Sum
        from rewards.models import PointTransaction
        today = timezone.now().date()

        all_users = list(users)
        all_users_pts = []
        for u in all_users:
            pts = PointTransaction.objects.filter(
                user=u, transaction_type='credit'
            ).aggregate(t=Sum('points'))['t'] or 0
            all_users_pts.append((u, pts))

        all_users_pts.sort(key=lambda x: x[1], reverse=True)
        for rank, (user, pts) in enumerate(all_users_pts[:20], 1):
            Leaderboard.objects.update_or_create(
                user=user, period='alltime', period_start=today,
                defaults={'points': pts, 'rank': rank}
            )
            Leaderboard.objects.update_or_create(
                user=user, period='weekly', period_start=today,
                defaults={'points': pts // 4, 'rank': rank}
            )
        self.stdout.write(f'  ✓ Leaderboard updated for {min(20, len(all_users_pts))} users')
