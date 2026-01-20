from rest_framework import serializers
from .models import StudentGroup, Student, Teacher
from auth.users.serializers import UserSerializer


class StudentGroupListSerializer(serializers.ModelSerializer):
    """StudentGroup ro'yxati uchun serializer"""
    students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentGroup
        fields = ['id', 'name', 'grade', 'students_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_students_count(self, obj):
        """Guruhdagi studentlar soni"""
        return obj.student_set.filter(deleted_at__isnull=True).count()


class StudentGroupDetailSerializer(serializers.ModelSerializer):
    """StudentGroup tafsiloti uchun serializer"""
    students_count = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentGroup
        fields = ['id', 'name', 'grade', 'students_count', 'students', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_students_count(self, obj):
        """Guruhdagi studentlar soni"""
        return obj.student_set.filter(deleted_at__isnull=True).count()
    
    def get_students(self, obj):
        """Guruhdagi barcha studentlar"""
        students = obj.student_set.filter(deleted_at__isnull=True).select_related('user')
        return StudentListSerializer(students, many=True).data


class StudentGroupCreateUpdateSerializer(serializers.ModelSerializer):
    """StudentGroup yaratish va yangilash uchun serializer"""
    
    class Meta:
        model = StudentGroup
        fields = ['name', 'grade']
    
    def validate_grade(self, value):
        """Sinf raqami validatsiyasi"""
        if value < 1 or value > 11:
            raise serializers.ValidationError("Sinf raqami 1 dan 11 gacha bo'lishi kerak")
        return value


class StudentListSerializer(serializers.ModelSerializer):
    """Student ro'yxati uchun serializer"""
    user = UserSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'full_name', 'group', 'group_name', 
            'date_of_birth', 'address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentDetailSerializer(serializers.ModelSerializer):
    """Student tafsiloti uchun serializer"""
    user = UserSerializer(read_only=True)
    group = StudentGroupListSerializer(read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'group', 'date_of_birth', 'age',
            'address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_age(self, obj):
        """Yoshni hisoblash"""
        if not obj.date_of_birth:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        age = today.year - obj.date_of_birth.year
        if today.month < obj.date_of_birth.month or (
            today.month == obj.date_of_birth.month and today.day < obj.date_of_birth.day
        ):
            age -= 1
        return age


class StudentCreateSerializer(serializers.ModelSerializer):
    """Student yaratish uchun serializer"""
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Student
        fields = ['user_id', 'group', 'date_of_birth', 'address']
    
    def validate_user_id(self, value):
        """User mavjudligini tekshirish"""
        from auth.users.models import User
        try:
            user = User.objects.get(id=value)
            if hasattr(user, 'student_profile'):
                raise serializers.ValidationError("Bu foydalanuvchi allaqachon student sifatida ro'yxatdan o'tgan")
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Foydalanuvchi topilmadi")
    
    def create(self, validated_data):
        user = validated_data.pop('user_id')
        return Student.objects.create(user=user, **validated_data)


class StudentUpdateSerializer(serializers.ModelSerializer):
    """Student yangilash uchun serializer"""
    
    class Meta:
        model = Student
        fields = ['group', 'date_of_birth', 'address']


class TeacherListSerializer(serializers.ModelSerializer):
    """Teacher ro'yxati uchun serializer"""
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'full_name', 'subjects', 
            'experience_years', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherDetailSerializer(serializers.ModelSerializer):
    """Teacher tafsiloti uchun serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'subjects', 'experience_years', 
            'bio', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherCreateSerializer(serializers.ModelSerializer):
    """Teacher yaratish uchun serializer"""
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Teacher
        fields = ['user_id', 'subjects', 'experience_years', 'bio']
    
    def validate_user_id(self, value):
        """User mavjudligini tekshirish"""
        from auth.users.models import User
        try:
            user = User.objects.get(id=value)
            if hasattr(user, 'teacher_profile'):
                raise serializers.ValidationError("Bu foydalanuvchi allaqachon o'qituvchi sifatida ro'yxatdan o'tgan")
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Foydalanuvchi topilmadi")
    
    def create(self, validated_data):
        user = validated_data.pop('user_id')
        return Teacher.objects.create(user=user, **validated_data)


class TeacherUpdateSerializer(serializers.ModelSerializer):
    """Teacher yangilash uchun serializer"""
    
    class Meta:
        model = Teacher
        fields = ['subjects', 'experience_years', 'bio']
