from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json
from .models import Game, GameSession
from rewards.models import PointTransaction, Notification


@login_required
def games_list(request):
    games = Game.objects.filter(is_active=True)
    return render(request, 'games/list.html', {'games': games})


@login_required
def game_play(request, pk):
    game = get_object_or_404(Game, pk=pk, is_active=True)
    session = GameSession.objects.create(user=request.user, game=game)
    game.total_plays += 1
    game.save()
    return render(request, f'games/play_{game.game_type}.html', {'game': game, 'session': session})


@login_required
def game_complete(request, session_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    session = get_object_or_404(GameSession, pk=session_id, user=request.user)
    if session.is_complete:
        return JsonResponse({'error': 'Already completed'}, status=400)
    data = json.loads(request.body)
    session.score = data.get('score', 0)
    session.level_reached = data.get('level', 1)
    session.time_taken_seconds = data.get('time_taken', 0)
    session.is_complete = True
    session.completed_at = timezone.now()
    pts = session.game.points_reward if data.get('won', False) else session.game.points_reward // 2
    session.points_earned = pts
    session.save()
    profile = request.user.profile
    profile.games_completed += 1
    profile.save()
    PointTransaction.award_points(request.user, pts, 'game', f'Game: {session.game.title} - Score: {session.score}', str(session.id))
    return JsonResponse({'points': pts, 'score': session.score})
