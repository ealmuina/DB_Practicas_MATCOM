from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from .forms import RequestAdminForm, ParticipationAdminForm, RegisteredStudentForm, ProjectForm, \
    StudentForm, TutorForm, PracticeManagerForm
from .models import *


def get_current_course():
    return Course.objects.get(start__lte=date.today(), end__gte=date.today())


def get_object_course(object_id):
    project = Project.objects.get(id=object_id)
    return project.course


def get_queryset_with_matching_course(field, db_field, request):
    if db_field.name in ('reg_student', 'project'):
        if request._obj_:
            field.queryset = field.queryset.filter(course=request._obj_.course)
        else:
            field.queryset = field.queryset.filter(course=get_current_course())
    return field


class AdminSite(admin.AdminSite):
    site_header = site_title = 'Administración de Prácticas'
    login_template = 'registration/login.html'


admin.site = AdminSite()


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1


class RequestInline(admin.TabularInline):
    model = Request
    extra = 1
    form = RequestAdminForm

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(RequestInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        return get_queryset_with_matching_course(field, db_field, request)


class RequestStudentInline(RequestInline):
    exclude = ('checked',)


class RequestProjectInline(RequestInline):
    fields = ('reg_student', 'project', 'checked')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(RequestInline, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ('reg_student', 'reg_student')
        return readonly_fields

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1
    form = ParticipationAdminForm

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(ParticipationInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        return get_queryset_with_matching_course(field, db_field, request)


@admin.register(Participation, site=admin.site)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['reg_student', 'project']
    list_filter = ['reg_student__practice__major', 'reg_student__practice__course']


@admin.register(Request, site=admin.site)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['reg_student', 'project', 'priority', 'checked']
    list_filter = ['reg_student__practice__major', 'reg_student__course']


@admin.register(Major, site=admin.site)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['name', 'years']
    list_filter = ['years']
    search_fields = ['name']


@admin.register(Workplace, site=admin.site)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name']


class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name']
    fieldsets = [
        ('Datos personales', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Datos de usuario', {
            'classes': ('collapse',),
            'fields': ('username', 'password')
        })
    ]


@admin.register(Student, site=admin.site)
class StudentAdmin(CustomUserAdmin):
    form = StudentForm


@admin.register(RegisteredStudent, site=admin.site)
class RegisteredStudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'group']
    list_filter = ['course', 'practice__major', 'practice__year']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    inlines = [RequestStudentInline, ParticipationInline]
    form = RegisteredStudentForm

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(RegisteredStudentAdmin, self).get_form(request, obj, **kwargs)


@admin.register(Project, site=admin.site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'tutor']
    search_fields = ['name', 'tutor__user__first_name', 'tutor__user__last_name']
    list_filter = ['course']
    inlines = [RequirementInline, ParticipationInline, RequestProjectInline]
    form = ProjectForm
    filter_horizontal = ('practices',)
    fields = ['tutor', 'course', 'name', 'description', 'report', 'practices']

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.tutor = Tutor.objects.get(user=request.user)
            obj.course = get_current_course()
        super(ProjectAdmin, self).save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(ProjectAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tutor__user=request.user, practices__start__gt=date.today())

    def get_inline_instances(self, request, obj=None):
        inlines = self.inlines[:]
        if not request.user.is_superuser:
            for x in inlines:
                if x is ParticipationInline:
                    inlines.remove(x)
        return [inline(self.model, self.admin_site) for inline in inlines]

    def get_fields(self, request, obj=None):
        fields = self.fields[:]
        if not request.user.is_superuser:
            fields.remove('tutor')
            fields.remove('course')
        return fields


@admin.register(Tutor, site=admin.site)
class TutorAdmin(CustomUserAdmin):
    radio_fields = {'category': admin.HORIZONTAL}
    list_filter = ['category', 'workplace']
    fieldsets = CustomUserAdmin.fieldsets + [
        ('Datos de tutor', {
            'fields': ('category', 'workplace', 'job')
        })
    ]
    form = TutorForm


@admin.register(PracticeManager, site=admin.site)
class PracticeManagerAdmin(admin.ModelAdmin):
    list_filter = ['practice__course']
    # fieldsets = CustomUserAdmin.fieldsets + [
    #     ('Datos de las prácticas', {
    #         'fields': ('course', 'major', 'year')
    #     })
    # ]
    form = PracticeManagerForm


admin.site.register(Practice)
admin.site.register(Course)

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
