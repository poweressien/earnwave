"""
EarnWave Custom Admin Site
Full-featured admin dashboard with analytics
"""
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class EarnWaveAdminSite(AdminSite):
    site_header = 'EarnWave Platform Admin'
    site_title = 'EarnWave Admin'
    index_title = 'Platform Management'

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        return app_list

    def index(self, request, extra_context=None):
        """Custom admin index with analytics."""
        from accounts.models import User
        from rewards.models import PointTransaction, AirtimeRedemption, Notification
        from surveys.models import Survey, SurveyResponse
        from quizzes.models import QuizAttempt
        from referrals.models import ReferralRecord
        from django.utils import timezone
        from django.db.models import Sum, Count
        import datetime

        today = timezone.now().date()
        week_ago = today - datetime.timedelta(days=7)
        month_ago = today - datetime.timedelta(days=30)

        analytics = {
            # User stats
            'total_users': User.objects.count(),
            'new_users_today': User.objects.filter(date_joined__date=today).count(),
            'new_users_week': User.objects.filter(date_joined__date__gte=week_ago).count(),
            'active_users': User.objects.filter(is_active=True).count(),

            # Points stats
            'total_points_issued': PointTransaction.objects.filter(
                transaction_type='credit'
            ).aggregate(t=Sum('points'))['t'] or 0,
            'points_today': PointTransaction.objects.filter(
                transaction_type='credit', created_at__date=today
            ).aggregate(t=Sum('points'))['t'] or 0,

            # Redemptions
            'pending_redemptions': AirtimeRedemption.objects.filter(status='pending').count(),
            'total_airtime_paid': AirtimeRedemption.objects.filter(
                status='completed'
            ).aggregate(t=Sum('airtime_amount'))['t'] or 0,
            'redemptions_today': AirtimeRedemption.objects.filter(
                created_at__date=today
            ).count(),

            # Activity
            'surveys_completed': SurveyResponse.objects.filter(is_complete=True).count(),
            'quizzes_completed': QuizAttempt.objects.filter(is_complete=True).count(),
            'referrals_total': ReferralRecord.objects.count(),
            'referrals_rewarded': ReferralRecord.objects.filter(status='rewarded').count(),

            # Recent activity
            'recent_redemptions': AirtimeRedemption.objects.select_related('user').order_by('-created_at')[:10],
            'recent_users': User.objects.order_by('-date_joined')[:8],
            'pending_redemption_list': AirtimeRedemption.objects.filter(
                status='pending'
            ).select_related('user').order_by('-created_at')[:5],

            # Level distribution
            'level_bronze': 0, 'level_silver': 0, 'level_gold': 0, 'level_platinum': 0,
        }

        extra_context = extra_context or {}
        extra_context['analytics'] = analytics
        return super().index(request, extra_context)
