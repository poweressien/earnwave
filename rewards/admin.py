from django.contrib import admin
from .models import PointTransaction, AirtimeRedemption, Badge, UserBadge, Notification


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'transaction_type', 'source', 'description', 'created_at']
    list_filter = ['transaction_type', 'source', 'created_at']
    search_fields = ['user__email', 'description']
    date_hierarchy = 'created_at'


@admin.register(AirtimeRedemption)
class AirtimeRedemptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'airtime_amount', 'network', 'phone_number', 'status', 'points_used', 'created_at']
    list_filter = ['status', 'network', 'created_at']
    search_fields = ['user__email', 'phone_number']
    actions = ['mark_completed', 'mark_failed']

    def mark_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', processed_at=timezone.now())
    mark_completed.short_description = 'Mark as Completed'

    def mark_failed(self, request, queryset):
        queryset.update(status='failed')
    mark_failed.short_description = 'Mark as Failed'


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'rarity', 'points_reward', 'condition_type', 'condition_value']
    list_filter = ['rarity']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    actions = ['mark_read']

    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
