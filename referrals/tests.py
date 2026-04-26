"""
EarnWave Referral System Test Suite
"""
from django.test import TestCase
from accounts.models import User, UserProfile
from rewards.models import PointTransaction
from .models import ReferralRecord
from django.conf import settings


def make_user(email, first='User'):
    user = User.objects.create_user(
        email=email, password='TestPass@123',
        first_name=first, last_name='Test'
    )
    UserProfile.objects.get_or_create(user=user)
    return user


class ReferralTest(TestCase):
    def setUp(self):
        self.referrer = make_user('referrer@test.ng', 'Chioma')
        self.referred = make_user('referred@test.ng', 'Tunde')

    def test_referral_record_creation(self):
        ref = ReferralRecord.objects.create(
            referrer=self.referrer, referred=self.referred
        )
        self.assertEqual(ref.status, 'pending')

    def test_qualify_and_reward(self):
        ref = ReferralRecord.objects.create(
            referrer=self.referrer, referred=self.referred
        )
        ref.qualify_and_reward()
        ref.refresh_from_db()
        self.assertEqual(ref.status, 'rewarded')
        self.assertTrue(ref.inviter_bonus_paid)
        self.assertTrue(ref.invitee_bonus_paid)

    def test_referrer_receives_correct_bonus(self):
        ref = ReferralRecord.objects.create(
            referrer=self.referrer, referred=self.referred
        )
        ref.qualify_and_reward()
        inviter_pts = PointTransaction.objects.filter(
            user=self.referrer, transaction_type='credit', source='referral'
        ).first()
        self.assertIsNotNone(inviter_pts)
        self.assertEqual(inviter_pts.points, settings.REFERRAL_BONUS_INVITER)

    def test_referred_receives_correct_bonus(self):
        ref = ReferralRecord.objects.create(
            referrer=self.referrer, referred=self.referred
        )
        ref.qualify_and_reward()
        invitee_pts = PointTransaction.objects.filter(
            user=self.referred, transaction_type='credit', source='referral'
        ).first()
        self.assertIsNotNone(invitee_pts)
        self.assertEqual(invitee_pts.points, settings.REFERRAL_BONUS_INVITEE)

    def test_cannot_reward_twice(self):
        ref = ReferralRecord.objects.create(
            referrer=self.referrer, referred=self.referred
        )
        result1 = ref.qualify_and_reward()
        result2 = ref.qualify_and_reward()
        self.assertTrue(result1)
        self.assertFalse(result2)

    def test_unique_referral_codes(self):
        codes = set([
            make_user(f'code{i}@test.ng').referral_code for i in range(10)
        ])
        self.assertEqual(len(codes), 10)

    def test_referral_view_authenticated(self):
        from django.test import Client
        client = Client()
        client.login(username='referrer@test.ng', password='TestPass@123')
        from django.urls import reverse
        response = client.get(reverse('referrals:home'))
        self.assertEqual(response.status_code, 200)
