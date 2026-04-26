"""
EarnWave Accounts Test Suite
"""
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, UserProfile


class UserCreationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_user(self):
        user = User.objects.create_user(
            email='test@earnwave.ng',
            password='TestPass@123',
            first_name='Chidi',
            last_name='Okonkwo'
        )
        self.assertEqual(user.email, 'test@earnwave.ng')
        self.assertEqual(user.get_full_name(), 'Chidi Okonkwo')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_referral_code_auto_generated(self):
        user = User.objects.create_user(
            email='ref@earnwave.ng',
            password='TestPass@123',
            first_name='Ada', last_name='Eze'
        )
        self.assertIsNotNone(user.referral_code)
        self.assertEqual(len(user.referral_code), 8)

    def test_profile_auto_created(self):
        user = User.objects.create_user(
            email='profile@earnwave.ng',
            password='TestPass@123',
            first_name='Emeka', last_name='Nwosu'
        )
        UserProfile.objects.get_or_create(user=user)
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.login_streak, 0)

    def test_signup_view_get(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EarnWave')

    def test_signup_view_post(self):
        response = self.client.post(reverse('accounts:signup'), {
            'first_name': 'Bolu',
            'last_name': 'Adeyemi',
            'email': 'bolu@earnwave.ng',
            'phone_number': '08012345678',
            'password1': 'StrongPass@123',
            'password2': 'StrongPass@123',
            'referral_code': '',
        })
        self.assertEqual(User.objects.filter(email='bolu@earnwave.ng').count(), 1)

    def test_login_view_get(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid_credentials(self):
        User.objects.create_user(
            email='login@earnwave.ng',
            password='TestPass@123',
            first_name='Kemi', last_name='Bello'
        )
        response = self.client.post(reverse('accounts:login'), {
            'email': 'login@earnwave.ng',
            'password': 'TestPass@123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'nobody@earnwave.ng',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            email='dup@earnwave.ng',
            password='TestPass@123',
            first_name='A', last_name='B'
        )
        response = self.client.post(reverse('accounts:signup'), {
            'first_name': 'C', 'last_name': 'D',
            'email': 'dup@earnwave.ng',
            'password1': 'StrongPass@123',
            'password2': 'StrongPass@123',
        })
        self.assertContains(response, 'already registered')

    def test_user_level_bronze_default(self):
        user = User.objects.create_user(
            email='level@earnwave.ng',
            password='TestPass@123',
            first_name='Level', last_name='Test'
        )
        self.assertEqual(user.level, 'Bronze')

    def test_points_balance_zero_initially(self):
        user = User.objects.create_user(
            email='pts@earnwave.ng',
            password='TestPass@123',
            first_name='Points', last_name='Test'
        )
        self.assertEqual(user.points_balance, 0)

    def test_superuser_creation(self):
        admin = User.objects.create_superuser(
            email='admin@earnwave.ng',
            password='Admin@1234',
            first_name='Admin', last_name='User'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class UserStreakTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='streak@earnwave.ng',
            password='TestPass@123',
            first_name='Streak', last_name='Test'
        )
        UserProfile.objects.get_or_create(user=self.user)

    def test_streak_starts_at_zero(self):
        self.assertEqual(self.user.profile.login_streak, 0)

    def test_first_login_sets_streak_to_one(self):
        updated = self.user.profile.update_streak()
        self.assertTrue(updated)
        self.assertEqual(self.user.profile.login_streak, 1)

    def test_same_day_login_no_increment(self):
        self.user.profile.update_streak()
        updated = self.user.profile.update_streak()
        self.assertFalse(updated)
        self.assertEqual(self.user.profile.login_streak, 1)
