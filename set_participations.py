import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd.settings')
django.setup()

from practicas.models import *


def set_participations(manager):
    # Set participation of students checked by tutors
    requests = Request.objects.filter(project__practices=manager.practice, checked=True).order_by('priority')
    for req in requests:
        part = Participation.objects.get_or_create(reg_student=req.reg_student)[0]

        if part.project:  # Skip already assigned participation
            continue

        part.project = req.project
        part.save()

    # Set other students participation
    reg_students = RegisteredStudent.objects.filter(practice=manager.practice) \
        .exclude(participation__project__isnull=False) \
        .order_by('?')
    for rs in reg_students:
        requests = Request.objects.filter(reg_student=rs).order_by('priority')
        for req in requests:
            part = Participation.objects.get_or_create(reg_student=rs)[0]
            if not part.project:
                part.project = req.project
                part.save()
                break
