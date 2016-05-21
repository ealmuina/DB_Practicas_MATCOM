import os

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


def validate_student_project_practice(self):
    try:
        if self.reg_student.practice not in self.project.practices.iterator():
            raise ValidationError("El estudiante registrado y el proyecto deben corresponder a las mismas prácticas.")
    except AttributeError:
        pass


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

    def clean(self):
        if self.start and self.end and self.start > self.end:
            raise ValidationError("La fecha de inicio del curso debe ser anterior a la de finalización.")

    def __str__(self):
        return '%s-%s' % (self.start.year, self.end.year)

    class Meta:
        verbose_name = 'curso'


class Practice(models.Model):
    course = models.ForeignKey('Course', verbose_name='curso')

    start = models.DateField('fecha de inicio')
    end = models.DateField('fecha de finalización')
    major = models.ForeignKey('Major', verbose_name='carrera')
    year = models.IntegerField('año',
                               validators=[MinValueValidator(1, message='Las carreras comienzan a partir del año 1.')])

    def clean(self):
        # Validate practice time
        if self.start and self.end and self.start > self.end:
            raise ValidationError("La fecha de inicio de las prácticas debe ser anterior a la de finalización.")

        # Validate practice is in course limits
        if self.start and self.end and \
                (self.start < self.course.start or self.end > self.course.end):
            raise ValidationError("La fecha de la práctica no está dentro del curso especificado.")

        # Validate year exists in that major
        if self.major and self.year and self.major.years < self.year:
            raise ValidationError(
                "El año de la práctica no es válido. Su carrera consta de {0} años.".format(self.major.years))

    def __str__(self):
        return "{0} {1} {2}".format(self.major, self.year, self.course)

    class Meta:
        verbose_name = 'práctica'
        unique_together = ('course', 'major', 'year')


class RegisteredStudent(models.Model):
    student = models.ForeignKey('Student', verbose_name='estudiante')
    practice = models.ForeignKey('Practice', verbose_name='práctica')
    course = models.ForeignKey('Course', verbose_name='curso')

    group = models.CharField('grupo', max_length=200)

    def __str__(self):
        return '{0} ({1}) ({2})'.format(self.student, self.group, self.course)

    def save(self, *args, **kwargs):
        self.course = self.practice.course
        super(RegisteredStudent, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'estudiante registrado'
        verbose_name_plural = 'estudiantes registrados'
        unique_together = ('student', 'course')


class Project(models.Model):
    tutor = models.ForeignKey('Tutor')
    course = models.ForeignKey('Course', verbose_name='curso')
    practices = models.ManyToManyField(Practice, verbose_name='prácticas')

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
        validate_student_project_practice(self)

    def __str__(self):
        return "{0} a {1} ({2})".format(self.reg_student.student, self.project, self.project.course)

    class Meta:
        verbose_name = 'solicitud'
        verbose_name_plural = 'solicitudes'
        unique_together = ('reg_student', 'project')


class Participation(models.Model):
    project = models.ForeignKey('Project', verbose_name='proyecto', blank=True, null=True)
    reg_student = models.OneToOneField('RegisteredStudent', verbose_name='estudiante registrado')

    proposed_grade = models.PositiveIntegerField('calificación propuesta', blank=True, null=True,
                                                 validators=[MaxValueValidator(5, "La máxima calificación es 5.")])
    grade = models.PositiveIntegerField('calificación', blank=True, null=True,
                                        validators=[MaxValueValidator(5, "La máxima calificación es 5.")])

    report = models.FileField('informe del estudiante', blank=True, storage=fs,
                              upload_to=make_participation_student_report_name)

    tutor_report = models.FileField('informe del tutor', blank=True, storage=fs,
                                    upload_to=make_participation_tutor_report_name)

    def clean(self):
        validate_student_project_practice(self)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            old_part = Participation.objects.get(reg_student=self.reg_student)
        except Participation.DoesNotExist:
            old_part = None

        if (not old_part or old_part.project != self.project) and self.project:
            requirement = Requirement.objects.filter(project=self.project, major=self.reg_student.practice.major,
                                                     year__lte=self.reg_student.practice.year,
                                                     students_count__gt=0).order_by('year').last()
            if requirement:
                requirement.students_count -= 1
                requirement.save()
        if old_part and old_part.project and old_part.project != self.project:
            requirement = Requirement.objects.filter(project=old_part.project, major=self.reg_student.practice.major,
                                                     year__lte=self.reg_student.practice.year).order_by('year').last()
            if requirement:
                requirement.students_count += 1
                requirement.save()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)
        requirement = Requirement.objects.filter(project=self.project, major=self.reg_student.practice.major,
                                                 year__lte=self.reg_student.practice.year).order_by('year').last()
        requirement.students_count += 1
        requirement.save()

    def __str__(self):
        return "{0} en {1} ({2})".format(self.reg_student.student, self.project, self.reg_student.course)

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

        perms = [
            Permission.objects.get(codename='change_participation'),

            Permission.objects.get(codename='add_project'),
            Permission.objects.get(codename='change_project'),
            Permission.objects.get(codename='delete_project'),

            Permission.objects.get(codename='change_request'),

            Permission.objects.get(codename='add_requirement'),
            Permission.objects.get(codename='change_requirement'),
            Permission.objects.get(codename='delete_requirement'),
        ]

        self.user.is_staff = True
        self.user.user_permissions.add(perms)
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
    user = models.ForeignKey(User, verbose_name='usuario')
    practice = models.ForeignKey('Practice', verbose_name='práctica')

    def save(self, *args, **kwargs):
        manager_permissions = Permission.objects.get(codename='manager_permissions')
        self.user.user_permissions.add(manager_permissions)
        self.user.save()
        super(PracticeManager, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'jefe de prácticas'
        verbose_name_plural = 'jefes de prácticas'
        permissions = [
            ('manager_permissions', 'Tiene permisos de jefe de practicas')
        ]
        unique_together = ('user', 'practice')
