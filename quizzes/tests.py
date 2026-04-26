"""
EarnWave Quizzes Test Suite
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, UserProfile
from rewards.models import PointTransaction
from .models import Quiz, QuizQuestion, QuizAttempt, QuizCategory


def make_user(email='quiz_user@test.ng'):
    user = User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Quiz', last_name='Tester'
    )
    UserProfile.objects.get_or_create(user=user)
    return user


def make_quiz():
    cat = QuizCategory.objects.create(
        name='General', slug='general', icon='book', color='#2563EB'
    )
    quiz = Quiz.objects.create(
        title='Test Quiz', category=cat, difficulty='easy',
        description='A test quiz', time_limit_seconds=30,
        points_per_correct=10, bonus_points=20
    )
    QuizQuestion.objects.create(
        quiz=quiz, text='What is 2+2?',
        option_a='3', option_b='4', option_c='5', option_d='6',
        correct_answer='B', order=1
    )
    QuizQuestion.objects.create(
        quiz=quiz, text='What color is the sky?',
        option_a='Green', option_b='Red', option_c='Blue', option_d='Yellow',
        correct_answer='C', order=2
    )
    return quiz


class QuizModelTest(TestCase):
    def test_quiz_creation(self):
        quiz = make_quiz()
        self.assertEqual(quiz.title, 'Test Quiz')
        self.assertEqual(quiz.questions.count(), 2)

    def test_attempt_score_percentage(self):
        quiz = make_quiz()
        user = make_user()
        attempt = QuizAttempt.objects.create(
            user=user, quiz=quiz, total_questions=2,
            correct_answers=1, is_complete=True
        )
        self.assertEqual(attempt.score_percentage, 50)

    def test_perfect_score_percentage(self):
        quiz = make_quiz()
        user = make_user()
        attempt = QuizAttempt.objects.create(
            user=user, quiz=quiz, total_questions=4,
            correct_answers=4, is_complete=True
        )
        self.assertEqual(attempt.score_percentage, 100)


class QuizViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.client.login(username='quiz_user@test.ng', password='TestPass@123')
        self.quiz = make_quiz()

    def test_quiz_list_view(self):
        response = self.client.get(reverse('quizzes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Quiz')

    def test_quiz_play_creates_attempt(self):
        self.client.get(reverse('quizzes:play', args=[self.quiz.pk]))
        self.assertEqual(QuizAttempt.objects.filter(user=self.user).count(), 1)

    def test_quiz_submit_all_correct(self):
        self.client.get(reverse('quizzes:play', args=[self.quiz.pk]))
        attempt = QuizAttempt.objects.filter(user=self.user).first()
        questions = self.quiz.questions.all()

        answers = {}
        for q in questions:
            answers[str(q.id)] = q.correct_answer

        response = self.client.post(
            reverse('quizzes:submit', args=[attempt.id]),
            data=json.dumps({'answers': answers, 'time_taken': 15}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['correct'], 2)
        self.assertEqual(data['score'], 100)
        self.assertEqual(data['points'], 40)  # 2×10 + 20 bonus

    def test_quiz_submit_no_correct(self):
        self.client.get(reverse('quizzes:play', args=[self.quiz.pk]))
        attempt = QuizAttempt.objects.filter(user=self.user).first()

        response = self.client.post(
            reverse('quizzes:submit', args=[attempt.id]),
            data=json.dumps({'answers': {}, 'time_taken': 5}),
            content_type='application/json'
        )
        data = response.json()
        self.assertEqual(data['correct'], 0)
        self.assertEqual(data['points'], 0)

    def test_quiz_increments_play_count(self):
        before = self.quiz.total_plays
        self.client.get(reverse('quizzes:play', args=[self.quiz.pk]))
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.total_plays, before + 1)

    def test_leaderboard_view(self):
        response = self.client.get(reverse('quizzes:leaderboard'))
        self.assertEqual(response.status_code, 200)

    def test_cannot_submit_twice(self):
        self.client.get(reverse('quizzes:play', args=[self.quiz.pk]))
        attempt = QuizAttempt.objects.filter(user=self.user).first()

        payload = json.dumps({'answers': {}, 'time_taken': 5})
        self.client.post(
            reverse('quizzes:submit', args=[attempt.id]),
            data=payload, content_type='application/json'
        )
        response = self.client.post(
            reverse('quizzes:submit', args=[attempt.id]),
            data=payload, content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
