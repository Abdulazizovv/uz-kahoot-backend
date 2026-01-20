from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.utils import timezone

from .models import StudentGroup, Student, Teacher
from .serializers import (
    StudentGroupListSerializer,
    StudentGroupDetailSerializer,
    StudentGroupCreateUpdateSerializer,
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
    TeacherListSerializer,
    TeacherDetailSerializer,
    TeacherCreateSerializer,
    TeacherUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Guruhlar ro'yxati",
        description="Barcha talabalar guruhlarini ro'yxatini olish",
        tags=["Guruhlar"]
    ),
    retrieve=extend_schema(
        summary="Guruh tafsilotlari",
        description="Bitta guruh haqida to'liq ma'lumot olish",
        tags=["Guruhlar"]
    ),
    create=extend_schema(
        summary="Yangi guruh yaratish",
        description="Yangi talabalar guruhi yaratish",
        tags=["Guruhlar"]
    ),
    update=extend_schema(
        summary="Guruhni yangilash",
        description="Mavjud guruh ma'lumotlarini to'liq yangilash",
        tags=["Guruhlar"]
    ),
    partial_update=extend_schema(
        summary="Guruhni qisman yangilash",
        description="Guruh ma'lumotlarini qisman yangilash",
        tags=["Guruhlar"]
    ),
    destroy=extend_schema(
        summary="Guruhni o'chirish",
        description="Guruhni soft delete qilish (deleted_at ni o'rnatish)",
        tags=["Guruhlar"]
    ),
)
class StudentGroupViewSet(viewsets.ModelViewSet):
    """
    StudentGroup CRUD operations
    
    Barcha guruhlar bilan ishlash uchun API endpoints:
    - GET /api/groups/ - ro'yxat
    - POST /api/groups/ - yangi guruh yaratish
    - GET /api/groups/{id}/ - bitta guruh
    - PUT /api/groups/{id}/ - yangilash
    - PATCH /api/groups/{id}/ - qisman yangilash
    - DELETE /api/groups/{id}/ - soft delete
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade']
    search_fields = ['name']
    ordering_fields = ['name', 'grade', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Faqat o'chirilmagan guruhlarni qaytarish"""
        return StudentGroup.objects.filter(deleted_at__isnull=True)
    
    def get_serializer_class(self):
        """Actionga qarab serializer tanlash"""
        if self.action == 'retrieve':
            return StudentGroupDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return StudentGroupCreateUpdateSerializer
        return StudentGroupListSerializer
    
    def perform_destroy(self, instance):
        """Soft delete - deleted_at ni o'rnatish"""
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="Guruh statistikasi",
        description="Guruhdagi studentlar soni va boshqa statistik ma'lumotlar",
        tags=["Guruhlar"],
        responses={200: {
            'type': 'object',
            'properties': {
                'students_count': {'type': 'integer'},
                'active_students': {'type': 'integer'},
                'group_info': {'type': 'object'}
            }
        }}
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Guruh statistikasi"""
        group = self.get_object()
        students = group.student_set.filter(deleted_at__isnull=True)
        
        return Response({
            'students_count': students.count(),
            'active_students': students.filter(user__is_active=True).count(),
            'group_info': {
                'name': group.name,
                'grade': group.grade,
                'created_at': group.created_at,
            }
        })


@extend_schema_view(
    list=extend_schema(
        summary="Studentlar ro'yxati",
        description="Barcha studentlarning ro'yxatini olish",
        tags=["Studentlar"]
    ),
    retrieve=extend_schema(
        summary="Student tafsilotlari",
        description="Bitta student haqida to'liq ma'lumot olish",
        tags=["Studentlar"]
    ),
    create=extend_schema(
        summary="Yangi student yaratish",
        description="Yangi student ro'yxatdan o'tkazish",
        tags=["Studentlar"]
    ),
    update=extend_schema(
        summary="Studentni yangilash",
        description="Student ma'lumotlarini to'liq yangilash",
        tags=["Studentlar"]
    ),
    partial_update=extend_schema(
        summary="Studentni qisman yangilash",
        description="Student ma'lumotlarini qisman yangilash",
        tags=["Studentlar"]
    ),
    destroy=extend_schema(
        summary="Studentni o'chirish",
        description="Studentni soft delete qilish",
        tags=["Studentlar"]
    ),
)
class StudentViewSet(viewsets.ModelViewSet):
    """
    Student CRUD operations
    
    Barcha studentlar bilan ishlash uchun API endpoints:
    - GET /api/students/ - ro'yxat
    - POST /api/students/ - yangi student
    - GET /api/students/{id}/ - bitta student
    - PUT /api/students/{id}/ - yangilash
    - PATCH /api/students/{id}/ - qisman yangilash
    - DELETE /api/students/{id}/ - soft delete
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['group', 'group__grade']
    search_fields = ['user__first_name', 'user__last_name', 'user__phone_number', 'address']
    ordering_fields = ['created_at', 'date_of_birth', 'user__first_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Faqat o'chirilmagan studentlarni qaytarish"""
        return Student.objects.filter(
            deleted_at__isnull=True
        ).select_related('user', 'group')
    
    def get_serializer_class(self):
        """Actionga qarab serializer tanlash"""
        if self.action == 'retrieve':
            return StudentDetailSerializer
        elif self.action == 'create':
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        return StudentListSerializer
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="Student profili",
        description="Joriy foydalanuvchining student profili",
        tags=["Studentlar"]
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Joriy userning student profili"""
        try:
            student = Student.objects.select_related('user', 'group').get(
                user=request.user,
                deleted_at__isnull=True
            )
            serializer = StudentDetailSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Siz student emassiz'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Guruh bo'yicha studentlar",
        description="Ma'lum bir guruhdagi barcha studentlar",
        tags=["Studentlar"],
        parameters=[
            OpenApiParameter(
                name='group_id',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Guruh ID (UUID)',
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_group(self, request):
        """Guruh bo'yicha studentlar"""
        group_id = request.query_params.get('group_id')
        if not group_id:
            return Response(
                {'detail': 'group_id parametri talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        students = self.get_queryset().filter(group_id=group_id)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="O'qituvchilar ro'yxati",
        description="Barcha o'qituvchilar ro'yxatini olish",
        tags=["O'qituvchilar"]
    ),
    retrieve=extend_schema(
        summary="O'qituvchi tafsilotlari",
        description="Bitta o'qituvchi haqida to'liq ma'lumot",
        tags=["O'qituvchilar"]
    ),
    create=extend_schema(
        summary="Yangi o'qituvchi yaratish",
        description="Yangi o'qituvchi ro'yxatdan o'tkazish",
        tags=["O'qituvchilar"]
    ),
    update=extend_schema(
        summary="O'qituvchini yangilash",
        description="O'qituvchi ma'lumotlarini to'liq yangilash",
        tags=["O'qituvchilar"]
    ),
    partial_update=extend_schema(
        summary="O'qituvchini qisman yangilash",
        description="O'qituvchi ma'lumotlarini qisman yangilash",
        tags=["O'qituvchilar"]
    ),
    destroy=extend_schema(
        summary="O'qituvchini o'chirish",
        description="O'qituvchini soft delete qilish",
        tags=["O'qituvchilar"]
    ),
)
class TeacherViewSet(viewsets.ModelViewSet):
    """
    Teacher CRUD operations
    
    Barcha o'qituvchilar bilan ishlash uchun API endpoints:
    - GET /api/teachers/ - ro'yxat
    - POST /api/teachers/ - yangi o'qituvchi
    - GET /api/teachers/{id}/ - bitta o'qituvchi
    - PUT /api/teachers/{id}/ - yangilash
    - PATCH /api/teachers/{id}/ - qisman yangilash
    - DELETE /api/teachers/{id}/ - soft delete
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__phone_number', 'subjects']
    ordering_fields = ['created_at', 'experience_years', 'user__first_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Faqat o'chirilmagan o'qituvchilarni qaytarish"""
        return Teacher.objects.filter(
            deleted_at__isnull=True
        ).select_related('user')
    
    def get_serializer_class(self):
        """Actionga qarab serializer tanlash"""
        if self.action == 'retrieve':
            return TeacherDetailSerializer
        elif self.action == 'create':
            return TeacherCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeacherUpdateSerializer
        return TeacherListSerializer
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.deleted_at = timezone.now()
        instance.save()
    
    @extend_schema(
        summary="O'qituvchi profili",
        description="Joriy foydalanuvchining o'qituvchi profili",
        tags=["O'qituvchilar"]
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Joriy userning o'qituvchi profili"""
        try:
            teacher = Teacher.objects.select_related('user').get(
                user=request.user,
                deleted_at__isnull=True
            )
            serializer = TeacherDetailSerializer(teacher)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response(
                {'detail': 'Siz o\'qituvchi emassiz'},
                status=status.HTTP_404_NOT_FOUND
            )
