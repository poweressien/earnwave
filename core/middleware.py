from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone


class AntiAbuseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        if request.path.startswith('/api/') or request.path.startswith('/rewards/watch-ad/'):
            cache_key = f'rate_limit_{ip}'
            requests = cache.get(cache_key, 0)
            if requests > 60:
                return JsonResponse({'error': 'Rate limit exceeded. Please slow down.'}, status=429)
            cache.set(cache_key, requests + 1, 60)
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0]
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
