from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import *


@login_required
def index(request):
    context_dict = {}

    course = Course.objects.get(practice_start__year=date.today().year)
    if course:
        if course.practice_running():
            context_dict['days_left'] = (course.practice_end - date.today()).days
        elif date.today() < course.practice_start:
            context_dict['days_until'] = (course.practice_start - date.today()).days
        else:
            context_dict['days_after'] = (date.today() - course.practice_end).days

    return render(request, 'practicas/index.html', context_dict)
