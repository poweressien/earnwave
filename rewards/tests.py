"""
EarnWave Rewards Test Suite
"""
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, UserProfile
from .models import PointTransaction, AirtimeRedemption, Badge, UserBadge, Notification


def make_user(email='user@test.ng', first='Test', last='User'):
    user = User.objects.create_user(
        email=email, password='TestPass@123',
        first_name=first, last_name=last
    )
    UserProfile.objects.get_or_create(user=user)
    return user


class PointTransactionTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_award_points(self):
        tx = PointTransaction.award_points(
            self.user, 50, 'signup_bonus', 'Welcome bonus'
        )
        self.assertEqual(tx.points, 50)
        self.assertEqual(tx.transaction_type, 'credit')
        self.assertEqual(self.user.points_balance, 50)

    def test_deduct_points(self):
        PointTransaction.award_points(self.user, 200, 'survey', 'Survey reward')
        PointTransaction.deduct_points(self.user, 100, 'redemption', 'Airtime')
        self.assertEqual(self.user.points_balance, 100)

    def test_deduct_insufficient_points_raises(self):
        PointTransaction.award_points(self.user, 50, 'survey', 'Test')
        with self.assertRaises(ValueError):
            PointTransaction.deduct_points(self.user, 200, 'redemption', 'Too much')

    def test_multiple_transactions_balance(self):
        PointTransaction.award_points(self.user, 100, 'survey', 'S1')
        PointTransaction.award_points(self.user, 200, 'quiz', 'Q1')
        PointTransaction.award_points(self.user, 50, 'ad_watch', 'Ad1')
        PointTransaction.deduct_points(self.user, 150, 'redemption', 'R1')
        self.assertEqual(self.user.points_balance, 200)

    def test_profile_total_updated(self):
        PointTransaction.award_points(self.user, 75, 'game', 'Game points')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_points_earned, 75)

    def test_level_progression(self):
        self.assertEqual(self.user.level, 'Bronze')
        PointTransaction.award_points(self.user, 1000, 'admin', 'Test')
        self.assertEqual(self.user.level, 'Silver')
        PointTransaction.award_points(self.user, 4000, 'admin', 'Test2')
        self.assertEqual(self.user.level, 'Gold')


class AirtimeRedemptionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('redeem@test.ng')
        self.client.login(username='redeem@test.ng', password='TestPass@123')
        # Give user enough points
        PointTransaction.award_points(self.user, 5000, 'admin', 'Test balance')

    def test_redeem_valid_request(self):
        response = self.client.post(reverse('rewards:redeem'), {
            'network': 'MTN',
            'phone_number': '08012345678',
            'amount': '10',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AirtimeRedemption.objects.filter(user=self.user).count(), 1)

    def test_redeem_insufficient_points(self):
        # Deplete points first
        PointTransaction.deduct_points(self.user, 4900, 'redemption', 'Drain')
        response = self.client.post(reverse('rewards:redeem'), {
            'network': 'Airtel',
            'phone_number': '08012345678',
            'amount': '50',
        })
        self.assertEqual(AirtimeRedemption.objects.filter(user=self.user).count(), 0)

    def test_points_deducted_on_redeem(self):
        before = self.user.points_balance
        self.client.post(reverse('rewards:redeem'), {
            'network': 'Glo',
            'phone_number': '08098765432',
            'amount': '20',
        })
        after = self.user.points_balance
        self.assertEqual(before - after, 2000)  # ₦20 × 100 pts/naira

    def test_redeem_below_minimum(self):
        response = self.client.post(reverse('rewards:redeem'), {
            'network': 'MTN',
            'phone_number': '08012345678',
            'amount': '5',  # Below ₦10 minimum
        })
        self.assertEqual(AirtimeRedemption.objects.count(), 0)


class AdWatchTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('ad@test.ng')
        self.client.login(username='ad@test.ng', password='TestPass@123')

    def test_watch_ad_earns_points(self):
        import json
        response = self.client.post(
            reverse('rewards:watch_ad'),
            content_type='application/json',
            data=json.dumps({})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['points'], 10)

    def test_ad_daily_limit(self):
        import json
        from django.conf import settings
        # Watch max ads
        for _ in range(settings.DAILY_AD_LIMIT):
            self.client.post(
                reverse('rewards:watch_ad'),
                content_type='application/json',
                data=json.dumps({})
            )
        # One more should fail
        response = self.client.post(
            reverse('rewards:watch_ad'),
            content_type='application/json',
            data=json.dumps({})
        )
        data = response.json()
        self.assertFalse(data['success'])
        self.assertTrue(data.get('limit_reached', False))


class BadgeTest(TestCase):
    def setUp(self):
        self.user = make_user('badge@test.ng')

    def test_badge_creation(self):
        badge = Badge.objects.create(
            name='Test Badge', description='Test',
            rarity='common', condition_type='surveys_completed',
            condition_value=1, points_reward=25
        )
        self.assertEqual(str(badge), 'Test Badge')

    def test_user_badge_award(self):
        badge = Badge.objects.create(
            name='Survey King', description='10 surveys',
            rarity='rare', condition_type='surveys_completed',
            condition_value=1, points_reward=50
        )
        UserBadge.objects.create(user=self.user, badge=badge)
        self.assertEqual(self.user.badges.count(), 1)

    def test_badge_check_awards_correctly(self):
        Badge.objects.create(
            name='First Timer', description='First survey',
            rarity='common', condition_type='surveys_completed',
            condition_value=1, points_reward=25
        )
        self.user.profile.surveys_completed = 1
        self.user.profile.save()
        from rewards.views import check_and_award_badges
        check_and_award_badges(self.user)
        self.assertEqual(self.user.badges.count(), 1)

    def test_badge_not_awarded_twice(self):
        badge = Badge.objects.create(
            name='Unique', description='Once',
            rarity='common', condition_type='surveys_completed',
            condition_value=1, points_reward=10
        )
        self.user.profile.surveys_completed = 5
        self.user.profile.save()
        from rewards.views import check_and_award_badges
        check_and_award_badges(self.user)
        check_and_award_badges(self.user)
        self.assertEqual(UserBadge.objects.filter(user=self.user, badge=badge).count(), 1)
