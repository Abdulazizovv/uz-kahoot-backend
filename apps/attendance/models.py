from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.common.models import BaseModel
from datetime import time, timedelta


class Schedule(BaseModel):
    """
    Darslar jadvali (takrorlanadigan jadval)
    Masalan: Har dushanba 09:00 da Matematika darsi
    """
    group = models.ForeignKey(
        'students.StudentGroup',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Guruh"
    )
    subject = models.ForeignKey(
        'quizzes.Subject',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Fan"
    )
    teacher = models.ForeignKey(
        'students.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules',
        verbose_name="O'qituvchi"
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Dushanba'),
            ('tuesday', 'Seshanba'),
            ('wednesday', 'Chorshanba'),
            ('thursday', 'Payshanba'),
            ('friday', 'Juma'),
            ('saturday', 'Shanba'),
            ('sunday', 'Yakshanba'),
        ],
        verbose_name="Hafta kuni"
    )
    start_time = models.TimeField(verbose_name="Boshlanish vaqti")
    end_time = models.TimeField(verbose_name="Tugash vaqti")
    room = models.CharField(max_length=50, blank=True, verbose_name="Xona/Sinf")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    
    def __str__(self):
        return f"{self.group.name} - {self.subject.name} ({self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')})"
    
    class Meta:
        verbose_name = "Dars jadvali"
        verbose_name_plural = "Darslar jadvali"
        ordering = ['day_of_week', 'start_time']
        unique_together = ['group', 'day_of_week', 'start_time']


class Lesson(BaseModel):
    """
    Aniq dars sessiyasi (ma'lum bir kun va vaqtda bo'lgan dars)
    """
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Jadval",
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        'students.StudentGroup',
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Guruh"
    )
    subject = models.ForeignKey(
        'quizzes.Subject',
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Fan"
    )
    teacher = models.ForeignKey(
        'students.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name="O'qituvchi"
    )
    date = models.DateField(verbose_name="Dars sanasi")
    start_time = models.TimeField(verbose_name="Boshlanish vaqti")
    end_time = models.TimeField(verbose_name="Tugash vaqti")
    room = models.CharField(max_length=50, blank=True, verbose_name="Xona/Sinf")
    topic = models.CharField(max_length=255, blank=True, verbose_name="Dars mavzusi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Rejalashtirilgan'),
            ('ongoing', 'Davom etmoqda'),
            ('completed', 'Tugallangan'),
            ('cancelled', 'Bekor qilingan'),
        ],
        default='scheduled',
        verbose_name="Holat"
    )
    # Test bilan bog'lash
    related_quiz_subject = models.ForeignKey(
        'quizzes.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_lessons',
        verbose_name="Test fani (davomat uchun)",
        help_text="Agar student shu fandan test topshirsa, darsga kelgan deb hisoblanadi"
    )
    auto_attendance_enabled = models.BooleanField(
        default=True,
        verbose_name="Avtomatik davomat yoqilgan",
        help_text="Test orqali avtomatik davomat olinsinmi?"
    )
    attendance_window_before = models.PositiveIntegerField(
        default=30,
        verbose_name="Darsdan oldin (daqiqa)",
        help_text="Darsdan necha daqiqa oldin test topshirsa davomat olinadi"
    )
    attendance_window_after = models.PositiveIntegerField(
        default=30,
        verbose_name="Darsdan keyin (daqiqa)",
        help_text="Darsdan necha daqiqa keyin test topshirsa davomat olinadi"
    )
    
    def __str__(self):
        return f"{self.group.name} - {self.subject.name} ({self.date} {self.start_time.strftime('%H:%M')})"
    
    def is_attendance_window_active(self, check_time=None):
        """Davomat olish oynasi ochiqmi?"""
        if check_time is None:
            check_time = timezone.now()
        
        # Sanani va vaqtni birlashtirish
        from datetime import datetime
        lesson_start = datetime.combine(self.date, self.start_time)
        lesson_end = datetime.combine(self.date, self.end_time)
        
        # Timezone qo'shish
        lesson_start = timezone.make_aware(lesson_start)
        lesson_end = timezone.make_aware(lesson_end)
        
        # Davomat oynasini hisoblash
        window_start = lesson_start - timedelta(minutes=self.attendance_window_before)
        window_end = lesson_end + timedelta(minutes=self.attendance_window_after)
        
        return window_start <= check_time <= window_end
    
    class Meta:
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"
        ordering = ['-date', '-start_time']


class Attendance(BaseModel):
    """
    Davomat qaydlari
    """
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Dars"
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Talaba"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Keldi'),
            ('absent', 'Kelmadi'),
            ('late', 'Kech qoldi'),
            ('excused', 'Sababli'),
        ],
        default='present',
        verbose_name="Holat"
    )
    marked_at = models.DateTimeField(auto_now_add=True, verbose_name="Belgilangan vaqt")
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendances',
        verbose_name="Kim belgiladi"
    )
    is_auto_marked = models.BooleanField(
        default=False,
        verbose_name="Avtomatik belgilanganmi?",
        help_text="Test orqali avtomatik belgilangan davomat"
    )
    related_quiz = models.ForeignKey(
        'quizzes.Quiz',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
        verbose_name="Bog'langan test"
    )
    notes = models.TextField(blank=True, verbose_name="Izoh")
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.lesson.subject.name} ({self.lesson.date}) - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Davomat"
        verbose_name_plural = "Davomat qaydlari"
        ordering = ['-lesson__date', '-lesson__start_time']
        unique_together = ['lesson', 'student']


class AttendanceStatistics(BaseModel):
    """
    Talabaning davomat statistikasi
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_statistics',
        verbose_name="Talaba"
    )
    subject = models.ForeignKey(
        'quizzes.Subject',
        on_delete=models.CASCADE,
        related_name='attendance_statistics',
        verbose_name="Fan",
        null=True,
        blank=True
    )
    total_lessons = models.PositiveIntegerField(default=0, verbose_name="Jami darslar")
    present_count = models.PositiveIntegerField(default=0, verbose_name="Kelgan")
    absent_count = models.PositiveIntegerField(default=0, verbose_name="Kelmagan")
    late_count = models.PositiveIntegerField(default=0, verbose_name="Kech qolgan")
    excused_count = models.PositiveIntegerField(default=0, verbose_name="Sababli")
    attendance_rate = models.FloatField(default=0.0, verbose_name="Davomat foizi")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Oxirgi yangilangan")
    
    def __str__(self):
        subject_name = self.subject.name if self.subject else "Barcha fanlar"
        return f"{self.student.user.get_full_name()} - {subject_name} statistikasi"
    
    def calculate_rate(self):
        """Davomat foizini hisoblash"""
        if self.total_lessons > 0:
            self.attendance_rate = (self.present_count / self.total_lessons) * 100
        else:
            self.attendance_rate = 0.0
        self.save()
    
    class Meta:
        verbose_name = "Davomat statistikasi"
        verbose_name_plural = "Davomat statistikalari"
        unique_together = ['student', 'subject']
