from django import forms
from django.core.exceptions import ValidationError

from .models import *


def validate_student_project_course(self):
    cleaned_data = self.cleaned_data

    reg_student = cleaned_data.get('reg_student')
    project = cleaned_data.get('project')

    if reg_student and project:
        if reg_student.course != project.course:
            raise ValidationError("El estudiante registrado y el proyecto deben corresponder al mismo curso.")

    return cleaned_data


class RequestAdminForm(forms.ModelForm):
    def clean(self):
        return validate_student_project_course(self)

    class Meta:
        model = Request
        exclude = ()


class RequestForm(forms.ModelForm):
    def clean(self):
        return validate_student_project_course(self)

    class Meta:
        model = Request
        fields = ('priority',)


class ParticipationForm(forms.ModelForm):
    def clean(self):
        return validate_student_project_course(self)

    class Meta:
        model = Participation
        exclude = ()


class CourseForm(forms.ModelForm):
    def clean(self):
        cleaned_data = self.cleaned_data

        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        if start and end:
            if start > end:
                raise ValidationError("La fecha de inicio del curso debe ser anterior a la de finalización.")

        start = cleaned_data.get('practice_start')
        end = cleaned_data.get('practice_end')

        if start and end:
            if start > end:
                raise ValidationError("La fecha de inicio de las prácticas debe ser anterior a la de finalización.")

        return cleaned_data

    class Meta:
        model = Course
        exclude = ()


class RegisteredStudentForm(forms.ModelForm):
    def clean(self):
        cleaned_data = self.cleaned_data

        major = cleaned_data['major']
        year = cleaned_data['year']

        if major and year:
            if major.years < year:
                raise ValidationError(
                    "El año que cursa el estudiante no es válido. Su carrera solamente tiene {0} años.".format(
                        major.years))

        return cleaned_data

    class Meta:
        model = RegisteredStudent
        exclude = ()


class ProjectAdminForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Project
        exclude = ()


class ProjectForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Project
        exclude = ('course', 'tutor')
