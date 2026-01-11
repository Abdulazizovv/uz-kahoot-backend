from django.contrib import admin
from .models import StudentGroup, Student, Teacher


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'created_at')
    list_filter = ('grade', 'created_at')
    search_fields = ('name',)
    ordering = ('grade', 'name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'date_of_birth', 'created_at')
    list_filter = ('group', 'created_at', 'date_of_birth')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'group')
    ordering = ('-created_at',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'subjects', 'experience_years', 'created_at')
    list_filter = ('experience_years', 'created_at')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name', 'subjects')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
