from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from .forms import CourseForm, RequestAdminForm, ParticipationForm, RegisteredStudentForm, ProjectAdminForm
from .models import *


class AdminSite(admin.AdminSite):
    site_header = site_title = 'Administración de Prácticas'


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
    form = ParticipationForm


class MajorAdmin(admin.ModelAdmin):
    list_display = ['name', 'years']
    list_filter = ['years']
    search_fields = ['name']


class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name']


class CourseAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('start', 'end')}),
        ('Prácticas', {'fields': ('practice_start', 'practice_end')})
    ]
    form = CourseForm


class StudentAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name']


class RegisteredStudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'major', 'group']
    list_filter = ['course', 'major']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    inlines = [RequestStudentInline, ParticipationInline]
    form = RegisteredStudentForm


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'tutor']
    search_fields = ['name', 'tutor__user__first_name', 'tutor__user__last_name']
    list_filter = ['course']
    inlines = [RequirementInline, ParticipationInline, RequestProjectInline]
    form = ProjectAdminForm


class TutorAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ['category', 'workplace']


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)

admin.site.register(Course, CourseAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(RegisteredStudent, RegisteredStudentAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Tutor, TutorAdmin)
