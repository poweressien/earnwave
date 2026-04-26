"""
EarnWave Accounts Views — Full version with forgot password, profile, OTP
"""
import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings as django_settings
from .models import User, UserProfile, OTPCode
from .forms import SignupForm, LoginForm, ProfileUpdateForm
from rewards.models import PointTransaction, Notification


# ─── AUTH ────────────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            ref_code = form.cleaned_data.get('referral_code', '').strip().upper()
            if ref_code:
                try:
                    referrer = User.objects.get(referral_code=ref_code)
                    if referrer.email != user.email:
                        user.referred_by = referrer
                except User.DoesNotExist:
                    pass
            user.ip_address = get_client_ip(request)
            user.save()
            UserProfile.objects.get_or_create(user=user)
            PointTransaction.award_points(user, 50, 'signup_bonus', 'Welcome bonus for joining EarnWave!')
            Notification.objects.create(
                user=user, title='Welcome to EarnWave! 🎉',
                message='You earned 50 welcome points! Complete your first survey or quiz to earn more.',
                notification_type='system'
            )
            if user.referred_by:
                from referrals.models import ReferralRecord
                ref, created = ReferralRecord.objects.get_or_create(
                    referrer=user.referred_by, referred=user,
                    defaults={'ip_address': get_client_ip(request)}
                )
                if created:
                    ref.qualify_and_reward()
            login(request, user)
            messages.success(request, f'Welcome to EarnWave, {user.first_name}! 🎉 You have 50 bonus points.')
            return redirect('dashboard:home')
    else:
        ref_code = request.GET.get('ref', '')
        form = SignupForm(initial={'referral_code': ref_code})
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            try:
                streak_updated = user.profile.update_streak()
                if streak_updated:
                    bonus = min(user.profile.login_streak * 5, 50)
                    PointTransaction.award_points(
                        user, bonus, 'daily_login',
                        f'Daily login streak — Day {user.profile.login_streak}! 🔥'
                    )
            except Exception:
                pass
            messages.success(request, f'Welcome back, {user.first_name}! 👋')
            return redirect(request.GET.get('next', 'dashboard:home'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been signed out. Come back soon! 👋')
    return redirect('core:landing')


# ─── FORGOT PASSWORD ─────────────────────────────────────────────────────────

def forgot_password_view(request):
    """Step 1 — enter email, receive OTP."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
            otp = OTPCode.generate(user, 'password_reset')
            # Send email (prints to console in dev)
            try:
                send_mail(
                    subject='EarnWave — Password Reset OTP',
                    message=f'Hi {user.first_name},\n\nYour password reset code is: {otp.code}\n\nThis code expires in 15 minutes.\n\nIf you did not request this, ignore this email.\n\n— EarnWave Team',
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            # Store email in session for next step
            request.session['reset_email'] = email
            messages.success(request, f'OTP sent to {email}. Check your inbox (and spam).')
            return redirect('accounts:reset_password')
        except User.DoesNotExist:
            # Don't reveal whether email exists
            messages.success(request, f'If {email} is registered, you will receive an OTP shortly.')
            return redirect('accounts:reset_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request):
    """Step 2 — enter OTP."""
    if request.method == 'POST':
        email = request.session.get('reset_email', '')
        code = request.POST.get('code', '').strip()
        try:
            user = User.objects.get(email=email)
            otp = OTPCode.objects.filter(
                user=user, otp_type='password_reset', is_used=False
            ).order_by('-created_at').first()
            if otp and otp.is_valid() and otp.code == code:
                otp.is_used = True
                otp.save()
                request.session['reset_verified'] = True
                return redirect('accounts:reset_password_confirm')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'Session expired. Please start over.')
            return redirect('accounts:forgot_password')
    return render(request, 'accounts/reset_password_otp.html')


def reset_password_confirm_view(request):
    """Step 3 — set new password."""
    if not request.session.get('reset_verified'):
        return redirect('accounts:forgot_password')
    if request.method == 'POST':
        email = request.session.get('reset_email', '')
        pw1 = request.POST.get('password1', '')
        pw2 = request.POST.get('password2', '')
        if pw1 != pw2:
            messages.error(request, "Passwords don't match.")
            return render(request, 'accounts/reset_password_confirm.html')
        if len(pw1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'accounts/reset_password_confirm.html')
        try:
            user = User.objects.get(email=email)
            user.set_password(pw1)
            user.save()
            del request.session['reset_email']
            del request.session['reset_verified']
            messages.success(request, '✅ Password reset successful! Please sign in.')
            return redirect('accounts:login')
        except User.DoesNotExist:
            return redirect('accounts:forgot_password')
    return render(request, 'accounts/reset_password_confirm.html')


# ─── PROFILE / SETTINGS ──────────────────────────────────────────────────────

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    chart_data = _build_activity_chart(user)
    activity_stats = [
        ('Surveys Completed', '📋', profile.surveys_completed, 'var(--blue-light)'),
        ('Quizzes Completed', '🧠', profile.quizzes_completed, '#A78BFA'),
        ('Games Completed', '🎮', profile.games_completed, 'var(--success)'),
        ('Login Streak', '🔥', f'{profile.login_streak} days', 'var(--gold)'),
        ('Longest Streak', '⭐', f'{profile.longest_streak} days', 'var(--gold)'),
        ('Airtime Earned', '📱', f'₦{profile.total_airtime_earned}', 'var(--success)'),
    ]
    from rewards.models import Badge, UserBadge
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')
    total_badges = Badge.objects.count()
    return render(request, 'accounts/profile.html', {
        'form': form, 'profile': profile,
        'chart_data': json.dumps(chart_data),
        'activity_stats': activity_stats,
        'user_badges': user_badges,
        'total_badges': total_badges,
    })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_pw = request.POST.get('old_password', '')
        new_pw = request.POST.get('new_password', '')
        confirm_pw = request.POST.get('confirm_password', '')
        if not request.user.check_password(old_pw):
            messages.error(request, 'Current password is incorrect.')
        elif len(new_pw) < 8:
            messages.error(request, 'New password must be at least 8 characters.')
        elif new_pw != confirm_pw:
            messages.error(request, "New passwords don't match.")
        else:
            request.user.set_password(new_pw)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, '✅ Password changed successfully!')
            return redirect('accounts:profile')
    return render(request, 'accounts/change_password.html')


@login_required
def toggle_dark_mode(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    profile = request.user.profile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return JsonResponse({'dark_mode': profile.dark_mode})


@login_required
def notification_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _build_activity_chart(user):
    today = timezone.now().date()
    labels, values = [], []
    for i in range(6, -1, -1):
        end = today - datetime.timedelta(days=i * 5)
        start = end - datetime.timedelta(days=4)
        pts = PointTransaction.objects.filter(
            user=user, transaction_type='credit',
            created_at__date__gte=start, created_at__date__lte=end,
        ).aggregate(t=Sum('points'))['t'] or 0
        labels.append(start.strftime('%d %b'))
        values.append(pts)
    return {'labels': labels, 'values': values}


def get_client_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0].strip() if x else request.META.get('REMOTE_ADDR', '127.0.0.1')
