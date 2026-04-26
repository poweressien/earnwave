from django.contrib import admin
from .models import Quiz, QuizQuestion, QuizCategory, QuizAttempt, Leaderboard


class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 1


@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'points_per_correct', 'is_daily', 'is_active', 'total_plays']
    list_filter = ['category', 'difficulty', 'is_daily', 'is_active']
    search_fields = ['title']
    inlines = [QuizQuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'correct_answers', 'points_earned', 'is_complete', 'created_at']
    list_filter = ['is_complete', 'quiz__category']
