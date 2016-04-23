import os
from datetime import datetime

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd.settings')
django.setup()

from practicas.models import *


def populate():
    c14_15 = add_course(start=datetime(2014, 9, 1),
                        end=datetime(2015, 7, 17),
                        practice_start=datetime(2015, 6, 29),
                        practice_end=datetime(2015, 7, 17))

    c15_16 = add_course(start=datetime(2015, 9, 1),
                        end=datetime(2016, 7, 22),
                        practice_start=datetime(2016, 7, 3),
                        practice_end=datetime(2016, 7, 22))

    cs = add_major(name='Ciencia de la Computación',
                   years='5')

    math = add_major(name='Matemática',
                     years='4')

    matcom = add_workplace(address='Universidad de La Habana. San Lázaro y L. Municipio Plaza de la Revolución',
                           name='MATCOM')

    eddy = add_user(username='eddy',
                    first_name='Eddy',
                    last_name='Almuiña',
                    email='e.almuina@lab.matcom.uh.cu',
                    password='1234')

    miguel = add_user(username='miguel',
                      first_name='Miguel',
                      last_name='Pérez',
                      email='m.perez@lab.matcom.uh.cu',
                      password='1234')

    jose = add_user(username='jose',
                    first_name='José',
                    last_name='Martínez',
                    email='j.martinez@lab.matcom.uh.cu',
                    password='1234')

    oscar = add_user(username='oscar_luis',
                     first_name='Oscar Luis',
                     last_name='Vera',
                     email='oscar@matcom.uh.cu',
                     password='1234')

    somoza = add_user(username='somoza',
                      first_name='Alfredo',
                      last_name='Somoza',
                      email='somoza@matcom.uh.cu',
                      password='1234')

    eddy = add_student(eddy)
    miguel = add_student(miguel)
    jose = add_student(jose)

    add_registered_student(student=eddy,
                           course=c15_16,
                           major=cs,
                           year=3,
                           group='C312')

    add_registered_student(student=miguel,
                           course=c15_16,
                           major=cs,
                           year=3,
                           group='C312')

    add_registered_student(student=jose,
                           course=c15_16,
                           major=cs,
                           year=3,
                           group='C312')

    eddy = add_registered_student(student=eddy,
                                  course=c14_15,
                                  major=cs,
                                  year=2,
                                  group='C213')

    miguel = add_registered_student(student=miguel,
                                    course=c14_15,
                                    major=cs,
                                    year=2,
                                    group='C213')

    jose = add_registered_student(student=jose,
                                  course=c14_15,
                                  major=cs,
                                  year=2,
                                  group='C213')

    oscar = add_tutor(user=oscar,
                      workplace=matcom,
                      category='MSC',
                      job='Vicedecano')

    somoza = add_tutor(user=somoza,
                       workplace=matcom,
                       category='MSC',
                       job='Profesor')

    scrapping = add_project(course=c14_15,
                            tutor=oscar,
                            name='Scrapping',
                            description='Implementación de un sistema de búsqueda de bibliografía digital.')

    strings = add_project(course=c14_15,
                          tutor=somoza,
                          name='Strings',
                          description='Investigación sobre algoritmos de manipulación de cadenas de caracteres.')

    add_requirement(project=strings,
                    major=cs,
                    year=2,
                    students_count=2)

    add_requirement(project=scrapping,
                    major=cs,
                    year=2,
                    students_count=3)

    add_request(reg_student=eddy,
                project=strings,
                priority=0)

    add_request(reg_student=miguel,
                project=strings,
                priority=0)

    add_request(reg_student=jose,
                project=scrapping,
                priority=0)

    add_participation(reg_student=eddy,
                      project=strings,
                      grade=5)

    add_participation(reg_student=miguel,
                      project=strings,
                      grade=5)

    add_participation(reg_student=jose,
                      project=scrapping,
                      grade=4)


def add_user(username, first_name, last_name, email, password):
    u = User.objects.get_or_create(username=username)[0]
    u.first_name = first_name
    u.last_name = last_name
    u.email = email
    u.set_password(password)
    u.save()
    return u


def add_student(user):
    s = Student.objects.get_or_create(user=user)[0]
    s.save()
    return s


def add_major(name, years):
    m = Major.objects.get_or_create(name=name,
                                    years=years)[0]
    m.save()
    return m


def add_course(start, end, practice_start, practice_end):
    c = Course.objects.get_or_create(start=start,
                                     end=end)[0]
    c.practice_start = practice_start
    c.practice_end = practice_end
    c.save()
    return c


def add_registered_student(student, course, major, year, group):
    rs = RegisteredStudent.objects.get_or_create(student=student,
                                                 course=course,
                                                 major=major,
                                                 year=year)[0]
    rs.group = group
    rs.save()
    return rs


def add_project(course, tutor, name, description, report=None):
    p = Project.objects.get_or_create(name=name,
                                      tutor=tutor,
                                      course=course)[0]
    p.description = description
    p.report = report
    p.save()
    return p


def add_tutor(user, workplace, category, job):
    t = Tutor.objects.get_or_create(user=user,
                                    workplace=workplace)[0]
    t.category = category
    t.job = job
    t.save()
    return t


def add_workplace(address, name, phone='0'):
    w = Workplace.objects.get_or_create(name=name,
                                        phone=phone)[0]
    w.address = address
    w.save()
    return w


def add_request(reg_student, project, priority, checked=True):
    req = Request.objects.get_or_create(reg_student=reg_student,
                                        project=project)[0]
    req.priority = priority
    req.checked = checked
    req.save()
    return req


def add_participation(reg_student, project, grade):
    part = Participation.objects.get_or_create(reg_student=reg_student,
                                               project=project)[0]
    part.grade = grade
    part.save()
    return part


def add_requirement(project, major, year, students_count):
    req = Requirement.objects.get_or_create(project=project,
                                            major=major,
                                            year=year,
                                            students_count=students_count)[0]
    req.save()
    return req


# Start execution here!
if __name__ == '__main__':
    print("Starting Practicas population script...")
    populate()
