import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Quiz, QuizQuestion, QuizAttempt, QuizCategory, Leaderboard
from rewards.models import PointTransaction, Notification


@login_required
def quiz_list(request):
    categories = QuizCategory.objects.all()
    cat_slug = request.GET.get('category', '')
    quizzes = Quiz.objects.filter(is_active=True)
    if cat_slug:
        quizzes = quizzes.filter(category__slug=cat_slug)
    return render(request, 'quizzes/list.html', {'quizzes': quizzes, 'categories': categories, 'active_cat': cat_slug})


@login_required
def quiz_play(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
    questions = list(quiz.questions.all())
    attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, total_questions=len(questions))
    quiz.total_plays += 1
    quiz.save()
    return render(request, 'quizzes/play.html', {'quiz': quiz, 'questions': questions, 'attempt': attempt})


@login_required
def quiz_submit(request, attempt_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    if attempt.is_complete:
        return JsonResponse({'error': 'Already submitted'}, status=400)
    data = json.loads(request.body)
    answers = data.get('answers', {})
    questions = attempt.quiz.questions.all()
    correct = 0
    for q in questions:
        user_ans = answers.get(str(q.id), '').upper()
        if user_ans == q.correct_answer:
            correct += 1
    attempt.correct_answers = correct
    attempt.score = int((correct / len(questions)) * 100) if questions else 0
    time_taken = data.get('time_taken', 0)
    attempt.time_taken_seconds = time_taken
    pts = correct * attempt.quiz.points_per_correct
    if correct == len(questions):
        pts += attempt.quiz.bonus_points
    attempt.points_earned = pts
    attempt.is_complete = True
    attempt.completed_at = timezone.now()
    attempt.save()
    if pts > 0:
        PointTransaction.award_points(request.user, pts, 'quiz', f'Quiz: {attempt.quiz.title} ({correct}/{len(questions)} correct)', str(attempt.id))
        profile = request.user.profile
        profile.quizzes_completed += 1
        profile.save()
        Notification.objects.create(user=request.user, title='Quiz Complete!', message=f'You scored {attempt.score}% and earned {pts} points!', notification_type='points')
    return JsonResponse({'score': attempt.score, 'correct': correct, 'total': len(questions), 'points': pts})


@login_required
def leaderboard_view(request):
    weekly = Leaderboard.objects.filter(period='weekly').select_related('user')[:20]
    alltime = Leaderboard.objects.filter(period='alltime').select_related('user')[:20]
    return render(request, 'quizzes/leaderboard.html', {'weekly': weekly, 'alltime': alltime})
