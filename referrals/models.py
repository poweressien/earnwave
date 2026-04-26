import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ReferralRecord(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('qualified', 'Qualified'), ('rewarded', 'Rewarded'), ('flagged', 'Flagged')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_referrals')
    referred = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_referral')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    inviter_bonus_paid = models.BooleanField(default=False)
    invitee_bonus_paid = models.BooleanField(default=False)
    inviter_points = models.IntegerField(default=0)
    invitee_points = models.IntegerField(default=0)
    qualified_at = models.DateTimeField(null=True, blank=True)
    rewarded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fraud_score = models.IntegerField(default=0)

    class Meta:
        unique_together = ['referrer', 'referred']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referrer.get_full_name()} -> {self.referred.get_full_name()}"

    def qualify_and_reward(self):
        if self.status != 'pending':
            return False
        from rewards.models import PointTransaction, Notification
        self.status = 'qualified'
        self.qualified_at = timezone.now()
        self.inviter_points = settings.REFERRAL_BONUS_INVITER
        self.invitee_points = settings.REFERRAL_BONUS_INVITEE
        PointTransaction.award_points(self.referrer, self.inviter_points, 'referral', f'Referral bonus: {self.referred.get_full_name()} joined', str(self.id))
        PointTransaction.award_points(self.referred, self.invitee_points, 'referral', f'Signup bonus from referral by {self.referrer.get_full_name()}', str(self.id))
        self.inviter_bonus_paid = True
        self.invitee_bonus_paid = True
        self.status = 'rewarded'
        self.rewarded_at = timezone.now()
        self.save()
        Notification.objects.create(user=self.referrer, title='Referral Bonus!', message=f'You earned {self.inviter_points} points for referring {self.referred.get_full_name()}!', notification_type='referral')
        return True
