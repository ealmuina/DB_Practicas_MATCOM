from django import forms

from .models import *


class RequestAdminForm(forms.ModelForm):
    class Meta:
        model = Request
        exclude = ()


class RequestForm(forms.ModelForm):
    priority = forms.IntegerField(label='Prioridad', help_text='Por favor asigne una prioridad a su solicitud.',
                                  initial=1)

    class Meta:
        model = Request
        fields = ('priority',)


class ParticipationForm(forms.ModelForm):
    grade = forms.IntegerField(max_value=5, min_value=2, required=False)

    class Meta:
        model = Participation
        exclude = ('project', 'reg_student')


class ParticipationAdminForm(forms.ModelForm):
    grade = forms.IntegerField(max_value=5, min_value=2, required=False)

    class Meta:
        model = Participation
        exclude = ()


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ()


class RegisteredStudentForm(forms.ModelForm):
    class Meta:
        model = RegisteredStudent
        exclude = ()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('slug',)
