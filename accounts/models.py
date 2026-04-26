import uuid
import string
import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


def generate_referral_code():
    """Generate a unique 8-char referral code. Safe during migrations."""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=8))
    try:
        while User.objects.filter(referral_code=code).exists():
            code = ''.join(random.choices(chars, k=8))
    except Exception:
        pass  # Table may not exist yet during migrations
    return code


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    referral_code = models.CharField(max_length=10, unique=True, default=generate_referral_code)
    referred_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals'
    )

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def points_balance(self):
        from rewards.models import PointTransaction
        from django.db.models import Sum
        earned = PointTransaction.objects.filter(
            user=self, transaction_type='credit'
        ).aggregate(total=Sum('points'))['total'] or 0
        spent = PointTransaction.objects.filter(
            user=self, transaction_type='debit'
        ).aggregate(total=Sum('points'))['total'] or 0
        return earned - spent

    @property
    def level(self):
        points = self.points_balance
        thresholds = settings.LEVEL_THRESHOLDS
        level = 'Bronze'
        for lvl, threshold in thresholds.items():
            if points >= threshold:
                level = lvl
        return level

    @property
    def level_color(self):
        colors = {
            'Bronze': '#CD7F32', 'Silver': '#C0C0C0',
            'Gold': '#FFD700', 'Platinum': '#E5E4E2'
        }
        return colors.get(self.level, '#CD7F32')


class UserProfile(models.Model):
    NETWORK_CHOICES = [('MTN', 'MTN'), ('Airtel', 'Airtel'), ('Glo', 'Glo'), ('9mobile', '9mobile')]
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    state = models.CharField(max_length=50, blank=True)
    preferred_network = models.CharField(max_length=10, choices=NETWORK_CHOICES, blank=True)
    airtime_phone = models.CharField(max_length=15, blank=True)

    total_points_earned = models.BigIntegerField(default=0)
    login_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_daily_login = models.DateField(null=True, blank=True)

    surveys_completed = models.IntegerField(default=0)
    quizzes_completed = models.IntegerField(default=0)
    games_completed = models.IntegerField(default=0)
    ads_watched_today = models.IntegerField(default=0)
    ads_watched_date = models.DateField(null=True, blank=True)
    total_airtime_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    email_notifications = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"

    def update_streak(self):
        today = timezone.now().date()
        if self.last_daily_login == today:
            return False
        if self.last_daily_login and (today - self.last_daily_login).days == 1:
            self.login_streak += 1
        else:
            self.login_streak = 1
        self.last_daily_login = today
        if self.login_streak > self.longest_streak:
            self.longest_streak = self.login_streak
        self.save()
        return True

    def can_watch_ad(self):
        today = timezone.now().date()
        if self.ads_watched_date != today:
            self.ads_watched_today = 0
            self.ads_watched_date = today
            self.save()
        return self.ads_watched_today < settings.DAILY_AD_LIMIT

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class OTPCode(models.Model):
    TYPE_CHOICES = [
        ('email_verify', 'Email Verification'),
        ('phone_verify', 'Phone Verification'),
        ('password_reset', 'Password Reset'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP {self.code} for {self.user.email}"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def generate(cls, user, otp_type):
        code = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timezone.timedelta(minutes=15)
        cls.objects.filter(user=user, otp_type=otp_type, is_used=False).update(is_used=True)
        return cls.objects.create(user=user, code=code, otp_type=otp_type, expires_at=expires_at)
