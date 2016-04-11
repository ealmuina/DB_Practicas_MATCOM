from django.contrib import admin

from .models import *


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['name', 'years']
    list_filter = ['years']
    search_fields = ['name']


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # TODO: Create form
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(RegisteredStudent)
class RegisteredStudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'major', 'group']
    list_filter = ['course', 'major']
    search_fields = ['student__user__first_name', 'student__user__last_name']


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['reg_student', 'project']
    search_fields = ['reg_student__student__user__first_name', 'reg_student__student__user__last_name' 'project__name']
    list_filter = ['project', 'reg_student__course']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'tutor']
    search_fields = ['name', 'tutor__user__first_name', 'tutor__user__last_name']
    list_filter = ['course']


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ['project', 'major', 'year', 'students_count']
    search_fields = ['project__name']
    list_filter = ['project', 'major', 'year']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['reg_student', 'project', 'priority', 'checked']
    search_fields = ['reg_student__student__user__first_name', 'reg_student__student__user__last_name' 'project__name']
    list_filter = ['reg_student__course']


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    # TODO: Create form
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ['category', 'workplace']


admin.site.register(Course)
