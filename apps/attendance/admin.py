from django.contrib import admin
from .models import Schedule, Lesson, Attendance, AttendanceStatistics


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['group', 'subject', 'teacher', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'subject', 'group', 'is_active']
    search_fields = ['group__name', 'subject__name', 'teacher__user__first_name', 'teacher__user__last_name']
    ordering = ['day_of_week', 'start_time']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['group', 'subject', 'teacher', 'date', 'start_time', 'end_time', 'status', 'auto_attendance_enabled']
    list_filter = ['status', 'date', 'subject', 'group', 'auto_attendance_enabled']
    search_fields = ['group__name', 'subject__name', 'topic', 'teacher__user__first_name']
    ordering = ['-date', '-start_time']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'status', 'is_auto_marked', 'marked_at', 'marked_by']
    list_filter = ['status', 'is_auto_marked', 'lesson__date', 'lesson__subject']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'lesson__subject__name']
    ordering = ['-marked_at']
    readonly_fields = ['marked_at', 'created_at', 'updated_at']


@admin.register(AttendanceStatistics)
class AttendanceStatisticsAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'total_lessons', 'present_count', 'absent_count', 'attendance_rate']
    list_filter = ['subject', 'last_updated']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'subject__name']
    readonly_fields = ['total_lessons', 'present_count', 'absent_count', 'late_count', 'excused_count', 'attendance_rate', 'last_updated']
