import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd.settings')
django.setup()

from practicas.models import *


def set_participations():
    course = Course.objects.get(start__lte=date.today(), end__gte=date.today())

    projects = Project.objects.filter(course=course)

    project_capacity = {proj: 0 for proj in projects}

    for proj in projects:
        requirements = Requirement.objects.filter(project=proj)
        for req in requirements:
            project_capacity[proj] += req.students_count

    reg_students = RegisteredStudent.objects.filter(course=course).order_by('?')
    for rs in reg_students:
        requests = Request.objects.filter(reg_student=rs, checked=True).order_by('priority')
        for req in requests:
            if project_capacity[req.project] > 0:
                part = Participation.objects.create(reg_student=rs, project=req.project)
                part.save()
                project_capacity[req.project] -= 1
                break


# Start execution here!
if __name__ == '__main__':
    print("Setting participations...")
    set_participations()
