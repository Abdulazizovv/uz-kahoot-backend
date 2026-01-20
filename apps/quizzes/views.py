from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.utils import timezone
from django.db.models import Count, Avg, Q
import random

from .models import Subject, Question, Answer, Quiz, StudentAnswer, QuizAttempt
from .serializers import (
    SubjectListSerializer,
    SubjectDetailSerializer,
    SubjectCreateUpdateSerializer,
    QuestionListSerializer,
    QuestionDetailSerializer,
    QuestionCreateSerializer,
    QuestionUpdateSerializer,
    QuestionForQuizSerializer,
    QuizListSerializer,
    QuizDetailSerializer,
    QuizCreateSerializer,
    StudentAnswerSerializer,
    StudentAnswerDetailSerializer,
    QuizAttemptSerializer,
    QuizStartSerializer,
    QuizSubmitAnswerSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Fanlar ro'yxati",
        description="Barcha fanlar ro'yxatini olish",
        tags=["Fanlar"]
    ),
    retrieve=extend_schema(
        summary="Fan tafsilotlari",
        description="Bitta fan haqida to'liq ma'lumot olish",
        tags=["Fanlar"]
    ),
    create=extend_schema(
        summary="Yangi fan yaratish",
        description="Yangi fan qo'shish",
        tags=["Fanlar"]
    ),
    update=extend_schema(
        summary="Fanni yangilash",
        description="Fan ma'lumotlarini to'liq yangilash",
        tags=["Fanlar"]
    ),
    partial_update=extend_schema(
        summary="Fanni qisman yangilash",
        description="Fan ma'lumotlarini qisman yangilash",
        tags=["Fanlar"]
    ),
    destroy=extend_schema(
        summary="Fanni o'chirish",
        description="Fanni soft delete qilish",
        tags=["Fanlar"]
    ),
)
class SubjectViewSet(viewsets.ModelViewSet):
    """
    Subject CRUD operations
    
    Fanlar bilan ishlash uchun API endpoints
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        return Subject.objects.filter(deleted_at__isnull=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SubjectCreateUpdateSerializer
        return SubjectListSerializer
    
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()


@extend_schema_view(
    list=extend_schema(
        summary="Savollar ro'yxati",
        description="Barcha savollar ro'yxatini olish",
        tags=["Savollar"]
    ),
    retrieve=extend_schema(
        summary="Savol tafsilotlari",
        description="Bitta savol haqida to'liq ma'lumot olish",
        tags=["Savollar"]
    ),
    create=extend_schema(
        summary="Yangi savol yaratish",
        description="Yangi savol va javoblar qo'shish",
        tags=["Savollar"]
    ),
    update=extend_schema(
        summary="Savolni yangilash",
        description="Savol ma'lumotlarini yangilash",
        tags=["Savollar"]
    ),
    partial_update=extend_schema(
        summary="Savolni qisman yangilash",
        description="Savol ma'lumotlarini qisman yangilash",
        tags=["Savollar"]
    ),
    destroy=extend_schema(
        summary="Savolni o'chirish",
        description="Savolni soft delete qilish",
        tags=["Savollar"]
    ),
)
class QuestionViewSet(viewsets.ModelViewSet):
    """
    Question CRUD operations
    
    Savollar bilan ishlash uchun API endpoints
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'difficulty']
    search_fields = ['question_text']
    ordering_fields = ['order', 'created_at', 'time_limit']
    ordering = ['subject', 'order']
    
    def get_queryset(self):
        return Question.objects.filter(
            deleted_at__isnull=True
        ).select_related('subject').prefetch_related('answers')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuestionDetailSerializer
        elif self.action == 'create':
            return QuestionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return QuestionUpdateSerializer
        return QuestionListSerializer
    
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="Fan bo'yicha savollar",
        description="Ma'lum bir fandagi barcha savollar",
        tags=["Savollar"],
        parameters=[
            OpenApiParameter(
                name='subject_id',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Fan ID (UUID)',
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_subject(self, request):
        """Fan bo'yicha savollar"""
        subject_id = request.query_params.get('subject_id')
        if not subject_id:
            return Response(
                {'detail': 'subject_id parametri talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        questions = self.get_queryset().filter(subject_id=subject_id)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Test sessiyalari ro'yxati",
        description="Barcha test sessiyalari ro'yxatini olish",
        tags=["Testlar"]
    ),
    retrieve=extend_schema(
        summary="Test sessiyasi tafsilotlari",
        description="Bitta test sessiyasi haqida to'liq ma'lumot",
        tags=["Testlar"]
    ),
    create=extend_schema(
        summary="Test sessiyasi yaratish",
        description="Yangi test sessiyasini boshlash",
        tags=["Testlar"]
    ),
    destroy=extend_schema(
        summary="Test sessiyasini o'chirish",
        description="Test sessiyasini soft delete qilish",
        tags=["Testlar"]
    ),
)
class QuizViewSet(viewsets.ModelViewSet):
    """
    Quiz CRUD operations
    
    Test sessiyalari bilan ishlash uchun API endpoints
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'student', 'is_completed']
    search_fields = ['title', 'student__user__first_name', 'student__user__last_name']
    ordering_fields = ['started_at', 'completed_at', 'score', 'percentage']
    ordering = ['-started_at']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    def get_queryset(self):
        return Quiz.objects.filter(
            deleted_at__isnull=True
        ).select_related('student__user', 'subject')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        elif self.action == 'create':
            return QuizCreateSerializer
        return QuizListSerializer
    
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="Test boshlash",
        description="Yangi test sessiyasini boshlash va tasodifiy savollar olish",
        tags=["Testlar"],
        request=QuizStartSerializer,
        responses={201: QuizDetailSerializer}
    )
    @action(detail=False, methods=['post'])
    def start_quiz(self, request):
        """Test boshlash"""
        serializer = QuizStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subject_id = serializer.validated_data['subject_id']
        questions_count = serializer.validated_data['questions_count']
        
        # Student profilini olish
        try:
            from apps.students.models import Student
            student = Student.objects.get(user=request.user, deleted_at__isnull=True)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Siz student emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Fandan tasodifiy savollar tanlash
        subject = Subject.objects.get(id=subject_id)
        all_questions = list(
            Question.objects.filter(
                subject_id=subject_id,
                deleted_at__isnull=True
            ).values_list('id', flat=True)
        )
        
        if len(all_questions) < questions_count:
            questions_count = len(all_questions)
        
        if questions_count == 0:
            return Response(
                {'detail': 'Bu fanda savollar topilmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        selected_question_ids = random.sample(all_questions, questions_count)
        
        # Test sessiyasini yaratish
        quiz = Quiz.objects.create(
            student=student,
            subject=subject,
            title=f"{subject.name} testi - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            total_questions=questions_count
        )
        
        # Savollarni olish
        questions = Question.objects.filter(
            id__in=selected_question_ids,
            deleted_at__isnull=True
        ).prefetch_related('answers')
        
        questions_data = QuestionForQuizSerializer(questions, many=True).data
        
        return Response({
            'quiz_id': quiz.id,
            'subject': SubjectListSerializer(subject).data,
            'total_questions': questions_count,
            'questions': questions_data,
            'started_at': quiz.started_at
        }, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Javob yuborish",
        description="Savolga javob yuborish",
        tags=["Testlar"],
        request=QuizSubmitAnswerSerializer,
        responses={200: StudentAnswerDetailSerializer}
    )
    @action(detail=False, methods=['post'])
    def submit_answer(self, request):
        """Javob yuborish"""
        serializer = QuizSubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quiz_id = serializer.validated_data['quiz_id']
        question_id = serializer.validated_data['question_id']
        answer_id = serializer.validated_data['answer_id']
        time_taken = serializer.validated_data['time_taken']
        
        # Test sessiyasini tekshirish
        try:
            quiz = Quiz.objects.get(id=quiz_id, deleted_at__isnull=True)
        except Quiz.DoesNotExist:
            return Response(
                {'detail': 'Test sessiyasi topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Test tugaganligini tekshirish
        if quiz.is_completed:
            return Response(
                {'detail': 'Test allaqachon tugatilgan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Student tekshirish
        if quiz.student.user != request.user:
            return Response(
                {'detail': 'Bu test sizga tegishli emas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Savol va javobni tekshirish
        try:
            question = Question.objects.get(id=question_id, deleted_at__isnull=True)
            answer = Answer.objects.get(id=answer_id, question=question, deleted_at__isnull=True)
        except (Question.DoesNotExist, Answer.DoesNotExist):
            return Response(
                {'detail': 'Savol yoki javob topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Allaqachon javob berilgan bo'lsa
        if StudentAnswer.objects.filter(
            quiz=quiz,
            question=question,
            deleted_at__isnull=True
        ).exists():
            return Response(
                {'detail': 'Bu savolga allaqachon javob berilgan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Javobni saqlash
        student_answer = StudentAnswer.objects.create(
            quiz=quiz,
            question=question,
            selected_answer=answer,
            time_taken=time_taken
        )
        
        # Statistikani yangilash
        if student_answer.is_correct:
            quiz.correct_answers += 1
        else:
            quiz.wrong_answers += 1
        quiz.save()
        
        response_serializer = StudentAnswerDetailSerializer(student_answer)
        return Response(response_serializer.data)
    
    @extend_schema(
        summary="Testni tugatish",
        description="Test sessiyasini tugatish va natijalarni hisoblash",
        tags=["Testlar"],
        responses={200: QuizDetailSerializer}
    )
    @action(detail=True, methods=['post'])
    def complete_quiz(self, request, pk=None):
        """Testni tugatish"""
        quiz = self.get_object()
        
        # Student tekshirish
        if quiz.student.user != request.user:
            return Response(
                {'detail': 'Bu test sizga tegishli emas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if quiz.is_completed:
            return Response(
                {'detail': 'Test allaqachon tugatilgan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Testni tugatish
        quiz.is_completed = True
        quiz.completed_at = timezone.now()
        quiz.calculate_results()
        
        # QuizAttempt statistikasini yangilash
        attempt, created = QuizAttempt.objects.get_or_create(
            student=quiz.student,
            subject=quiz.subject,
            defaults={'deleted_at': None}
        )
        
        attempt.total_attempts += 1
        attempt.total_questions_answered += quiz.total_questions
        attempt.total_correct += quiz.correct_answers
        attempt.total_wrong += quiz.wrong_answers
        attempt.last_attempt_date = timezone.now()
        
        # O'rtacha ballni hisoblash
        all_quizzes = Quiz.objects.filter(
            student=quiz.student,
            subject=quiz.subject,
            is_completed=True,
            deleted_at__isnull=True
        )
        attempt.average_score = all_quizzes.aggregate(Avg('score'))['score__avg'] or 0
        
        # Eng yaxshi ballni yangilash
        if quiz.score > attempt.best_score:
            attempt.best_score = quiz.score
        
        attempt.save()
        
        serializer = QuizDetailSerializer(quiz)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mening testlarim",
        description="Joriy foydalanuvchining barcha testlari",
        tags=["Testlar"]
    )
    @action(detail=False, methods=['get'])
    def my_quizzes(self, request):
        """Mening testlarim"""
        try:
            from apps.students.models import Student
            student = Student.objects.get(user=request.user, deleted_at__isnull=True)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Siz student emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        quizzes = self.get_queryset().filter(student=student)
        
        # Filterlash
        is_completed = request.query_params.get('is_completed')
        if is_completed is not None:
            is_completed = is_completed.lower() in ['true', '1', 'yes']
            quizzes = quizzes.filter(is_completed=is_completed)
        
        page = self.paginate_queryset(quizzes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Test statistikasi",
        description="Talabalarning test urinishlari statistikasi",
        tags=["Statistika"]
    ),
    retrieve=extend_schema(
        summary="Statistika tafsilotlari",
        description="Bitta statistika yozuvi haqida ma'lumot",
        tags=["Statistika"]
    ),
)
class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    QuizAttempt statistikasi
    
    Talabalarning test urinishlari statistikasi (faqat o'qish)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = QuizAttemptSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'subject']
    ordering_fields = ['total_attempts', 'average_score', 'best_score', 'last_attempt_date']
    ordering = ['-last_attempt_date']
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(
            deleted_at__isnull=True
        ).select_related('student__user', 'subject')
    
    @extend_schema(
        summary="Mening statistikam",
        description="Joriy foydalanuvchining test statistikasi",
        tags=["Statistika"]
    )
    @action(detail=False, methods=['get'])
    def my_statistics(self, request):
        """Mening statistikam"""
        try:
            from apps.students.models import Student
            student = Student.objects.get(user=request.user, deleted_at__isnull=True)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Siz student emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        statistics = self.get_queryset().filter(student=student)
        serializer = self.get_serializer(statistics, many=True)
        return Response(serializer.data)
