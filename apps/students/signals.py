from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Student, Teacher


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    User yaratilganda uning turiga qarab Student yoki Teacher profili yaratiladi.
    """
    if created:
        if instance.user_type == 'student':
            Student.objects.create(user=instance)
        elif instance.user_type == 'teacher':
            Teacher.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    User saqlanganida profil ham saqlanadi (agar mavjud bo'lsa).
    """
    if instance.user_type == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.user_type == 'teacher' and hasattr(instance, 'teacher_profile'):
        instance.teacher_profile.save()
