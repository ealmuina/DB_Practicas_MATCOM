from django.contrib.auth.models import User
from django.db import models


# TODO: Validar que un estudiante registrado solo puede estar en un proyecto de su mismo curso

class Student(models.Model):
    user = models.OneToOneField(User, verbose_name='usuario')

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'estudiante'


class Major(models.Model):
    name = models.CharField('nombre', max_length=200)
    years = models.IntegerField('número de años')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'carrera'


class Course(models.Model):
    start = models.DateField('fecha de inicio')
    end = models.DateField('Fecha de finalización')

    def __str__(self):
        return '%s-%s' % (self.start.year, self.end.year)

    class Meta:
        verbose_name = 'curso'


class RegisteredStudent(models.Model):
    student = models.ForeignKey('Student', verbose_name='estudiante')
    course = models.ForeignKey('Course', verbose_name='curso')
    major = models.ForeignKey('Major', verbose_name='carrera')

    group = models.CharField('grupo', max_length=200)

    def __str__(self):
        return '{0} ({1})'.format(self.student, self.course)

    class Meta:
        verbose_name = 'estudiante registrado'
        verbose_name_plural = 'estudiantes registrados'


class Project(models.Model):
    course = models.ForeignKey('Course', verbose_name='curso')
    tutor = models.ForeignKey('Tutor')

    name = models.CharField('nombre', max_length=200)
    description = models.CharField('descripción', max_length=200)
    report = models.FileField('informe del tutor', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'proyecto'


class Request(models.Model):
    reg_student = models.ForeignKey('RegisteredStudent', verbose_name='estudiante registrado')
    project = models.ForeignKey('Project', verbose_name='proyecto')

    priority = models.IntegerField('prioridad')
    checked = models.BooleanField('confirmación del tutor')

    class Meta:
        verbose_name = 'solicitud'
        verbose_name_plural = 'solicitudes'


class Participation(models.Model):
    reg_student = models.OneToOneField('RegisteredStudent', verbose_name='estudiante registrado')
    project = models.ForeignKey('Project', verbose_name='proyecto')

    grade = models.IntegerField('calificación')
    report = models.FileField('informe del estudiante', blank=True)
    tutor_report = models.FileField('informe del tutor', blank=True)

    class Meta:
        verbose_name = 'participación'
        verbose_name_plural = 'participaciones'


class Requirement(models.Model):
    project = models.ForeignKey('Project', verbose_name='proyecto')
    major = models.ForeignKey('Major', verbose_name='carrera')

    year = models.IntegerField('año')
    students_count = models.IntegerField('cantidad de estudiantes')

    class Meta:
        verbose_name = 'requisito'


class Tutor(models.Model):
    user = models.OneToOneField(User, verbose_name='usuario')

    DOCTOR = 'DR'
    MASTER = 'MSC'
    BACHELOR = 'LIC'
    CATEGORIES = ((DOCTOR, 'Doctor'),
                  (MASTER, 'Master'),
                  (BACHELOR, 'Licenciado'))

    category = models.CharField('categoría científica', choices=CATEGORIES, max_length=3)

    workplace = models.ForeignKey('Workplace', verbose_name='centro de trabajo')
    job = models.CharField('puesto', max_length=200)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name_plural = 'tutores'


class Workplace(models.Model):
    name = models.CharField('nombre', max_length=200)
    address = models.CharField('dirección', max_length=250)
    phone = models.IntegerField('teléfono')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'centro de trabajo'
        verbose_name_plural = 'centros de trabajo'
