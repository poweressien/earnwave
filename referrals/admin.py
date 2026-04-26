from django.contrib import admin
from .models import ReferralRecord

@admin.register(ReferralRecord)
class ReferralRecordAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred', 'status', 'inviter_points', 'fraud_score', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['referrer__email', 'referred__email']
    actions = ['flag_fraud']

    def flag_fraud(self, request, queryset):
        queryset.update(status='flagged')
    flag_fraud.short_description = 'Flag as Fraudulent'
