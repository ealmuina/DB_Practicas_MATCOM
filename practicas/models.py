import os
from datetime import date

from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import slugify

from bd.settings import MEDIA_ROOT


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(MEDIA_ROOT, name))
        return name


fs = OverwriteStorage(location=MEDIA_ROOT)


def validate_student_project_course(self):
    if 'reg_student' in self.__dict__ and self.reg_student and 'project' in self.__dict__ and self.project:
        if self.reg_student.course != self.project.course:
            raise ValidationError("El estudiante registrado y el proyecto deben corresponder al mismo curso.")


def make_project_report_name(instance, filename):
    ext = filename.split('.')[-1]
    return 'Proyecto {0}.{1}'.format(instance.name, ext)


def make_participation_student_report_name(instance, filename):
    ext = filename.split('.')[-1]
    return 'Informe de {0} (estudiante).{1}'.format(instance.reg_student, ext)


def make_participation_tutor_report_name(instance, filename):
    ext = filename.split('.')[-1]
    return 'Informe de {0} (tutor).{1}'.format(instance.reg_student, ext)


class Student(models.Model):
    user = models.OneToOneField(User, verbose_name='usuario', unique=True)

    def save(self, *args, **kwargs):
        student_permissions = Permission.objects.get(codename='student_permissions')
        self.user.user_permissions.add(student_permissions)
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'estudiante'
        permissions = [
            ('student_permissions', 'Tiene permisos de estudiante')
        ]


class Major(models.Model):
    name = models.CharField('nombre', max_length=200, unique=True)
    years = models.IntegerField('número de años',
                                validators=[MinValueValidator(1, message='Toda carrera debe durar más de 1 año.')])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'carrera'


class Course(models.Model):
    start = models.DateField('fecha de inicio', unique=True)
    end = models.DateField('Fecha de finalización', unique=True)

    practice_start = models.DateField('fecha de inicio de las prácticas', unique=True)
    practice_end = models.DateField('fecha de finalización de las prácticas', unique=True)

    def practice_running(self):
        now = date.today()
        return now >= self.practice_start and now <= self.practice_end

    def clean(self):
        if self.start and self.end:
            if self.start > self.end:
                raise ValidationError("La fecha de inicio del curso debe ser anterior a la de finalización.")

        if self.practice_start and self.practice_end:
            if self.practice_start > self.practice_end:
                raise ValidationError("La fecha de inicio de las prácticas debe ser anterior a la de finalización.")

    def __str__(self):
        return '%s-%s' % (self.start.year, self.end.year)

    class Meta:
        verbose_name = 'curso'


class RegisteredStudent(models.Model):
    student = models.ForeignKey('Student', verbose_name='estudiante')
    course = models.ForeignKey('Course', verbose_name='curso')
    major = models.ForeignKey('Major', verbose_name='carrera')

    year = models.IntegerField('año',
                               validators=[MinValueValidator(1, message='Las carreras comienzan a partir del año 1.')])
    group = models.CharField('grupo', max_length=200)

    def clean(self):
        if self.major and self.year:
            if self.major.years < self.year:
                raise ValidationError(
                    "El año que cursa el estudiante no es válido. Su carrera consta de {0} años.".format(
                        self.major.years))

    def __str__(self):
        return '{0} ({1}) ({2})'.format(self.student, self.group, self.course)

    class Meta:
        verbose_name = 'estudiante registrado'
        verbose_name_plural = 'estudiantes registrados'
        unique_together = ('student', 'course')


class Project(models.Model):
    course = models.ForeignKey('Course', verbose_name='curso')
    tutor = models.ForeignKey('Tutor')

    name = models.CharField('nombre', max_length=200)
    description = models.TextField('descripción')
    report = models.FileField('informe del tutor', blank=True, storage=fs, upload_to=make_project_report_name)

    slug = models.SlugField(editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'proyecto'


class Request(models.Model):
    reg_student = models.ForeignKey('RegisteredStudent', verbose_name='estudiante registrado')
    project = models.ForeignKey('Project', verbose_name='proyecto')

    priority = models.PositiveIntegerField('prioridad', default=1)
    checked = models.BooleanField('confirmación del tutor', default=False)

    def clean(self):
        validate_student_project_course(self)

    def __str__(self):
        return "{0} a {1} ({2})".format(self.reg_student.student, self.project, self.project.course)

    class Meta:
        verbose_name = 'solicitud'
        verbose_name_plural = 'solicitudes'
        unique_together = ('reg_student', 'project')


class Participation(models.Model):
    project = models.ForeignKey('Project', verbose_name='proyecto')
    reg_student = models.OneToOneField('RegisteredStudent', verbose_name='estudiante registrado')

    grade = models.PositiveIntegerField('calificación', blank=True, null=True,
                                        validators=[MaxValueValidator(5, "La máxima calificación es 5.")])
    report = models.FileField('informe del estudiante', blank=True, storage=fs,
                              upload_to=make_participation_student_report_name)

    tutor_report = models.FileField('informe del tutor', blank=True, storage=fs,
                                    upload_to=make_participation_tutor_report_name)

    def clean(self):
        validate_student_project_course(self)

    def __str__(self):
        return "{0} en {1} ({2})".format(self.reg_student.student, self.project, self.project.course)

    class Meta:
        verbose_name = 'participación'
        verbose_name_plural = 'participaciones'


class Requirement(models.Model):
    project = models.ForeignKey('Project', verbose_name='proyecto')
    major = models.ForeignKey('Major', verbose_name='carrera')

    year = models.IntegerField('año',
                               validators=[
                                   MinValueValidator(1, message='Toda carrera tiene duración mayor que 1 año.')])
    students_count = models.IntegerField('cantidad de estudiantes', validators=[
        MinValueValidator(1, "En el proyecto debe participar al menos 1 estudiante.")])

    def delete(self, using=None, keep_parents=False):
        super(Requirement, self).delete(using, keep_parents)

        requests = Request.objects.filter(project=self.project)
        for req in requests:
            if not Requirement.objects.filter(project=self.project, major=req.reg_student.major,
                                              year__lte=req.reg_student.year).exists():
                req.delete()

    class Meta:
        verbose_name = 'requisito'
        unique_together = ('project', 'major', 'year')


class Tutor(models.Model):
    user = models.OneToOneField(User, verbose_name='usuario', unique=True)

    DOCTOR = 'DR'
    MASTER = 'MSC'
    BACHELOR = 'LIC'
    CATEGORIES = ((DOCTOR, 'Doctor'),
                  (MASTER, 'Master'),
                  (BACHELOR, 'Licenciado'))

    category = models.CharField('categoría científica', choices=CATEGORIES, max_length=3)

    workplace = models.ForeignKey('Workplace', verbose_name='centro de trabajo')
    job = models.CharField('puesto', max_length=200)

    def save(self, *args, **kwargs):
        tutor_permissions = Permission.objects.get(codename='tutor_permissions')
        self.user.user_permissions.add(tutor_permissions)

        change_participation = Permission.objects.get(codename='change_participation')

        add_project = Permission.objects.get(codename='add_project')
        change_project = Permission.objects.get(codename='change_project')
        delete_project = Permission.objects.get(codename='delete_project')

        change_request = Permission.objects.get(codename='change_request')

        add_requirement = Permission.objects.get(codename='add_requirement')
        change_requirement = Permission.objects.get(codename='change_requirement')
        delete_requirement = Permission.objects.get(codename='delete_requirement')

        self.user.is_staff = True
        self.user.user_permissions.add(change_participation, add_project, change_project, delete_project,
                                       change_request, add_requirement, change_requirement, delete_requirement)
        self.user.save()

        super(Tutor, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name_plural = 'tutores'
        permissions = [
            ('tutor_permissions', 'Tiene permisos de tutor')
        ]


class Workplace(models.Model):
    name = models.CharField('nombre', max_length=200, unique=True)
    address = models.CharField('dirección', max_length=250)
    phone = models.PositiveIntegerField('teléfono')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'centro de trabajo'
        verbose_name_plural = 'centros de trabajo'


class PracticeManager(models.Model):
    user = models.OneToOneField(User, verbose_name='usuario', unique=True)
    course = models.ForeignKey(Course, verbose_name='curso')
    major = models.ForeignKey('Major', verbose_name='carrera')
    year = models.IntegerField('año',
                               validators=[MinValueValidator(1, message='Las carreras comienzan a partir del año 1.')])

    def clean(self):
        if self.major and self.year:
            if self.major.years < self.year:
                raise ValidationError(
                    "El año que cursa el estudiante no es válido. Su carrera consta de {0} años.".format(
                        self.major.years))

    def save(self, *args, **kwargs):
        manager_permissions = Permission.objects.get(codename='manager_permissions')
        self.user.user_permissions.add(manager_permissions)
        super(PracticeManager, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'jefe de prácticas'
        verbose_name_plural = 'jefes de prácticas'
        permissions = [
            ('manager_permissions', 'Tiene permisos de jefe de practicas')
        ]
