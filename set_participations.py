import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd.settings')
django.setup()

from practicas.models import *


def set_participations(manager):
    projects = Project.objects.filter(practices=manager.practice)
    project_capacity = {proj: 0 for proj in projects}

    # Set participation of students checked by tutors
    requests = Request.objects.filter(project__practices=manager.practice, checked=True).order_by('priority')
    for req in requests:
        part = Participation.objects.get_or_create(reg_student=req.reg_student)[0]
        part.project = req.project
        part.save()

    # Set other students participation
    for proj in projects:
        requirements = Requirement.objects.filter(project=proj)
        for req in requirements:
            project_capacity[proj] += req.students_count
        project_capacity[proj] -= Participation.objects.filter(project=proj).count()

    reg_students = RegisteredStudent.objects.filter(practice=manager.practice).exclude(
        participation__project__isnull=False).order_by('?')
    for rs in reg_students:
        requests = Request.objects.filter(reg_student=rs).order_by('priority')
        for req in requests:
            if project_capacity[req.project] > 0:
                part = Participation.objects.get_or_create(reg_student=rs)[0]
                part.project = req.project
                part.save()
                project_capacity[req.project] -= 1
                break
