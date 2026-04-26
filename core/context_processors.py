from django.conf import settings
from rewards.models import Notification


def site_settings(request):
    return {
        'PLATFORM_NAME': settings.PLATFORM_NAME,
        'PLATFORM_TAGLINE': settings.PLATFORM_TAGLINE,
        'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY,
    }


def user_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}
