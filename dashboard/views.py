from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rewards.models import PointTransaction, AirtimeRedemption, Notification, Badge, UserBadge
from surveys.models import Survey, SurveyResponse
from quizzes.models import QuizAttempt, Leaderboard
from games.models import GameSession
from referrals.models import ReferralRecord


@login_required
def home(request):
    user = request.user
    profile = user.profile
    # Recent transactions
    recent_transactions = PointTransaction.objects.filter(user=user)[:5]
    # Pending redemptions
    pending_redemptions = AirtimeRedemption.objects.filter(user=user, status='pending').count()
    # Unread notifications
    unread_notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    # Active surveys
    available_surveys = Survey.objects.filter(status='active').exclude(responses__user=user).order_by('?')[:3]
    # Top leaderboard
    today = timezone.now().date()
    leaderboard = Leaderboard.objects.filter(period='weekly').select_related('user')[:5]
    # User badges
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')[:6]
    # Recent quiz attempts
    recent_quizzes = QuizAttempt.objects.filter(user=user, is_complete=True)[:3]
    # Referral stats
    referral_count = ReferralRecord.objects.filter(referrer=user).count()
    referral_earnings = ReferralRecord.objects.filter(referrer=user, status='rewarded').count() * 100
    # Calculate next level
    points = user.points_balance
    level_data = get_level_progress(points)
    context = {
        'profile': profile,
        'recent_transactions': recent_transactions,
        'pending_redemptions': pending_redemptions,
        'unread_notifications': unread_notifications,
        'available_surveys': available_surveys,
        'leaderboard': leaderboard,
        'user_badges': user_badges,
        'recent_quizzes': recent_quizzes,
        'referral_count': referral_count,
        'referral_earnings': referral_earnings,
        'level_data': level_data,
        'points': points,
    }
    return render(request, 'dashboard/home.html', context)


def get_level_progress(points):
    from django.conf import settings
    thresholds = settings.LEVEL_THRESHOLDS
    levels = list(thresholds.items())
    current_level = 'Bronze'
    next_level = None
    current_threshold = 0
    next_threshold = None
    for i, (level, threshold) in enumerate(levels):
        if points >= threshold:
            current_level = level
            current_threshold = threshold
            if i + 1 < len(levels):
                next_level = levels[i + 1][0]
                next_threshold = levels[i + 1][1]
    progress = 0
    if next_threshold:
        progress = min(100, int((points - current_threshold) / (next_threshold - current_threshold) * 100))
    return {
        'current': current_level,
        'next': next_level,
        'progress': progress,
        'points_to_next': (next_threshold - points) if next_threshold else 0,
    }


@login_required
def transactions(request):
    transactions = PointTransaction.objects.filter(user=request.user)
    return render(request, 'dashboard/transactions.html', {'transactions': transactions})


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'dashboard/notifications.html', {'notifications': notifs})
