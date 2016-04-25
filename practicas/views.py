from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from practicas.forms import RequestForm, ParticipationForm
from .models import *


def get_course_and_reg_student(request):
    try:
        course = Course.objects.get(start__lte=date.today(), end__gte=date.today())
    except Course.DoesNotExist:
        course = None

    try:
        reg_student = RegisteredStudent.objects.get(student__user=request.user, course=course)
    except RegisteredStudent.DoesNotExist:
        reg_student = None

    return course, reg_student


@login_required
def index(request):
    context_dict = {}

    course, reg_student = get_course_and_reg_student(request)

    if course:
        tutor_projects = Project.objects.filter(tutor__user=request.user, course=course)
        context_dict['tutor_projects'] = tutor_projects

        if course.practice_running():
            context_dict['days_left'] = (course.practice_end - date.today()).days
        elif date.today() < course.practice_start:
            context_dict['days_until'] = (course.practice_start - date.today()).days
        else:
            # Practice is over
            context_dict['days_after'] = (date.today() - course.practice_end).days
            if reg_student:
                # Current user is a student
                grade = Participation.objects.get(reg_student=reg_student).grade
                context_dict['grade'] = grade

    return render(request, 'practicas/index.html', context_dict)


@permission_required('practicas.student_permissions')
def projects_available(request):
    course, reg_student = get_course_and_reg_student(request)

    # TODO: Averiguar si puedo pedir valores especificos de los objetos. En plan SELECT project FROM...
    requirements = Requirement.objects.filter(project__course=course, major=reg_student.major,
                                              year__lte=reg_student.year)
    available_projects = []
    for req in requirements:
        if req.project not in available_projects:
            available_projects.append(req.project)

    requested_projects = []
    requests = Request.objects.filter(reg_student=reg_student).order_by('priority')
    for req in requests:
        available_projects.remove(req.project)
        requested_projects.append(req)

    return render(request, 'practicas/available_projects.html',
                  {'available_projects': available_projects, 'requested_projects': requested_projects})


class ArchiveProjectDetailView(DetailView):
    model = Project
    template_name = 'practicas/archive_project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ArchiveProjectDetailView, self).get_context_data(**kwargs)

        participations = Participation.objects.filter(project=self.object)
        context['participations'] = participations

        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ArchiveProjectDetailView, self).dispatch(request, *args, **kwargs)


@permission_required('practicas.student_permissions')
def request_remove(request, project_name_slug):
    course, reg_student = get_course_and_reg_student(request)
    project = get_object_or_404(Project, slug=project_name_slug)

    req = get_object_or_404(Request, project=project, reg_student=reg_student)
    if not req.checked:
        req.delete()
        return redirect('projects-available', permanent=True)
    else:
        return HttpResponseForbidden(
            """<h1>Error</h1>
            Su solicitud ha sido validada por el tutor del proyecto.
            Por favor, comuníquese con este si desea cancelarla.""")


@permission_required('practicas.student_permissions')
def project_detail(request, project_name_slug):
    try:
        project = Project.objects.get(slug=project_name_slug)
    except Project.DoesNotExist:
        project = None
    course, reg_student = get_course_and_reg_student(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = RequestForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            if project and reg_student:
                req = form.save(commit=False)
                req.checked = False
                req.project = project
                req.reg_student = reg_student
                # Save the new request to the database and redirect to projects.
                req.save()
                return redirect('projects-available', permanent=True)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = RequestForm()

    context = {'form': form, 'project': project}

    try:
        context['request'] = Request.objects.get(project=project, reg_student=reg_student)
    except Request.DoesNotExist:
        context['request'] = None

    # Bad form (or form details), no form supplied...
    # Render rhe form with error messages (if any).
    return render(request, 'practicas/project_detail.html', context)


class ProjectArchive(ListView):
    model = Project
    template_name = 'practicas/archive_projects.html'


@permission_required('practicas.tutor_permissions')
def evaluate_participations(request, project_name_slug):
    project = get_object_or_404(Project, slug=project_name_slug)
    course = get_object_or_404(Course, start__lte=date.today(), end__gte=date.today())

    participations = Participation.objects.filter(project=project)
    tutor = Tutor.objects.get(user=request.user)

    if tutor != project.tutor or project.course != course:
        return HttpResponseForbidden(
            "<h1>Error</h1>Usted no tiene permiso para modificar las participaciones en el proyecto solicitado.")

    # A HTTP POST?
    if request.method == 'POST':
        forms = []
        valid = True
        for i in range(len(participations)):
            forms.append(ParticipationForm(request.POST, prefix=str(i), instance=participations[i]))
            valid = valid and forms[i].is_valid()

        # Have been provided with valid forms?
        if valid:
            for i in range(len(forms)):
                part = forms[i].save(commit=False)
                # Did the tutor provide a report?
                if '{0}-tutor_report'.format(i) in request.FILES:
                    participations[i].tutor_report.delete()
                    part.tutor_report = request.FILES['{0}-tutor_report'.format(i)]
                part.save()
            return redirect(index, permanent=True)
        else:
            # The supplied forms contained errors - just print them to the terminal.
            print(form.errors for form in forms)
    else:
        # If the request was not a POST, display the forms to enter details.
        forms = []
        for i in range(len(participations)):
            forms.append(ParticipationForm(instance=participations[i], prefix=str(i)))

    tuples = [(forms[i], participations[i]) for i in range(len(forms))]

    # Bad form (or form details), no form supplied...
    # Render rhe form with error messages (if any).
    return render(request, 'practicas/evaluate_participation.html',
                  {'tuples': tuples, 'project': participations[0].project})


@permission_required('practicas.student_permissions')
def upload_report(request):
    course, reg_student = get_course_and_reg_student(request)
    participation = get_object_or_404(Participation, reg_student=reg_student)

    # A HTTP POST?
    if request.method == 'POST':
        form = ParticipationForm(request.POST, instance=participation)

        # Have been provided with a valid form?
        if form.is_valid():
            part = form.save(commit=False)
            # Did the user provide a report?
            if 'report' in request.FILES:
                participation.report.delete()
                part.report = request.FILES['report']
                part.save()
                return redirect(index, permanent=True)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = ParticipationForm(instance=participation)

    # Bad form (or form details), no form supplied...
    # Render rhe form with error messages (if any).
    return render(request, 'practicas/upload_report.html', {'form': form, 'participation': participation})
