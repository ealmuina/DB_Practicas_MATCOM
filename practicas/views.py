from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.aggregates import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from practicas.forms import RequestForm, ParticipationAssignForm, ParticipationForm
from set_participations import set_participations
from .models import *


@login_required
def index(request):
    context_dict = {}

    try:
        reg_student = RegisteredStudent.objects.get(student__user=request.user,
                                                    practice__course__start__lte=date.today(),
                                                    practice__course__end__gte=date.today())
        practice = reg_student.practice

    except RegisteredStudent.DoesNotExist:
        reg_student = None

        try:
            manager = PracticeManager.objects.get(user=request.user, practice__course__start__lte=date.today(),
                                                  practice__course__end__gte=date.today())
            practice = manager.practice
            manager_projects = Project.objects.filter(practices=practice)

            t = []
            for proj in manager_projects:
                total = Requirement.objects.filter(project=proj).aggregate(Sum('students_count'))
                t.append((proj, total['students_count__sum']))
            context_dict['manager_projects'] = t

        except PracticeManager.DoesNotExist:
            practice = None

    tutor_projects = Project.objects.filter(tutor__user=request.user, practices__start__lte=date.today(),
                                            practices__end__gte=date.today()).distinct()
    context_dict['tutor_projects'] = tutor_projects

    if practice:
        if practice.start <= date.today() <= practice.end:
            context_dict['days_left'] = (practice.end - date.today()).days + 1

        elif date.today() < practice.start:
            context_dict['days_until'] = (practice.start - date.today()).days

            if reg_student:
                available_projects = Project.objects.filter(practices=practice,
                                                            requirement__major=practice.major,
                                                            requirement__year__lte=practice.year).order_by('?')
                context_dict['available_projects'] = available_projects[:6]

        else:
            # Practice is over
            context_dict['days_after'] = (date.today() - practice.end).days
            if reg_student:
                # Current user is a student
                grade = Participation.objects.get(reg_student=reg_student).grade
                context_dict['grade'] = grade

    return render(request, 'practicas/index.html', context_dict)


@permission_required('practicas.student_permissions')
def projects_available(request):
    reg_student = get_object_or_404(RegisteredStudent, student__user=request.user, course__start__lte=date.today(),
                                    course__end__gte=date.today())
    practice = reg_student.practice

    available_projects = Project.objects.filter(practices=practice, requirement__major=practice.major,
                                                requirement__year__lte=practice.year) \
        .exclude(request__reg_student=reg_student)

    requested_projects = Request.objects.filter(reg_student=reg_student).order_by('priority')

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
    reg_student = get_object_or_404(RegisteredStudent, student__user=request.user, course__start__lte=date.today(),
                                    course__end__gte=date.today())
    practice = reg_student.practice
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
    project = get_object_or_404(Project, slug=project_name_slug)

    reg_student = get_object_or_404(RegisteredStudent, student__user=request.user, course__start__lte=date.today(),
                                    course__end__gte=date.today())
    practice = reg_student.practice

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
    ordering = ['-course']


@permission_required('practicas.tutor_permissions')
def evaluate_participations(request, project_name_slug):
    project = get_object_or_404(Project, slug=project_name_slug)
    current_projects = Project.objects.filter(tutor__user=request.user, practices__start__lte=date.today(),
                                              practices__end__gte=date.today())
    participations = Participation.objects.filter(project=project)

    if project not in current_projects:
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
    reg_student = get_object_or_404(RegisteredStudent, student__user=request.user, course__start__lte=date.today(),
                                    course__end__gte=date.today())
    practice = reg_student.practice
    participation = get_object_or_404(Participation, reg_student=reg_student)

    # A HTTP POST?
    if request.method == 'POST':
        form = ParticipationForm(request.POST, instance=participation)

        # Have been provided with a valid form?
        if form.is_valid():
            part = form.save(commit=False)
            # Did the user provide a report?
            if 'report' in request.FILES:
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


@permission_required('practicas.manager_permissions')
def assign_projects(request):
    manager = PracticeManager.objects.get(user=request.user, practice__course__start__lte=date.today(),
                                          practice__course__end__gte=date.today())
    practice = manager.practice

    reg_students = RegisteredStudent.objects.filter(practice=practice).order_by('group', 'student__user__last_name')

    # A HTTP POST?
    if request.method == 'POST':
        forms = []
        valid = True
        for i in range(len(reg_students)):
            try:
                participation = Participation.objects.get(reg_student=reg_students[i])
                forms.append(ParticipationAssignForm(request.POST, prefix=str(i), instance=participation))
            except Participation.DoesNotExist:
                forms.append(
                    ParticipationAssignForm(request.POST, prefix=str(i), initial={'reg_student': reg_students[i]}))
            valid = valid and forms[i].is_valid()

        # Have been provided with valid forms?
        if valid:
            for i in range(len(forms)):
                part = forms[i].save(commit=False)
                # if not part.project_id:
                #     print(int(forms[i].data['{0}-project'.format(i)]))
                #     part.project = Project.objects.get(id=int(forms[i].data['{0}-project'.format(i)]))
                part.reg_student = reg_students[i]
                part.proposed_grade = forms[i].initial['proposed_grade']
                part.save()

            return redirect(index, permanent=True)
        else:
            # The supplied forms contained errors - just print them to the terminal.
            print(form.errors for form in forms)
    else:
        # If the request was not a POST, display the forms to enter details.
        forms = []
        for i in range(len(reg_students)):
            try:
                participation = Participation.objects.get(reg_student=reg_students[i])
                forms.append(ParticipationAssignForm(instance=participation, prefix=str(i), practice=practice))
            except Participation.DoesNotExist:
                forms.append(
                    ParticipationAssignForm(prefix=str(i), practice=practice, initial={'reg_student': reg_students[i]}))

        tuples = [(forms[i], reg_students[i], forms[i].instance.proposed_grade if forms[i].instance else None) for i in
                  range(len(forms))]

        # Bad form (or form details), no form supplied...
        # Render rhe form with error messages (if any).
        return render(request, 'practicas/assign_projects.html',
                      {'tuples': tuples, 'practice': practice})


@permission_required('practicas.manager_permissions')
def auto_assign_projects(request):
    manager = PracticeManager.objects.get(user=request.user, practice__course__start__lte=date.today(),
                                          practice__course__end__gte=date.today())
    set_participations(manager)
    return redirect(assign_projects)


class RequestsList(ListView):
    model = Request
    template_name = 'practicas/requests_list.html'

    def get_queryset(self):
        manager = PracticeManager.objects.get(user=self.request.user, practice__course__start__lte=date.today(),
                                              practice__course__end__gte=date.today())
        return Request.objects.filter(project__practices=manager.practice).order_by('reg_student')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RequestsList, self).dispatch(request, *args, **kwargs)
