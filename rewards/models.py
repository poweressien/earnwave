import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class PointTransaction(models.Model):
    TYPE_CHOICES = [('credit', 'Credit'), ('debit', 'Debit')]
    SOURCE_CHOICES = [
        ('survey', 'Survey'), ('quiz', 'Quiz'), ('game', 'Game'),
        ('ad_watch', 'Ad Watch'), ('referral', 'Referral'), ('daily_login', 'Daily Login'),
        ('streak_bonus', 'Streak Bonus'), ('task', 'Task'), ('redemption', 'Redemption'),
        ('admin', 'Admin'), ('signup_bonus', 'Signup Bonus'), ('spin_wheel', 'Spin Wheel'),
        ('daily_challenge', 'Daily Challenge'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_transactions')
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.CharField(max_length=200)
    reference_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} {self.points}pts — {self.user.get_full_name()}"

    @classmethod
    def award_points(cls, user, points, source, description, reference_id=''):
        tx = cls.objects.create(
            user=user, points=points, transaction_type='credit',
            source=source, description=description, reference_id=reference_id
        )
        profile = user.profile
        profile.total_points_earned += points
        profile.save(update_fields=['total_points_earned'])
        return tx

    @classmethod
    def deduct_points(cls, user, points, source, description, reference_id=''):
        if user.points_balance < points:
            raise ValueError('Insufficient points balance')
        return cls.objects.create(
            user=user, points=points, transaction_type='debit',
            source=source, description=description, reference_id=reference_id
        )


class AirtimeRedemption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('processing', 'Processing'),
        ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')
    ]
    NETWORK_CHOICES = [('MTN', 'MTN'), ('Airtel', 'Airtel'), ('Glo', 'Glo'), ('9mobile', '9mobile')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    points_used = models.IntegerField()
    airtime_amount = models.DecimalField(max_digits=8, decimal_places=2)
    network = models.CharField(max_length=10, choices=NETWORK_CHOICES)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paystack_reference = models.CharField(max_length=100, blank=True)
    admin_note = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Redemption ₦{self.airtime_amount} — {self.user.get_full_name()}"


class Badge(models.Model):
    RARITY_CHOICES = [('common', 'Common'), ('rare', 'Rare'), ('epic', 'Epic'), ('legendary', 'Legendary')]
    name = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='award')
    rarity = models.CharField(max_length=10, choices=RARITY_CHOICES, default='common')
    points_reward = models.IntegerField(default=0)
    condition_type = models.CharField(max_length=50)
    condition_value = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']


class Notification(models.Model):
    TYPE_CHOICES = [
        ('points', 'Points'), ('redemption', 'Redemption'), ('badge', 'Badge'),
        ('referral', 'Referral'), ('system', 'System'), ('challenge', 'Challenge'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class DailyChallenge(models.Model):
    CHALLENGE_TYPES = [
        ('survey', 'Complete a Survey'), ('quiz', 'Complete a Quiz'),
        ('game', 'Play a Game'), ('streak', 'Maintain Streak'),
        ('referral', 'Refer a Friend'), ('ad', 'Watch Ads'),
    ]
    title = models.CharField(max_length=120)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    target = models.IntegerField(default=1)
    points_reward = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.date})"


class UserDailyChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_challenges')
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'challenge']


    @property
    def progress_pct(self):
        if self.challenge.target == 0:
            return 0
        return min(100, int((self.progress / self.challenge.target) * 100))

    @property
    def current_count(self):
        return self.progress


class SpinHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spins')
    points_won = models.IntegerField(default=0)
    label = models.CharField(max_length=50)
    spun_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-spun_at']
