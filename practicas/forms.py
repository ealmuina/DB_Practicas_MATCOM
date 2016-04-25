from django import forms
from django.db import IntegrityError

from .models import *


class UserForm(forms.ModelForm):
    username = forms.CharField(label='Nombre de usuario')
    email = forms.EmailField(label='Email', max_length=200)
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellidos')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.initial = {'username': self.instance.user.username,
                            'email': self.instance.user.email,
                            'first_name': self.instance.user.first_name,
                            'last_name': self.instance.user.last_name}

    def clean(self):
        super(UserForm, self).clean()

        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        try:
            if not self.instance:
                self.instance.user = User.objects.create_user(username, email, password,
                                                              first_name=first_name,
                                                              last_name=last_name)
            else:
                user = self.instance.user
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name

                if password:
                    user.set_password(password)

                user.save()

        except IntegrityError:
            raise ValidationError('El usuario que intenta crear ya existe.')

    class Meta:
        exclude = ('user',)


class StudentForm(UserForm):
    pass


class TutorForm(UserForm):
    def __init__(self, *args, **kwargs):
        super(TutorForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.initial['category'] = self.instance.category
            self.initial['workplace'] = self.instance.workplace
            self.initial['job'] = self.instance.job


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
