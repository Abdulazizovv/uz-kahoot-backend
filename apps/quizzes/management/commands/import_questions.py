import json
import os
from django.core.management.base import BaseCommand
from apps.quizzes.models import Subject, Question, Answer


class Command(BaseCommand):
    help = 'JSON fayldan test savollarini import qilish'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='JSON fayl yo\'li (masalan: elektromagnetizm.json)'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'Fayl topilmadi: {json_file}')
            )
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'JSON formatida xatolik: {e}')
            )
            return
        
        # Fan nomini olish
        subject_name = data.get('subject')
        if not subject_name:
            self.stdout.write(
                self.style.ERROR('JSON faylda "subject" maydoni topilmadi')
            )
            return
        
        # Fanni yaratish yoki olish
        subject, created = Subject.objects.get_or_create(
            name=subject_name,
            defaults={'description': f'{subject_name} fani bo\'yicha test savollari'}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Yangi fan yaratildi: {subject_name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Fan allaqachon mavjud: {subject_name}')
            )
        
        # Savollarni import qilish
        questions = data.get('questions', [])
        if not questions:
            self.stdout.write(
                self.style.ERROR('JSON faylda savollar topilmadi')
            )
            return
        
        imported_count = 0
        skipped_count = 0
        
        for idx, q_data in enumerate(questions, 1):
            question_text = q_data.get('question')
            answers_list = q_data.get('answers', [])
            solution_index = q_data.get('solution')
            cooldown = q_data.get('cooldown', 5)
            time_limit = q_data.get('time', 20)
            
            if not question_text or not answers_list or solution_index is None:
                self.stdout.write(
                    self.style.WARNING(f'Savol #{idx}: Ma\'lumotlar to\'liq emas, o\'tkazib yuborildi')
                )
                skipped_count += 1
                continue
            
            # Savolni yaratish
            question, q_created = Question.objects.get_or_create(
                subject=subject,
                question_text=question_text,
                defaults={
                    'time_limit': time_limit,
                    'cooldown': cooldown,
                    'order': idx,
                    'difficulty': 'medium'
                }
            )
            
            if not q_created:
                self.stdout.write(
                    self.style.WARNING(f'Savol #{idx}: Allaqachon mavjud, o\'tkazib yuborildi')
                )
                skipped_count += 1
                continue
            
            # Javoblarni yaratish
            for ans_idx, ans_text in enumerate(answers_list):
                is_correct = (ans_idx == solution_index)
                Answer.objects.create(
                    question=question,
                    answer_text=ans_text,
                    is_correct=is_correct,
                    order=ans_idx
                )
            
            imported_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ Savol #{idx} import qilindi')
            )
        
        # Yakuniy natija
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'\nImport yakunlandi!\n'
                f'Fan: {subject_name}\n'
                f'Import qilindi: {imported_count} ta savol\n'
                f'O\'tkazib yuborildi: {skipped_count} ta savol\n'
            )
        )
