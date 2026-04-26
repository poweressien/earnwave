"""
EarnWave Rewards Views — Points, airtime, ads, spin wheel, daily challenges
"""
import json
import hmac
import hashlib
import random
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import (
    PointTransaction, AirtimeRedemption, Notification, Badge, UserBadge,
    DailyChallenge, UserDailyChallenge, SpinHistory
)

logger = logging.getLogger(__name__)

# ─── SPIN WHEEL CONFIG ───────────────────────────────────────────────────────
SPIN_SEGMENTS = [
    {'label': '10 Points',   'points': 10,  'color': '#2563EB', 'weight': 30},
    {'label': '25 Points',   'points': 25,  'color': '#7C3AED', 'weight': 25},
    {'label': '50 Points',   'points': 50,  'color': '#10B981', 'weight': 20},
    {'label': '5 Points',    'points': 5,   'color': '#374151', 'weight': 15},
    {'label': '100 Points',  'points': 100, 'color': '#F59E0B', 'weight': 7},
    {'label': '75 Points',   'points': 75,  'color': '#EF4444', 'weight': 10},
    {'label': '200 Points',  'points': 200, 'color': '#EC4899', 'weight': 3},
    {'label': 'Try Again',   'points': 0,   'color': '#1F2937', 'weight': 10},
]


# ─── MAIN REWARDS HOME ───────────────────────────────────────────────────────

@login_required
def rewards_home(request):
    user = request.user
    profile = user.profile
    points = user.points_balance
    redemptions = AirtimeRedemption.objects.filter(user=user)[:10]
    transactions = PointTransaction.objects.filter(user=user)[:15]
    badges = UserBadge.objects.filter(user=user).select_related('badge')
    total_earned = PointTransaction.objects.filter(
        user=user, transaction_type='credit'
    ).aggregate(t=__import__('django.db.models', fromlist=['Sum']).Sum('points'))['t'] or 0

    # Today's challenges
    today = timezone.now().date()
    today_challenges = DailyChallenge.objects.filter(is_active=True, date=today)
    user_challenges = {
        uc.challenge_id: uc
        for uc in UserDailyChallenge.objects.filter(user=user, challenge__date=today)
    }

    # Spin eligibility: once per day
    last_spin = SpinHistory.objects.filter(user=user).first()
    can_spin = not last_spin or last_spin.spun_at.date() < today

    return render(request, 'rewards/home.html', {
        'points': points,
        'redemptions': redemptions,
        'transactions': transactions,
        'profile': profile,
        'badges': badges,
        'total_earned': total_earned,
        'ad_points': settings.AD_WATCH_POINTS,
        'min_redemption': settings.MIN_REDEMPTION_POINTS,
        'points_per_naira': settings.POINTS_PER_NAIRA,
        'today_challenges': today_challenges,
        'user_challenges': user_challenges,
        'can_spin': can_spin,
        'spin_segments': SPIN_SEGMENTS,
        'recent_spins': SpinHistory.objects.filter(user=user)[:5],
    })


# ─── REDEEM AIRTIME ──────────────────────────────────────────────────────────

@login_required
@require_POST
def redeem_airtime(request):
    network = request.POST.get('network', '').strip()
    phone = request.POST.get('phone_number', '').strip()
    amount_str = request.POST.get('amount', '0').strip()
    if not network or not phone:
        messages.error(request, 'Please fill in all fields.')
        return redirect('rewards:home')
    try:
        amount = int(amount_str)
        if amount < 10:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, 'Enter a valid amount (minimum ₦10).')
        return redirect('rewards:home')

    points_needed = amount * settings.POINTS_PER_NAIRA
    if points_needed < settings.MIN_REDEMPTION_POINTS:
        messages.error(request, f'Minimum redemption is {settings.MIN_REDEMPTION_POINTS:,} pts (₦{settings.MIN_REDEMPTION_POINTS // settings.POINTS_PER_NAIRA}).')
        return redirect('rewards:home')
    if request.user.points_balance < points_needed:
        messages.error(request, f'Insufficient points. You need {points_needed:,} pts — you have {request.user.points_balance:,} pts.')
        return redirect('rewards:home')
    pending = AirtimeRedemption.objects.filter(user=request.user, status='pending').count()
    if pending >= 3:
        messages.error(request, 'You have 3 pending redemptions. Wait for them to process first.')
        return redirect('rewards:home')
    try:
        PointTransaction.deduct_points(request.user, points_needed, 'redemption', f'Airtime redemption: ₦{amount} {network} to {phone}')
        redemption = AirtimeRedemption.objects.create(
            user=request.user, points_used=points_needed, airtime_amount=amount,
            network=network, phone_number=phone,
        )
        profile = request.user.profile
        profile.total_airtime_earned += amount
        profile.save(update_fields=['total_airtime_earned'])
        Notification.objects.create(
            user=request.user, title='Redemption Submitted! 📱',
            message=f'Your request for ₦{amount} {network} airtime to {phone} is being processed.',
            notification_type='redemption', link='/rewards/'
        )
        if not settings.DEBUG and settings.PAYSTACK_SECRET_KEY != 'sk_test_your_key':
            try:
                from core.paystack import paystack
                paystack.process_redemption(redemption)
            except Exception as e:
                logger.error(f'Paystack error: {e}')
        messages.success(request, f'✅ ₦{amount} {network} airtime to {phone} is being processed within 24 hours.')
        check_and_award_badges(request.user)
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('rewards:home')


# ─── WATCH AD ────────────────────────────────────────────────────────────────

@login_required
@require_POST
def watch_ad(request):
    profile = request.user.profile
    if not profile.can_watch_ad():
        return JsonResponse({'success': False, 'error': f'Daily limit ({settings.DAILY_AD_LIMIT} ads) reached. Come back tomorrow!', 'limit_reached': True})
    profile.ads_watched_today += 1
    profile.save(update_fields=['ads_watched_today', 'ads_watched_date'])
    pts = settings.AD_WATCH_POINTS
    PointTransaction.award_points(request.user, pts, 'ad_watch', f'Ad watch #{profile.ads_watched_today} — daily bonus')
    remaining = settings.DAILY_AD_LIMIT - profile.ads_watched_today
    return JsonResponse({'success': True, 'points': pts, 'remaining': remaining, 'total_watched': profile.ads_watched_today})


# ─── SPIN WHEEL ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def spin_wheel(request):
    today = timezone.now().date()
    last_spin = SpinHistory.objects.filter(user=request.user).first()
    if last_spin and last_spin.spun_at.date() >= today:
        return JsonResponse({'success': False, 'error': 'You already spun today! Come back tomorrow.', 'next_spin': 'tomorrow'})

    # Weighted random selection
    total_weight = sum(s['weight'] for s in SPIN_SEGMENTS)
    r = random.uniform(0, total_weight)
    cumulative = 0
    result = SPIN_SEGMENTS[0]
    for i, seg in enumerate(SPIN_SEGMENTS):
        cumulative += seg['weight']
        if r <= cumulative:
            result = seg
            segment_index = i
            break

    SpinHistory.objects.create(user=request.user, points_won=result['points'], label=result['label'])

    if result['points'] > 0:
        PointTransaction.award_points(request.user, result['points'], 'spin_wheel', f'Spin wheel reward: {result["label"]}')
        Notification.objects.create(
            user=request.user, title='Spin Wheel Win! 🎡',
            message=f'You won {result["points"]} points from the daily spin!',
            notification_type='points'
        )

    return JsonResponse({
        'success': True,
        'segment_index': segment_index,
        'points': result['points'],
        'label': result['label'],
        'new_balance': request.user.points_balance,
    })


# ─── DAILY CHALLENGES ────────────────────────────────────────────────────────

@login_required
def daily_challenge(request):
    today = timezone.now().date()
    challenges = DailyChallenge.objects.filter(is_active=True, date=today)
    if not challenges.exists():
        # Auto-create today's challenges if none exist
        default_challenges = [
            {'title': 'Survey Warrior', 'description': 'Complete 1 survey today', 'challenge_type': 'survey', 'target': 1, 'points_reward': 75},
            {'title': 'Quiz Ace', 'description': 'Complete 2 quizzes today', 'challenge_type': 'quiz', 'target': 2, 'points_reward': 60},
            {'title': 'Ad Watcher', 'description': 'Watch 3 ads today', 'challenge_type': 'ad', 'target': 3, 'points_reward': 40},
        ]
        for c in default_challenges:
            DailyChallenge.objects.create(date=today, **c)
        challenges = DailyChallenge.objects.filter(is_active=True, date=today)

    user_challenges = {
        uc.challenge_id: uc
        for uc in UserDailyChallenge.objects.filter(user=request.user, challenge__date=today)
    }
    return render(request, 'rewards/daily_challenge.html', {
        'challenges': challenges, 'user_challenges': user_challenges,
        'today': today,
    })


# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


# ─── PAYSTACK WEBHOOK ────────────────────────────────────────────────────────

@csrf_exempt
def paystack_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    sig = request.headers.get('X-Paystack-Signature', '')
    secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
    computed = hmac.new(secret, request.body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(computed, sig):
        return HttpResponse(status=400)
    try:
        payload = json.loads(request.body)
        if payload.get('event') == 'charge.success':
            ref = payload['data'].get('reference', '')
            r = AirtimeRedemption.objects.filter(paystack_reference=ref).first()
            if r:
                r.status = 'completed'
                r.processed_at = timezone.now()
                r.save()
                Notification.objects.create(
                    user=r.user, title='Airtime Delivered! 🎉',
                    message=f'₦{r.airtime_amount} {r.network} sent to {r.phone_number}.',
                    notification_type='redemption',
                )
    except Exception as e:
        logger.error(f'Webhook error: {e}')
    return HttpResponse(status=200)


# ─── BADGE CHECKER ───────────────────────────────────────────────────────────

def check_and_award_badges(user):
    try:
        profile = user.profile
        badges = Badge.objects.exclude(id__in=UserBadge.objects.filter(user=user).values('badge_id'))
        for badge in badges:
            earned = False
            ct, cv = badge.condition_type, badge.condition_value
            if ct == 'surveys_completed' and profile.surveys_completed >= cv: earned = True
            elif ct == 'quizzes_completed' and profile.quizzes_completed >= cv: earned = True
            elif ct == 'games_completed' and profile.games_completed >= cv: earned = True
            elif ct == 'login_streak' and profile.login_streak >= cv: earned = True
            elif ct == 'total_points' and profile.total_points_earned >= cv: earned = True
            elif ct == 'referrals':
                from referrals.models import ReferralRecord
                if ReferralRecord.objects.filter(referrer=user, status='rewarded').count() >= cv:
                    earned = True
            if earned:
                UserBadge.objects.create(user=user, badge=badge)
                if badge.points_reward > 0:
                    PointTransaction.award_points(user, badge.points_reward, 'admin', f'Badge earned: {badge.name}')
                Notification.objects.create(
                    user=user, title=f'🏅 Badge Unlocked: {badge.name}!',
                    message=f'You earned "{badge.name}" ({badge.get_rarity_display()}). +{badge.points_reward} bonus pts!',
                    notification_type='badge',
                )
    except Exception as e:
        logger.error(f'Badge check error: {e}')


# ─── SPIN WHEEL PAGE (GET) ────────────────────────────────────────────────────
import json as _json, random as _random
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET"])
def spin_page(request):
    from .models import SpinHistory, SPIN_SEGMENTS
    today = timezone.now().date()
    last_spin = SpinHistory.objects.filter(user=request.user).first()
    already_spun = last_spin and last_spin.spun_at.date() >= today
    spin_history = SpinHistory.objects.filter(user=request.user)[:10]
    return render(request, 'rewards/spin.html', {
        'already_spun': already_spun,
        'last_spin': last_spin if already_spun else None,
        'segments': SPIN_SEGMENTS,
        'segments_json': _json.dumps(SPIN_SEGMENTS),
        'spin_history': spin_history,
    })
