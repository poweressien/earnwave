import uuid
from django.db import models
from django.conf import settings


class Survey(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('active', 'Active'), ('paused', 'Paused'), ('completed', 'Completed')]
    CATEGORY_CHOICES = [
        ('general', 'General'), ('consumer', 'Consumer Research'), ('health', 'Health'),
        ('finance', 'Finance'), ('tech', 'Technology'), ('lifestyle', 'Lifestyle'),
        ('education', 'Education'), ('politics', 'Politics'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    points_reward = models.IntegerField(default=50)
    estimated_minutes = models.IntegerField(default=5)
    max_responses = models.IntegerField(default=1000)
    current_responses = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_sponsored = models.BooleanField(default=False)
    sponsor_name = models.CharField(max_length=100, blank=True)
    sponsor_logo = models.ImageField(upload_to='sponsors/', blank=True, null=True)
    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)
    gender_filter = models.CharField(max_length=5, blank=True)
    state_filter = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_available(self):
        from django.utils import timezone
        return (self.status == 'active' and
                self.current_responses < self.max_responses and
                (self.expires_at is None or timezone.now() < self.expires_at))


class SurveyQuestion(models.Model):
    TYPE_CHOICES = [('multiple_choice', 'Multiple Choice'), ('text', 'Text'), ('rating', 'Rating'), ('boolean', 'Yes/No')]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice')
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.survey.title} - Q{self.order}"


class SurveyOption(models.Model):
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey_responses')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    is_complete = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'survey']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.survey.title}"


class SurveyAnswer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(SurveyOption, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
