from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from practicas.forms import RequestForm
from .models import *


def get_course_and_reg_student(request):
    try:
        course = Course.objects.get(practice_start__year=date.today().year)
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
        if not req.project in available_projects:
            available_projects.append(req.project)

    requested_projects = []
    requests = Request.objects.filter(reg_student=reg_student)
    for req in requests:
        available_projects.remove(req.project)
        requested_projects.append(req)

    return render(request, 'practicas/available_projects.html',
                  {'available_projects': available_projects, 'requested_projects': requested_projects})


class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)

        project = context['object']
        try:
            reg_student = RegisteredStudent.objects.get(student__user=self.request.user, course=project.course)
        except RegisteredStudent.DoesNotExist:
            reg_student = None

        if reg_student:
            try:
                context['request'] = Request.objects.get(project=project, reg_student=reg_student)
            except Request.DoesNotExist:
                context['request'] = None

        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectDetailView, self).dispatch(request, *args, **kwargs)  # def request_remove(request):


@permission_required('practicas.student_permissions')
def request_remove(request, project_name_slug):
    course, reg_student = get_course_and_reg_student(request)
    project = get_object_or_404(Project, slug=project_name_slug)

    req = get_object_or_404(Request, project=project, reg_student=reg_student)
    if not req.checked:
        req.delete()
        return redirect('project-detail', project_name_slug, permanent=True)
    else:
        return HttpResponseForbidden(
            """<h1>Error</h1>
            Su solicitud ha sido validada por el tutor del proyecto.
            Por favor, comuníquese con este si desea cancelarla.""")


@permission_required('practicas.student_permissions')
def request(request, project_name_slug):
    try:
        project = Project.objects.get(slug=project_name_slug)
    except Project.DoesNotExist:
        project = None
    course, reg_student = get_course_and_reg_student(request)

    # Verify the reg_student hasn't made a request to this project already.
    try:
        req = Request.objects.get(reg_student=reg_student, project=project)
    except Request.DoesNotExist:
        req = None

    if req:
        return HttpResponseForbidden("<h1>Error</h1>La solicitud que intenta crear ya existe.")

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
                return projects_available(
                    request)  # TODO: Turn into a redirect, y que me muestre un cartelito de solicitud exitosa.
        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = RequestForm()

    # Bad form (or form details), no form supplied...
    # Render rhe form with error messages (if any).
    return render(request, 'practicas/request.html', {'form': form, 'project': project})
