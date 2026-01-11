from django.db import models
from django.conf import settings
from apps.common.models import BaseModel


class StudentGroup(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Guruh nomi")
    grade = models.SmallIntegerField(default=1, verbose_name="Sinfi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Talabalar guruhi"
        verbose_name_plural = "Talabalar guruhlari"


class Student(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile', verbose_name="Foydalanuvchi")
    group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Guruh")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan sana")
    address = models.TextField(null=True, blank=True, verbose_name="Manzil")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.phone_number}"

    class Meta:
        verbose_name = "Talaba"
        verbose_name_plural = "Talabalar"


class Teacher(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile', verbose_name="Foydalanuvchi")
    subjects = models.CharField(max_length=500, blank=True, verbose_name="Fanlar")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Tajriba yillari")
    bio = models.TextField(blank=True, verbose_name="Biografiya")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.phone_number}"

    class Meta:
        verbose_name = "O'qituvchi"
        verbose_name_plural = "O'qituvchilar"
