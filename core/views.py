from django.shortcuts import render
from surveys.models import Survey
from quizzes.models import Quiz, Leaderboard
from accounts.models import User


def landing(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard:home')
    stats = {
        'users': User.objects.filter(is_active=True).count(),
        'surveys': Survey.objects.filter(status='active').count(),
        'quizzes': Quiz.objects.filter(is_active=True).count(),
    }
    return render(request, 'core/landing.html', {'stats': stats})


def how_it_works(request):
    return render(request, 'core/how_it_works.html')


def about(request):
    return render(request, 'core/about.html')


def faq(request):
    return render(request, 'core/faq.html')


def contact(request):
    return render(request, 'core/contact.html')


def privacy(request):
    return render(request, 'core/privacy.html')


def terms(request):
    return render(request, 'core/terms.html')


def handler404(request, exception=None):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
