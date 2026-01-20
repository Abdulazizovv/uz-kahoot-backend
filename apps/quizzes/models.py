from django.db import models
from django.conf import settings
from apps.common.models import BaseModel


class Subject(BaseModel):
    """Fan/Mavzu modeli"""
    name = models.CharField(max_length=255, unique=True, verbose_name="Fan nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"
        ordering = ['order', 'name']


class Question(BaseModel):
    """Savol modeli"""
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='questions',
        verbose_name="Fan"
    )
    question_text = models.TextField(verbose_name="Savol matni")
    time_limit = models.PositiveIntegerField(
        default=20, 
        verbose_name="Vaqt chegarasi (soniyalarda)"
    )
    cooldown = models.PositiveIntegerField(
        default=5, 
        verbose_name="Cooldown (soniyalarda)"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Oson'),
            ('medium', 'O\'rta'),
            ('hard', 'Qiyin'),
        ],
        default='medium',
        verbose_name="Qiyinlik darajasi"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    
    def __str__(self):
        return f"{self.subject.name}: {self.question_text[:50]}..."
    
    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ['subject', 'order', 'created_at']


class Answer(BaseModel):
    """Javob varianti modeli"""
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name="Savol"
    )
    answer_text = models.TextField(verbose_name="Javob matni")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri javobmi?")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.answer_text[:30]}"
    
    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"
        ordering = ['question', 'order']


class Quiz(BaseModel):
    """Test sessiyasi modeli"""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Talaba"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Fan"
    )
    title = models.CharField(max_length=255, verbose_name="Test nomi")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Boshlangan vaqt")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugatilgan vaqt")
    is_completed = models.BooleanField(default=False, verbose_name="Tugatilganmi?")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Jami savollar soni")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="To'g'ri javoblar soni")
    wrong_answers = models.PositiveIntegerField(default=0, verbose_name="Noto'g'ri javoblar soni")
    score = models.FloatField(default=0.0, verbose_name="Ball")
    percentage = models.FloatField(default=0.0, verbose_name="Foiz")
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    def calculate_results(self):
        """Natijalarni hisoblash"""
        if self.total_questions > 0:
            self.percentage = (self.correct_answers / self.total_questions) * 100
            self.score = self.correct_answers
        else:
            self.percentage = 0
            self.score = 0
        self.save()
    
    class Meta:
        verbose_name = "Test sessiyasi"
        verbose_name_plural = "Test sessiyalari"
        ordering = ['-started_at']


class StudentAnswer(BaseModel):
    """Talabaning bergan javobi modeli"""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name="Test sessiyasi"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name="Savol"
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='student_selections',
        verbose_name="Tanlangan javob",
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(default=False, verbose_name="To'g'rimi?")
    time_taken = models.PositiveIntegerField(
        default=0, 
        verbose_name="Sarflangan vaqt (soniyalarda)"
    )
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Javob berilgan vaqt")
    
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.quiz.student.user.get_full_name()} - {self.question.question_text[:30]}"
    
    def save(self, *args, **kwargs):
        """Javob to'g'ri yoki noto'g'ri ekanligini tekshirish"""
        if self.selected_answer:
            self.is_correct = self.selected_answer.is_correct
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Talaba javobi"
        verbose_name_plural = "Talaba javoblari"
        ordering = ['quiz', 'answered_at']
        unique_together = ['quiz', 'question']  # Bir test sessiyasida bir savolga faqat bir marta javob berish mumkin


class QuizAttempt(BaseModel):
    """Test urinishlari statistikasi"""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name="Talaba"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Fan"
    )
    total_attempts = models.PositiveIntegerField(default=0, verbose_name="Jami urinishlar")
    total_questions_answered = models.PositiveIntegerField(default=0, verbose_name="Jami javob berilgan savollar")
    total_correct = models.PositiveIntegerField(default=0, verbose_name="Jami to'g'ri javoblar")
    total_wrong = models.PositiveIntegerField(default=0, verbose_name="Jami noto'g'ri javoblar")
    average_score = models.FloatField(default=0.0, verbose_name="O'rtacha ball")
    best_score = models.FloatField(default=0.0, verbose_name="Eng yaxshi ball")
    last_attempt_date = models.DateTimeField(null=True, blank=True, verbose_name="Oxirgi urinish sanasi")
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} statistikasi"
    
    class Meta:
        verbose_name = "Test urinishi statistikasi"
        verbose_name_plural = "Test urinishlari statistikasi"
        unique_together = ['student', 'subject']
