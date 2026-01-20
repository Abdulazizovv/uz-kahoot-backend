from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.utils import timezone
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta

from .models import Schedule, Lesson, Attendance, AttendanceStatistics
from .serializers import (
    ScheduleListSerializer,
    ScheduleDetailSerializer,
    ScheduleCreateUpdateSerializer,
    LessonListSerializer,
    LessonDetailSerializer,
    LessonCreateSerializer,
    LessonUpdateSerializer,
    AttendanceListSerializer,
    AttendanceDetailSerializer,
    AttendanceCreateSerializer,
    AttendanceUpdateSerializer,
    AttendanceBulkCreateSerializer,
    AttendanceStatisticsSerializer,
    AttendanceReportSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Darslar jadvali ro'yxati",
        description="Barcha darslar jadvalini olish",
        tags=["Jadval"]
    ),
    retrieve=extend_schema(
        summary="Jadval tafsilotlari",
        description="Bitta jadval yozuvi haqida ma'lumot",
        tags=["Jadval"]
    ),
    create=extend_schema(
        summary="Yangi jadval yaratish",
        description="Yangi dars jadvali qo'shish",
        tags=["Jadval"]
    ),
    update=extend_schema(
        summary="Jadvalni yangilash",
        description="Jadval ma'lumotlarini yangilash",
        tags=["Jadval"]
    ),
    partial_update=extend_schema(
        summary="Jadvalni qisman yangilash",
        description="Jadval ma'lumotlarini qisman yangilash",
        tags=["Jadval"]
    ),
    destroy=extend_schema(
        summary="Jadvalni o'chirish",
        description="Jadvalni soft delete qilish",
        tags=["Jadval"]
    ),
)
class ScheduleViewSet(viewsets.ModelViewSet):
    """Darslar jadvali CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['group', 'subject', 'teacher', 'day_of_week', 'is_active']
    search_fields = ['group__name', 'subject__name', 'room']
    ordering_fields = ['day_of_week', 'start_time', 'created_at']
    ordering = ['day_of_week', 'start_time']
    
    def get_queryset(self):
        return Schedule.objects.filter(
            deleted_at__isnull=True
        ).select_related('group', 'subject', 'teacher__user')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ScheduleDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ScheduleCreateUpdateSerializer
        return ScheduleListSerializer
    
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="Guruh jadvali",
        description="Ma'lum bir guruhning haftalik darslar jadvali",
        tags=["Jadval"],
        parameters=[
            OpenApiParameter(name='group_id', type=str, location=OpenApiParameter.QUERY, required=True)
        ]
    )
    @action(detail=False, methods=['get'])
    def by_group(self, request):
        """Guruh bo'yicha jadval"""
        group_id = request.query_params.get('group_id')
        if not group_id:
            return Response(
                {'detail': 'group_id parametri talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        schedules = self.get_queryset().filter(group_id=group_id)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Darslar ro'yxati",
        description="Barcha darslar ro'yxatini olish",
        tags=["Darslar"]
    ),
    retrieve=extend_schema(
        summary="Dars tafsilotlari",
        description="Bitta dars haqida to'liq ma'lumot",
        tags=["Darslar"]
    ),
    create=extend_schema(
        summary="Yangi dars yaratish",
        description="Yangi dars sessiyasini qo'shish",
        tags=["Darslar"]
    ),
    update=extend_schema(
        summary="Darsni yangilash",
        description="Dars ma'lumotlarini yangilash",
        tags=["Darslar"]
    ),
    partial_update=extend_schema(
        summary="Darsni qisman yangilash",
        description="Dars ma'lumotlarini qisman yangilash",
        tags=["Darslar"]
    ),
    destroy=extend_schema(
        summary="Darsni o'chirish",
        description="Darsni soft delete qilish",
        tags=["Darslar"]
    ),
)
class LessonViewSet(viewsets.ModelViewSet):
    """Darslar CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['group', 'subject', 'teacher', 'date', 'status', 'auto_attendance_enabled']
    search_fields = ['topic', 'description', 'group__name', 'subject__name']
    ordering_fields = ['date', 'start_time', 'created_at']
    ordering = ['-date', '-start_time']
    
    def get_queryset(self):
        return Lesson.objects.filter(
            deleted_at__isnull=True
        ).select_related('group', 'subject', 'teacher__user', 'schedule', 'related_quiz_subject')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        elif self.action == 'create':
            return LessonCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LessonUpdateSerializer
        return LessonListSerializer
    
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="Bugungi darslar",
        description="Bugungi kun uchun rejalashtirilgan darslar",
        tags=["Darslar"]
    )
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Bugungi darslar"""
        today = timezone.now().date()
        lessons = self.get_queryset().filter(date=today)
        
        # Guruh bo'yicha filter
        group_id = request.query_params.get('group_id')
        if group_id:
            lessons = lessons.filter(group_id=group_id)
        
        serializer = self.get_serializer(lessons, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Haftalik darslar",
        description="Joriy hafta uchun darslar",
        tags=["Darslar"],
        parameters=[
            OpenApiParameter(name='group_id', type=str, location=OpenApiParameter.QUERY, required=False)
        ]
    )
    @action(detail=False, methods=['get'])
    def this_week(self, request):
        """Haftalik darslar"""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        lessons = self.get_queryset().filter(
            date__gte=week_start,
            date__lte=week_end
        )
        
        group_id = request.query_params.get('group_id')
        if group_id:
            lessons = lessons.filter(group_id=group_id)
        
        serializer = self.get_serializer(lessons, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Jadvldan darslar yaratish",
        description="Ma'lum bir hafta uchun jadvaldan darslarni avtomatik yaratish",
        tags=["Darslar"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'start_date': {'type': 'string', 'format': 'date'},
                    'end_date': {'type': 'string', 'format': 'date'},
                    'group_id': {'type': 'string', 'format': 'uuid'}
                }
            }
        }
    )
    @action(detail=False, methods=['post'])
    def generate_from_schedule(self, request):
        """Jadvldan darslar yaratish"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        group_id = request.data.get('group_id')
        
        if not all([start_date, end_date, group_id]):
            return Response(
                {'detail': 'start_date, end_date va group_id talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Noto\'g\'ri sana formati (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guruhning jadvalini olish
        schedules = Schedule.objects.filter(
            group_id=group_id,
            is_active=True,
            deleted_at__isnull=True
        )
        
        created_lessons = []
        current_date = start_date
        
        while current_date <= end_date:
            day_name = current_date.strftime('%A').lower()
            
            # Shu kun uchun jadvallarni topish
            day_schedules = schedules.filter(day_of_week=day_name)
            
            for schedule in day_schedules:
                # Allaqachon yaratilgan dars bor yoki yo'qligini tekshirish
                if not Lesson.objects.filter(
                    group=schedule.group,
                    subject=schedule.subject,
                    date=current_date,
                    start_time=schedule.start_time,
                    deleted_at__isnull=True
                ).exists():
                    lesson = Lesson.objects.create(
                        schedule=schedule,
                        group=schedule.group,
                        subject=schedule.subject,
                        teacher=schedule.teacher,
                        date=current_date,
                        start_time=schedule.start_time,
                        end_time=schedule.end_time,
                        room=schedule.room,
                        related_quiz_subject=schedule.subject,
                        auto_attendance_enabled=True
                    )
                    created_lessons.append(lesson)
            
            current_date += timedelta(days=1)
        
        return Response({
            'created_count': len(created_lessons),
            'lessons': LessonListSerializer(created_lessons, many=True).data
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        summary="Davomat qaydlari ro'yxati",
        description="Barcha davomat qaydlarini olish",
        tags=["Davomat"]
    ),
    retrieve=extend_schema(
        summary="Davomat tafsilotlari",
        description="Bitta davomat qaydi haqida ma'lumot",
        tags=["Davomat"]
    ),
    create=extend_schema(
        summary="Davomat belgilash",
        description="Talaba uchun davomat belgilash (qo'lda)",
        tags=["Davomat"]
    ),
    update=extend_schema(
        summary="Davomatni yangilash",
        description="Davomat holatini yangilash",
        tags=["Davomat"]
    ),
    partial_update=extend_schema(
        summary="Davomatni qisman yangilash",
        description="Davomat holatini qisman yangilash",
        tags=["Davomat"]
    ),
    destroy=extend_schema(
        summary="Davomatni o'chirish",
        description="Davomat qaydini soft delete qilish",
        tags=["Davomat"]
    ),
)
class AttendanceViewSet(viewsets.ModelViewSet):
    """Davomat CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lesson', 'student', 'status', 'is_auto_marked', 'lesson__date', 'lesson__subject']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'notes']
    ordering_fields = ['marked_at', 'lesson__date', 'lesson__start_time']
    ordering = ['-marked_at']
    
    def get_queryset(self):
        return Attendance.objects.filter(
            deleted_at__isnull=True
        ).select_related('lesson__group', 'lesson__subject', 'student__user', 'marked_by', 'related_quiz')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AttendanceDetailSerializer
        elif self.action == 'create':
            return AttendanceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AttendanceUpdateSerializer
        return AttendanceListSerializer
    
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="Bir nechta talabaga davomat belgilash",
        description="Bir vaqtning o'zida bir nechta talabaga davomat belgilash",
        tags=["Davomat"],
        request=AttendanceBulkCreateSerializer
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bir nechta talabaga davomat belgilash"""
        serializer = AttendanceBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        lesson_id = serializer.validated_data['lesson_id']
        students_status = serializer.validated_data['students_status']
        
        try:
            lesson = Lesson.objects.get(id=lesson_id, deleted_at__isnull=True)
        except Lesson.DoesNotExist:
            return Response(
                {'detail': 'Dars topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from apps.students.models import Student
        created_attendances = []
        errors = []
        
        for item in students_status:
            try:
                student = Student.objects.get(id=item['student_id'], deleted_at__isnull=True)
                
                # Allaqachon davomat belgilangan bo'lsa
                if Attendance.objects.filter(
                    lesson=lesson,
                    student=student,
                    deleted_at__isnull=True
                ).exists():
                    errors.append({
                        'student_id': str(student.id),
                        'error': 'Davomat allaqachon belgilangan'
                    })
                    continue
                
                attendance = Attendance.objects.create(
                    lesson=lesson,
                    student=student,
                    status=item['status'],
                    marked_by=request.user,
                    is_auto_marked=False,
                    notes=item.get('notes', '')
                )
                created_attendances.append(attendance)
                
            except Student.DoesNotExist:
                errors.append({
                    'student_id': item['student_id'],
                    'error': 'Talaba topilmadi'
                })
        
        return Response({
            'created_count': len(created_attendances),
            'attendances': AttendanceListSerializer(created_attendances, many=True).data,
            'errors': errors
        }, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Mening davomatim",
        description="Joriy student uchun davomat qaydlari",
        tags=["Davomat"]
    )
    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """Mening davomatim"""
        try:
            from apps.students.models import Student
            student = Student.objects.get(user=request.user, deleted_at__isnull=True)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Siz student emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        attendances = self.get_queryset().filter(student=student)
        
        # Sana bo'yicha filter
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            attendances = attendances.filter(lesson__date__gte=start_date)
        if end_date:
            attendances = attendances.filter(lesson__date__lte=end_date)
        
        page = self.paginate_queryset(attendances)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(attendances, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Davomat statistikasi",
        description="Talabalarning davomat statistikasi",
        tags=["Statistika"]
    ),
    retrieve=extend_schema(
        summary="Statistika tafsilotlari",
        description="Bitta statistika yozuvi",
        tags=["Statistika"]
    ),
)
class AttendanceStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """Davomat statistikasi (faqat o'qish)"""
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceStatisticsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'subject']
    ordering_fields = ['attendance_rate', 'total_lessons', 'last_updated']
    ordering = ['-attendance_rate']
    
    def get_queryset(self):
        return AttendanceStatistics.objects.filter(
            deleted_at__isnull=True
        ).select_related('student__user', 'subject')
    
    @extend_schema(
        summary="Mening statistikam",
        description="Joriy student uchun davomat statistikasi",
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
    
    @extend_schema(
        summary="Davomat hisoboti",
        description="Ma'lum davr uchun davomat hisoboti",
        tags=["Statistika"],
        request=AttendanceReportSerializer
    )
    @action(detail=False, methods=['post'])
    def report(self, request):
        """Davomat hisoboti"""
        serializer = AttendanceReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        group_id = serializer.validated_data.get('group_id')
        subject_id = serializer.validated_data.get('subject_id')
        student_id = serializer.validated_data.get('student_id')
        
        # Davomat qaydlarini filter qilish
        attendances = Attendance.objects.filter(
            lesson__date__gte=start_date,
            lesson__date__lte=end_date,
            deleted_at__isnull=True
        )
        
        if group_id:
            attendances = attendances.filter(lesson__group_id=group_id)
        if subject_id:
            attendances = attendances.filter(lesson__subject_id=subject_id)
        if student_id:
            attendances = attendances.filter(student_id=student_id)
        
        # Statistikani hisoblash
        total_records = attendances.count()
        present_count = attendances.filter(status='present').count()
        absent_count = attendances.filter(status='absent').count()
        late_count = attendances.filter(status='late').count()
        excused_count = attendances.filter(status='excused').count()
        
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_records': total_records,
                'present': present_count,
                'absent': absent_count,
                'late': late_count,
                'excused': excused_count,
                'attendance_rate': round(attendance_rate, 2)
            }
        })
