from rest_framework import serializers
from .models import Schedule, Lesson, Attendance, AttendanceStatistics
from apps.students.serializers import StudentListSerializer, TeacherListSerializer
from apps.quizzes.serializers import SubjectListSerializer


class ScheduleListSerializer(serializers.ModelSerializer):
    """Jadval ro'yxati uchun serializer"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'group', 'group_name', 'subject', 'subject_name',
            'teacher', 'teacher_name', 'day_of_week', 'start_time',
            'end_time', 'room', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.user.get_full_name()
        return None


class ScheduleDetailSerializer(serializers.ModelSerializer):
    """Jadval tafsiloti uchun serializer"""
    group = serializers.SerializerMethodField()
    subject = SubjectListSerializer(read_only=True)
    teacher = TeacherListSerializer(read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'group', 'subject', 'teacher', 'day_of_week',
            'start_time', 'end_time', 'room', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_group(self, obj):
        from apps.students.serializers import StudentGroupListSerializer
        return StudentGroupListSerializer(obj.group).data


class ScheduleCreateUpdateSerializer(serializers.ModelSerializer):
    """Jadval yaratish va yangilash uchun serializer"""
    
    class Meta:
        model = Schedule
        fields = [
            'group', 'subject', 'teacher', 'day_of_week',
            'start_time', 'end_time', 'room', 'is_active'
        ]
    
    def validate(self, data):
        """Vaqt validatsiyasi"""
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "Tugash vaqti boshlanish vaqtidan katta bo'lishi kerak"
                )
        return data


class LessonListSerializer(serializers.ModelSerializer):
    """Darslar ro'yxati uchun serializer"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'group', 'group_name', 'subject', 'subject_name',
            'teacher', 'teacher_name', 'date', 'start_time', 'end_time',
            'room', 'topic', 'status', 'auto_attendance_enabled',
            'attendance_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.user.get_full_name()
        return None
    
    def get_attendance_count(self, obj):
        """Davomat belgilangan talabalar soni"""
        return obj.attendances.filter(deleted_at__isnull=True).count()


class LessonDetailSerializer(serializers.ModelSerializer):
    """Dars tafsiloti uchun serializer"""
    group = serializers.SerializerMethodField()
    subject = SubjectListSerializer(read_only=True)
    teacher = TeacherListSerializer(read_only=True)
    related_quiz_subject = SubjectListSerializer(read_only=True)
    schedule = ScheduleListSerializer(read_only=True)
    attendance_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'schedule', 'group', 'subject', 'teacher', 'date',
            'start_time', 'end_time', 'room', 'topic', 'description',
            'status', 'related_quiz_subject', 'auto_attendance_enabled',
            'attendance_window_before', 'attendance_window_after',
            'attendance_stats', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_group(self, obj):
        from apps.students.serializers import StudentGroupListSerializer
        return StudentGroupListSerializer(obj.group).data
    
    def get_attendance_stats(self, obj):
        """Dars bo'yicha davomat statistikasi"""
        attendances = obj.attendances.filter(deleted_at__isnull=True)
        return {
            'total': attendances.count(),
            'present': attendances.filter(status='present').count(),
            'absent': attendances.filter(status='absent').count(),
            'late': attendances.filter(status='late').count(),
            'excused': attendances.filter(status='excused').count(),
        }


class LessonCreateSerializer(serializers.ModelSerializer):
    """Dars yaratish uchun serializer"""
    
    class Meta:
        model = Lesson
        fields = [
            'schedule', 'group', 'subject', 'teacher', 'date',
            'start_time', 'end_time', 'room', 'topic', 'description',
            'status', 'related_quiz_subject', 'auto_attendance_enabled',
            'attendance_window_before', 'attendance_window_after'
        ]
    
    def validate(self, data):
        """Validatsiya"""
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "Tugash vaqti boshlanish vaqtidan katta bo'lishi kerak"
                )
        return data


class LessonUpdateSerializer(serializers.ModelSerializer):
    """Dars yangilash uchun serializer"""
    
    class Meta:
        model = Lesson
        fields = [
            'teacher', 'start_time', 'end_time', 'room', 'topic',
            'description', 'status', 'related_quiz_subject',
            'auto_attendance_enabled', 'attendance_window_before',
            'attendance_window_after'
        ]


class AttendanceListSerializer(serializers.ModelSerializer):
    """Davomat ro'yxati uchun serializer"""
    student = StudentListSerializer(read_only=True)
    lesson_info = serializers.SerializerMethodField()
    marked_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'lesson', 'lesson_info', 'student', 'status',
            'marked_at', 'marked_by', 'marked_by_name', 'is_auto_marked',
            'related_quiz', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'marked_at', 'created_at', 'updated_at']
    
    def get_lesson_info(self, obj):
        return {
            'id': obj.lesson.id,
            'subject': obj.lesson.subject.name,
            'date': obj.lesson.date,
            'start_time': obj.lesson.start_time,
            'group': obj.lesson.group.name
        }
    
    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return obj.marked_by.get_full_name()
        return None


class AttendanceDetailSerializer(serializers.ModelSerializer):
    """Davomat tafsiloti uchun serializer"""
    student = StudentListSerializer(read_only=True)
    lesson = LessonDetailSerializer(read_only=True)
    marked_by_name = serializers.SerializerMethodField()
    related_quiz_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'lesson', 'student', 'status', 'marked_at',
            'marked_by', 'marked_by_name', 'is_auto_marked',
            'related_quiz', 'related_quiz_info', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'marked_at', 'created_at', 'updated_at']
    
    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return obj.marked_by.get_full_name()
        return None
    
    def get_related_quiz_info(self, obj):
        if obj.related_quiz:
            return {
                'id': obj.related_quiz.id,
                'title': obj.related_quiz.title,
                'score': obj.related_quiz.score,
                'percentage': obj.related_quiz.percentage
            }
        return None


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Davomat yaratish (qo'lda belgilash) uchun serializer"""
    
    class Meta:
        model = Attendance
        fields = ['lesson', 'student', 'status', 'notes']
    
    def validate(self, data):
        """Validatsiya"""
        lesson = data.get('lesson')
        student = data.get('student')
        
        # Student guruhi dars guruhi bilan mos kelishini tekshirish
        if student.group != lesson.group:
            raise serializers.ValidationError(
                "Talaba bu darsga qatnashmaydi (guruh mos kelmaydi)"
            )
        
        # Allaqachon davomat belgilangan bo'lsa
        if Attendance.objects.filter(
            lesson=lesson,
            student=student,
            deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError(
                "Bu talaba uchun davomat allaqachon belgilangan"
            )
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        return Attendance.objects.create(
            marked_by=request.user if request else None,
            is_auto_marked=False,
            **validated_data
        )


class AttendanceUpdateSerializer(serializers.ModelSerializer):
    """Davomat yangilash uchun serializer"""
    
    class Meta:
        model = Attendance
        fields = ['status', 'notes']


class AttendanceBulkCreateSerializer(serializers.Serializer):
    """Bir nechta talabaga davomat belgilash"""
    lesson_id = serializers.UUIDField(required=True)
    students_status = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="[{'student_id': 'uuid', 'status': 'present'}, ...]"
    )
    
    def validate_students_status(self, value):
        """Validatsiya"""
        for item in value:
            if 'student_id' not in item or 'status' not in item:
                raise serializers.ValidationError(
                    "Har bir element 'student_id' va 'status' fieldlariga ega bo'lishi kerak"
                )
            if item['status'] not in ['present', 'absent', 'late', 'excused']:
                raise serializers.ValidationError(
                    f"Noto'g'ri status: {item['status']}"
                )
        return value


class AttendanceStatisticsSerializer(serializers.ModelSerializer):
    """Davomat statistikasi serializer"""
    student = StudentListSerializer(read_only=True)
    subject = SubjectListSerializer(read_only=True)
    
    class Meta:
        model = AttendanceStatistics
        fields = [
            'id', 'student', 'subject', 'total_lessons',
            'present_count', 'absent_count', 'late_count',
            'excused_count', 'attendance_rate', 'last_updated'
        ]


class AttendanceReportSerializer(serializers.Serializer):
    """Davomat hisoboti uchun serializer"""
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    group_id = serializers.UUIDField(required=False)
    subject_id = serializers.UUIDField(required=False)
    student_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        """Validatsiya"""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError(
                "Boshlanish sanasi tugash sanasidan katta bo'lmasligi kerak"
            )
        return data
