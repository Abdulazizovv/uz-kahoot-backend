from django.contrib import admin
from .models import Subject, Question, Answer, Quiz, StudentAnswer, QuizAttempt


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ['answer_text', 'is_correct', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'subject', 'difficulty', 'time_limit', 'created_at']
    list_filter = ['subject', 'difficulty', 'created_at']
    search_fields = ['question_text']
    ordering = ['subject', 'order']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text', 'question', 'is_correct', 'order']
    list_filter = ['is_correct', 'created_at']
    search_fields = ['answer_text', 'question__question_text']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'title', 'is_completed', 'score', 'percentage', 'started_at']
    list_filter = ['subject', 'is_completed', 'started_at']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'title']
    ordering = ['-started_at']
    readonly_fields = ['started_at', 'completed_at', 'score', 'percentage']


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question', 'selected_answer', 'is_correct', 'time_taken', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['quiz__student__user__first_name', 'question__question_text']
    ordering = ['-answered_at']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'total_attempts', 'total_correct', 'average_score', 'best_score']
    list_filter = ['subject', 'last_attempt_date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    readonly_fields = ['total_attempts', 'total_correct', 'total_wrong', 'average_score', 'best_score']
