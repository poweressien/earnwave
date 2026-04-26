from django.contrib import admin
from .models import Survey, SurveyQuestion, SurveyOption, SurveyResponse


class SurveyOptionInline(admin.TabularInline):
    model = SurveyOption
    extra = 2


class SurveyQuestionInline(admin.StackedInline):
    model = SurveyQuestion
    extra = 1


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'points_reward', 'status', 'current_responses', 'max_responses', 'is_sponsored']
    list_filter = ['status', 'category', 'is_sponsored']
    search_fields = ['title', 'sponsor_name']
    inlines = [SurveyQuestionInline]

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['user', 'survey', 'is_complete', 'points_awarded', 'completed_at']
    list_filter = ['is_complete']
