from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ReferralRecord
from django.conf import settings


@login_required
def referral_home(request):
    user = request.user
    referrals = ReferralRecord.objects.filter(referrer=user).select_related('referred')
    total_earned = sum(r.inviter_points for r in referrals if r.inviter_bonus_paid)
    referral_url = request.build_absolute_uri(f'/accounts/signup/?ref={user.referral_code}')
    return render(request, 'referrals/home.html', {
        'referrals': referrals,
        'total_earned': total_earned,
        'referral_url': referral_url,
        'inviter_bonus': settings.REFERRAL_BONUS_INVITER,
        'invitee_bonus': settings.REFERRAL_BONUS_INVITEE,
    })
