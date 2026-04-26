from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'is_verified', 'is_active', 'date_joined', 'points_balance', 'level']
    list_filter = ['is_active', 'is_verified', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'referral_code']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'phone_number', 'username')}),
        ('Referral', {'fields': ('referral_code', 'referred_by')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_verified', 'is_locked', 'login_attempts')}),
        ('Permissions', {'fields': ('is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}),
    )
    readonly_fields = ['date_joined', 'referral_code']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_streak', 'total_points_earned', 'surveys_completed', 'quizzes_completed']
    search_fields = ['user__email', 'user__first_name']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'otp_type', 'is_used', 'expires_at', 'created_at']
    list_filter = ['otp_type', 'is_used']
