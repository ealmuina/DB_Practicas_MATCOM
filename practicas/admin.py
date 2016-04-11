from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import *


class AdminSite(admin.AdminSite):
    site_header = site_title = 'Administración de Prácticas'


admin.site = AdminSite()


# class StudentInline(admin.StackedInline):
#     model = Student
#
#
# class TutorInline(admin.StackedInline):
#     model = Tutor
#
#
# class UserAdmin(UserAdmin):
#     inlines = [StudentInline, TutorInline]
#
#
# admin.site.register(User, UserAdmin)


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


class StudentAdmin(admin.ModelAdmin):
    # TODO: Create form
    search_fields = ['user__first_name', 'user__last_name']


class RegisteredStudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'major', 'group']
    list_filter = ['course', 'major']
    search_fields = ['student__user__first_name', 'student__user__last_name']


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['reg_student', 'project']
    search_fields = ['reg_student__student__user__first_name', 'reg_student__student__user__last_name' 'project__name']
    list_filter = ['project', 'reg_student__course']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'tutor']
    search_fields = ['name', 'tutor__user__first_name', 'tutor__user__last_name']
    list_filter = ['course']


class RequirementAdmin(admin.ModelAdmin):
    list_display = ['project', 'major', 'year', 'students_count']
    search_fields = ['project__name']
    list_filter = ['project', 'major', 'year']


class RequestAdmin(admin.ModelAdmin):
    list_display = ['reg_student', 'project', 'priority', 'checked']
    search_fields = ['reg_student__student__user__first_name', 'reg_student__student__user__last_name' 'project__name']
    list_filter = ['reg_student__course']


class TutorAdmin(admin.ModelAdmin):
    # TODO: Create form
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ['category', 'workplace']


admin.site.register(User, UserAdmin)
admin.site.register(Group)

admin.site.register(Course, CourseAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(RegisteredStudent, RegisteredStudentAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Tutor, TutorAdmin)
