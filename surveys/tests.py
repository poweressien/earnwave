"""
EarnWave Surveys Test Suite
"""
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, UserProfile
from rewards.models import PointTransaction
from .models import Survey, SurveyQuestion, SurveyOption, SurveyResponse


def make_user(email='survey_user@test.ng'):
    user = User.objects.create_user(
        email=email, password='TestPass@123',
        first_name='Survey', last_name='Tester'
    )
    UserProfile.objects.get_or_create(user=user)
    return user


def make_survey(title='Test Survey', points=50, status='active'):
    return Survey.objects.create(
        title=title, description='A test survey',
        category='general', points_reward=points,
        estimated_minutes=3, max_responses=100, status=status
    )


class SurveyModelTest(TestCase):
    def test_survey_availability(self):
        s = make_survey()
        self.assertTrue(s.is_available())

    def test_paused_survey_not_available(self):
        s = make_survey(status='paused')
        self.assertFalse(s.is_available())

    def test_full_survey_not_available(self):
        s = Survey.objects.create(
            title='Full', description='Full survey',
            category='general', points_reward=50,
            max_responses=5, current_responses=5, status='active'
        )
        self.assertFalse(s.is_available())

    def test_survey_str(self):
        s = make_survey('My Survey')
        self.assertEqual(str(s), 'My Survey')


class SurveyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.client.login(username='survey_user@test.ng', password='TestPass@123')
        self.survey = make_survey()

        q = SurveyQuestion.objects.create(
            survey=self.survey, text='What is your age group?',
            question_type='multiple_choice', order=1
        )
        SurveyOption.objects.create(question=q, text='18-25', order=1)
        SurveyOption.objects.create(question=q, text='26-35', order=2)

    def test_survey_list_view(self):
        response = self.client.get(reverse('surveys:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Survey')

    def test_survey_detail_view(self):
        response = self.client.get(reverse('surveys:detail', args=[self.survey.pk]))
        self.assertEqual(response.status_code, 200)

    def test_survey_completion_awards_points(self):
        q = self.survey.questions.first()
        opt = q.options.first()
        response = self.client.post(
            reverse('surveys:detail', args=[self.survey.pk]),
            {f'question_{q.id}': str(opt.id)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            SurveyResponse.objects.filter(user=self.user, is_complete=True).count(), 1
        )
        self.assertEqual(self.user.points_balance, 50)

    def test_cannot_complete_survey_twice(self):
        q = self.survey.questions.first()
        opt = q.options.first()
        self.client.post(
            reverse('surveys:detail', args=[self.survey.pk]),
            {f'question_{q.id}': str(opt.id)}
        )
        # Second attempt
        response = self.client.post(
            reverse('surveys:detail', args=[self.survey.pk]),
            {f'question_{q.id}': str(opt.id)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            SurveyResponse.objects.filter(user=self.user, is_complete=True).count(), 1
        )

    def test_inactive_survey_inaccessible(self):
        s = make_survey(status='paused')
        response = self.client.get(reverse('surveys:detail', args=[s.pk]))
        self.assertEqual(response.status_code, 404)

    def test_survey_response_increments_counter(self):
        q = self.survey.questions.first()
        opt = q.options.first()
        before = self.survey.current_responses
        self.client.post(
            reverse('surveys:detail', args=[self.survey.pk]),
            {f'question_{q.id}': str(opt.id)}
        )
        self.survey.refresh_from_db()
        self.assertEqual(self.survey.current_responses, before + 1)

    def test_unauthenticated_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('surveys:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
