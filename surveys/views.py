from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Survey, SurveyResponse, SurveyAnswer
from rewards.models import PointTransaction, Notification


@login_required
def survey_list(request):
    surveys = Survey.objects.filter(status='active')
    completed_ids = SurveyResponse.objects.filter(user=request.user, is_complete=True).values_list('survey_id', flat=True)
    return render(request, 'surveys/list.html', {'surveys': surveys, 'completed_ids': list(completed_ids)})


@login_required
def survey_detail(request, pk):
    survey = get_object_or_404(Survey, pk=pk, status='active')
    completed = SurveyResponse.objects.filter(user=request.user, survey=survey, is_complete=True).exists()
    if completed:
        messages.info(request, 'You have already completed this survey.')
        return redirect('surveys:list')
    response, _ = SurveyResponse.objects.get_or_create(user=request.user, survey=survey)
    questions = survey.questions.prefetch_related('options').all()
    if request.method == 'POST':
        for question in questions:
            if question.question_type == 'multiple_choice':
                option_id = request.POST.get(f'question_{question.id}')
                if option_id:
                    SurveyAnswer.objects.update_or_create(response=response, question=question, defaults={'selected_option_id': option_id})
            else:
                text = request.POST.get(f'question_{question.id}', '')
                if text:
                    SurveyAnswer.objects.update_or_create(response=response, question=question, defaults={'text_answer': text})
        response.is_complete = True
        response.completed_at = timezone.now()
        response.points_awarded = survey.points_reward
        response.save()
        survey.current_responses += 1
        survey.save()
        profile = request.user.profile
        profile.surveys_completed += 1
        profile.save()
        PointTransaction.award_points(request.user, survey.points_reward, 'survey', f'Completed survey: {survey.title}', str(survey.id))
        Notification.objects.create(user=request.user, title='Survey Completed! 🎉', message=f'You earned {survey.points_reward} points for completing "{survey.title}"', notification_type='points')
        messages.success(request, f'Survey complete! You earned {survey.points_reward} points!')
        return redirect('surveys:list')
    return render(request, 'surveys/detail.html', {'survey': survey, 'questions': questions, 'response': response})
