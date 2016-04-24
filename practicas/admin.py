from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .forms import CourseForm, RequestAdminForm, ParticipationAdminForm, RegisteredStudentForm, ProjectForm
from .models import *


def get_current_course():
    return Course.objects.get(start__lte=date.today(), end__gte=date.today())


def get_object_course(object_id):
    project = Project.objects.get(id=object_id)
    return project.course


class AdminSite(admin.AdminSite):
    site_header = site_title = 'Administración de Prácticas'
    login_template = 'registration/login.html'


admin.site = AdminSite()


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1


class RequestStudentInline(admin.TabularInline):
    model = Request
    extra = 1
    form = RequestAdminForm
    exclude = ('checked',)


class RequestProjectInline(admin.TabularInline):
    model = Request
    extra = 1
    form = RequestAdminForm
    exclude = ('priority',)


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1
    form = ParticipationAdminForm


@admin.register(Major, site=admin.site)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['name', 'years']
    list_filter = ['years']
    search_fields = ['name']


@admin.register(Workplace, site=admin.site)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name']


@admin.register(Course, site=admin.site)
class CourseAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('start', 'end')}),
        ('Prácticas', {'fields': ('practice_start', 'practice_end')})
    ]
    form = CourseForm


@admin.register(Student, site=admin.site)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(RegisteredStudent, site=admin.site)
class RegisteredStudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'major', 'group']
    list_filter = ['course', 'major', 'year']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    inlines = [RequestStudentInline, ParticipationInline]
    form = RegisteredStudentForm


@admin.register(Project, site=admin.site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'tutor']
    search_fields = ['name', 'tutor__user__first_name', 'tutor__user__last_name']
    list_filter = ['course']
    inlines = [RequirementInline, ParticipationInline, RequestProjectInline]
    form = ProjectForm

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.tutor = Tutor.objects.get(user=request.user)
            obj.course = get_current_course()
        super(ProjectAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        course = get_current_course()
        if date.today() > course.practice_start:
            # Practice is already started. Tutors can't modify their projects now.
            return qs.filter(tutor=None)
        return qs.filter(tutor__user=request.user, course=course)

    def get_inline_instances(self, request, obj=None):
        inlines = self.inlines[:]
        if not request.user.is_superuser:
            for x in inlines:
                if x is ParticipationInline:
                    inlines.remove(x)
        return [inline(self.model, self.admin_site) for inline in inlines]

    def get_fields(self, request, obj=None):
        fields = super(ProjectAdmin, self).get_fields(request, obj)
        if not request.user.is_superuser:
            fields.remove('tutor')
            fields.remove('course')
        return fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not request.user.is_superuser:
            course = get_object_course(object_id)

            if not self.get_queryset(request).filter(id=object_id).exists() or date.today() > course.practice_start:
                return HttpResponseRedirect(reverse('admin:practicas_project_changelist'))

        return super(ProjectAdmin, self).change_view(request, object_id, form_url, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        if not request.user.is_superuser:
            course = get_object_course(object_id)

            if not self.get_queryset(request).filter(id=object_id).exists() or date.today() > course.practice_start:
                return HttpResponseRedirect(reverse('admin:practicas_project_changelist'))

        return super(ProjectAdmin, self).delete_view(request, object_id, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        if not request.user.is_superuser:
            if not self.get_queryset(request).filter(id=object_id).exists():
                return HttpResponseRedirect(reverse('admin:practicas_project_changelist'))

        return super(ProjectAdmin, self).history_view(request, object_id, extra_context)


@admin.register(Tutor, site=admin.site)
class TutorAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ['category', 'workplace']


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
