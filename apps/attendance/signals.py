from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.quizzes.models import Quiz
from .models import Lesson, Attendance, AttendanceStatistics


@receiver(post_save, sender=Quiz)
def auto_mark_attendance_on_quiz_completion(sender, instance, created, **kwargs):
    """
    Test tugagandan keyin avtomatik davomat belgilash
    """
    # Faqat test tugallanganda
    if not instance.is_completed:
        return
    
    # Bugungi kun
    today = timezone.now().date()
    current_time = timezone.now()
    
    # Bugungi kungi darslarni topish
    lessons = Lesson.objects.filter(
        date=today,
        group=instance.student.group,
        subject=instance.subject,  # Test fani bilan mos kelishi kerak
        auto_attendance_enabled=True,
        status__in=['scheduled', 'ongoing'],
        deleted_at__isnull=True
    )
    
    for lesson in lessons:
        # Davomat oynasi ochiqmi?
        if not lesson.is_attendance_window_active(current_time):
            continue
        
        # Allaqachon davomat belgilangan bo'lsa
        if Attendance.objects.filter(
            lesson=lesson,
            student=instance.student,
            deleted_at__isnull=True
        ).exists():
            continue
        
        # Avtomatik davomat belgilash
        Attendance.objects.create(
            lesson=lesson,
            student=instance.student,
            status='present',
            is_auto_marked=True,
            related_quiz=instance,
            marked_by=instance.student.user,
            notes='Test orqali avtomatik belgilandi'
        )
        
        # Statistikani yangilash
        update_attendance_statistics(instance.student, lesson.subject)


@receiver(post_save, sender=Attendance)
def update_statistics_on_attendance(sender, instance, created, **kwargs):
    """
    Davomat belgilanganda statistikani yangilash
    """
    if created:
        update_attendance_statistics(instance.student, instance.lesson.subject)


def update_attendance_statistics(student, subject):
    """
    Talabaning davomat statistikasini yangilash
    """
    # Fan bo'yicha statistika
    stats, created = AttendanceStatistics.objects.get_or_create(
        student=student,
        subject=subject,
        defaults={'deleted_at': None}
    )
    
    # Davomat qaydlarini hisoblash
    attendances = Attendance.objects.filter(
        student=student,
        lesson__subject=subject,
        deleted_at__isnull=True
    )
    
    stats.total_lessons = attendances.count()
    stats.present_count = attendances.filter(status='present').count()
    stats.absent_count = attendances.filter(status='absent').count()
    stats.late_count = attendances.filter(status='late').count()
    stats.excused_count = attendances.filter(status='excused').count()
    stats.calculate_rate()
    
    # Umumiy statistika (barcha fanlar)
    overall_stats, _ = AttendanceStatistics.objects.get_or_create(
        student=student,
        subject=None,
        defaults={'deleted_at': None}
    )
    
    all_attendances = Attendance.objects.filter(
        student=student,
        deleted_at__isnull=True
    )
    
    overall_stats.total_lessons = all_attendances.count()
    overall_stats.present_count = all_attendances.filter(status='present').count()
    overall_stats.absent_count = all_attendances.filter(status='absent').count()
    overall_stats.late_count = all_attendances.filter(status='late').count()
    overall_stats.excused_count = all_attendances.filter(status='excused').count()
    overall_stats.calculate_rate()
