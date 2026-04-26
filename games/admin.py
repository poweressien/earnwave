from django.contrib import admin
from .models import Game, GameSession

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'game_type', 'difficulty', 'points_reward', 'is_active', 'total_plays']
    list_filter = ['game_type', 'difficulty', 'is_active']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'score', 'points_earned', 'is_complete', 'created_at']
    list_filter = ['is_complete', 'game__game_type']
