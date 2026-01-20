from rest_framework import serializers
from .models import Subject, Question, Answer, Quiz, StudentAnswer, QuizAttempt
from apps.students.serializers import StudentListSerializer


class SubjectListSerializer(serializers.ModelSerializer):
    """Fanlar ro'yxati uchun serializer"""
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'order', 'questions_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_questions_count(self, obj):
        """Fandagi savollar soni"""
        return obj.questions.filter(deleted_at__isnull=True).count()


class SubjectDetailSerializer(serializers.ModelSerializer):
    """Fan tafsiloti uchun serializer"""
    questions_count = serializers.SerializerMethodField()
    total_quizzes = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'order', 'questions_count', 'total_quizzes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_questions_count(self, obj):
        return obj.questions.filter(deleted_at__isnull=True).count()
    
    def get_total_quizzes(self, obj):
        return obj.quizzes.filter(deleted_at__isnull=True).count()


class SubjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Fan yaratish va yangilash uchun serializer"""
    
    class Meta:
        model = Subject
        fields = ['name', 'description', 'order']


class AnswerSerializer(serializers.ModelSerializer):
    """Javob serializer"""
    
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'order']
        read_only_fields = ['id']


class AnswerListSerializer(serializers.ModelSerializer):
    """Javoblar ro'yxati (to'g'ri javob ko'rsatilmaydi)"""
    
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'order']
        read_only_fields = ['id']


class QuestionListSerializer(serializers.ModelSerializer):
    """Savollar ro'yxati uchun serializer"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    answers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'subject_name', 'question_text', 
            'time_limit', 'cooldown', 'difficulty', 'order',
            'answers_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_answers_count(self, obj):
        return obj.answers.filter(deleted_at__isnull=True).count()


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Savol tafsiloti uchun serializer (to'g'ri javob ko'rsatiladi - admin uchun)"""
    subject = SubjectListSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'question_text', 'time_limit', 
            'cooldown', 'difficulty', 'order', 'answers',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuestionForQuizSerializer(serializers.ModelSerializer):
    """Test uchun savol serializer (to'g'ri javob yashirilgan)"""
    answers = AnswerListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'time_limit', 'cooldown', 'answers']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Savol yaratish uchun serializer"""
    answers = AnswerSerializer(many=True, write_only=True)
    
    class Meta:
        model = Question
        fields = ['subject', 'question_text', 'time_limit', 'cooldown', 'difficulty', 'order', 'answers']
    
    def validate_answers(self, value):
        """Javoblar validatsiyasi"""
        if len(value) < 2:
            raise serializers.ValidationError("Kamida 2 ta javob bo'lishi kerak")
        
        correct_answers = [ans for ans in value if ans.get('is_correct')]
        if len(correct_answers) != 1:
            raise serializers.ValidationError("Faqat 1 ta to'g'ri javob bo'lishi kerak")
        
        return value
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        
        return question


class QuestionUpdateSerializer(serializers.ModelSerializer):
    """Savol yangilash uchun serializer"""
    
    class Meta:
        model = Question
        fields = ['question_text', 'time_limit', 'cooldown', 'difficulty', 'order']


class QuizListSerializer(serializers.ModelSerializer):
    """Test sessiyalari ro'yxati uchun serializer"""
    student = StudentListSerializer(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'student', 'subject', 'subject_name', 'title',
            'started_at', 'completed_at', 'is_completed',
            'total_questions', 'correct_answers', 'wrong_answers',
            'score', 'percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuizDetailSerializer(serializers.ModelSerializer):
    """Test sessiyasi tafsiloti uchun serializer"""
    student = StudentListSerializer(read_only=True)
    subject = SubjectListSerializer(read_only=True)
    student_answers = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'student', 'subject', 'title',
            'started_at', 'completed_at', 'is_completed',
            'total_questions', 'correct_answers', 'wrong_answers',
            'score', 'percentage', 'student_answers', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_student_answers(self, obj):
        answers = obj.student_answers.filter(deleted_at__isnull=True).select_related(
            'question', 'selected_answer'
        )
        return StudentAnswerDetailSerializer(answers, many=True).data


class QuizCreateSerializer(serializers.ModelSerializer):
    """Test sessiyasi yaratish uchun serializer"""
    student_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Quiz
        fields = ['student_id', 'subject', 'title', 'total_questions']
    
    def create(self, validated_data):
        from apps.students.models import Student
        student_id = validated_data.pop('student_id')
        student = Student.objects.get(id=student_id)
        return Quiz.objects.create(student=student, **validated_data)


class StudentAnswerSerializer(serializers.ModelSerializer):
    """Talaba javobi serializer"""
    
    class Meta:
        model = StudentAnswer
        fields = ['quiz', 'question', 'selected_answer', 'time_taken']
    
    def validate(self, data):
        """Validatsiya"""
        quiz = data.get('quiz')
        question = data.get('question')
        
        # Savol fan bilan mos kelishini tekshirish
        if question.subject != quiz.subject:
            raise serializers.ValidationError("Savol test faniga mos kelmaydi")
        
        # Allaqachon javob berilgan bo'lsa
        if StudentAnswer.objects.filter(
            quiz=quiz, 
            question=question,
            deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError("Bu savolga allaqachon javob berilgan")
        
        return data


class StudentAnswerDetailSerializer(serializers.ModelSerializer):
    """Talaba javobi tafsiloti serializer"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    selected_answer_text = serializers.CharField(source='selected_answer.answer_text', read_only=True)
    correct_answer = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAnswer
        fields = [
            'id', 'question', 'question_text', 
            'selected_answer', 'selected_answer_text',
            'correct_answer', 'is_correct', 'time_taken', 'answered_at'
        ]
    
    def get_correct_answer(self, obj):
        """To'g'ri javobni olish"""
        correct = obj.question.answers.filter(
            is_correct=True,
            deleted_at__isnull=True
        ).first()
        if correct:
            return {
                'id': correct.id,
                'answer_text': correct.answer_text
            }
        return None


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Test urinishlari statistikasi serializer"""
    student = StudentListSerializer(read_only=True)
    subject = SubjectListSerializer(read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student', 'subject', 'total_attempts',
            'total_questions_answered', 'total_correct', 'total_wrong',
            'average_score', 'best_score', 'success_rate', 'last_attempt_date'
        ]
    
    def get_success_rate(self, obj):
        """Muvaffaqiyat foizi"""
        if obj.total_questions_answered > 0:
            return round((obj.total_correct / obj.total_questions_answered) * 100, 2)
        return 0.0


class QuizStartSerializer(serializers.Serializer):
    """Test boshlash uchun serializer"""
    subject_id = serializers.UUIDField(required=True)
    questions_count = serializers.IntegerField(default=10, min_value=1, max_value=50)
    
    def validate_subject_id(self, value):
        """Fan mavjudligini tekshirish"""
        try:
            Subject.objects.get(id=value, deleted_at__isnull=True)
            return value
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Fan topilmadi")


class QuizSubmitAnswerSerializer(serializers.Serializer):
    """Javob yuborish uchun serializer"""
    quiz_id = serializers.UUIDField(required=True)
    question_id = serializers.UUIDField(required=True)
    answer_id = serializers.UUIDField(required=True)
    time_taken = serializers.IntegerField(required=True, min_value=0)
