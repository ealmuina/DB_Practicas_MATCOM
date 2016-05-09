from django import forms
from django.db import IntegrityError

from .models import *


class UserForm(forms.ModelForm):
    username = forms.CharField(label='Nombre de usuario')
    email = forms.EmailField(label='Email', max_length=200)
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellidos')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña', required=False)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial = {'username': self.instance.user.username,
                            'email': self.instance.user.email,
                            'first_name': self.instance.user.first_name,
                            'last_name': self.instance.user.last_name}
        self.modify = True if instance else False

    def clean_password(self):
        password = self.cleaned_data['password']
        if password == '' and not self.modify:
            raise forms.ValidationError('Debe introducir una contraseña válida.')
        return password

    def clean(self):
        super(UserForm, self).clean()

        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)

        try:
            if not self.modify:
                self.instance.user = User.objects.create_user(username, email, password,
                                                              first_name=first_name,
                                                              last_name=last_name)
            else:
                self.instance.user.username = username
                self.instance.user.email = email
                self.instance.user.first_name = first_name
                self.instance.user.last_name = last_name

                if password:
                    self.instance.user.set_password(password)

                self.instance.user.save()

        except IntegrityError:
            raise forms.ValidationError('El usuario que intenta crear ya existe.')
        except ValueError:
            raise forms.ValidationError('Debe especificar un nombre de usuario correcto.')

    class Meta:
        exclude = ('user',)


class StudentForm(UserForm):
    pass


class TutorForm(UserForm):
    def __init__(self, *args, **kwargs):
        super(TutorForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['category'] = self.instance.category
            self.initial['workplace'] = self.instance.workplace
            self.initial['job'] = self.instance.job


class PracticeManagerForm(UserForm):
    def __init__(self, *args, **kwargs):
        super(PracticeManagerForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['course'] = self.instance.course
            self.initial['major'] = self.instance.major
            self.initial['year'] = self.instance.year


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

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course') if 'course' in kwargs else None
        super(ParticipationForm, self).__init__(*args, **kwargs)
        if course:
            self.fields['project'] = forms.ModelChoiceField(queryset=Project.objects.filter(course=course))
            if 'instance' in kwargs:
                self.fields['project'].initial = kwargs['instance'].project

    class Meta:
        model = Participation
        exclude = ('reg_student',)


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
