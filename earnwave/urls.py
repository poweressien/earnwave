from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('surveys/', include('surveys.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('games/', include('games.urls')),
    path('rewards/', include('rewards.urls')),
    path('referrals/', include('referrals.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'EarnWave Admin'
admin.site.site_title = 'EarnWave'
admin.site.index_title = 'Platform Management'

# Custom error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
