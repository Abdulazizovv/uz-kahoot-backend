# Test/Quiz API Documentation

## Test Tizimi API

Ta'lim platformasining test tizimi to'liq CRUD operatsiyalari bilan.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Barcha endpointlar JWT token talab qiladi:
```
Authorization: Bearer {access_token}
```

---

## 1. Fanlar (Subjects)

### 1.1 Fanlar ro'yxati
```http
GET /api/subjects/
```

**Query Parameters:**
- `search` - Fan nomi yoki tavsifi bo'yicha qidiruv
- `ordering` - Tartiblash (name, order, created_at)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Elektromagnetizm",
    "description": "Elektromagnetizm fani bo'yicha test savollari",
    "order": 1,
    "questions_count": 13,
    "created_at": "2026-01-19T10:00:00Z",
    "updated_at": "2026-01-19T10:00:00Z"
  }
]
```

### 1.2 Fan tafsilotlari
```http
GET /api/subjects/{id}/
```

### 1.3 Yangi fan yaratish
```http
POST /api/subjects/
```

**Request Body:**
```json
{
  "name": "Fizika",
  "description": "Fizika fani",
  "order": 1
}
```

---

## 2. Savollar (Questions)

### 2.1 Savollar ro'yxati
```http
GET /api/questions/
```

**Query Parameters:**
- `subject` - Fan ID bo'yicha filter
- `difficulty` - Qiyinlik darajasi (easy, medium, hard)
- `search` - Savol matni bo'yicha qidiruv

**Response:**
```json
[
  {
    "id": "uuid",
    "subject": "uuid",
    "subject_name": "Elektromagnetizm",
    "question_text": "Magnitlar qanday turlarga bo'linadi?",
    "time_limit": 20,
    "cooldown": 5,
    "difficulty": "medium",
    "order": 1,
    "answers_count": 4,
    "created_at": "2026-01-19T10:00:00Z",
    "updated_at": "2026-01-19T10:00:00Z"
  }
]
```

### 2.2 Savol tafsilotlari (Admin uchun - to'g'ri javob ko'rsatiladi)
```http
GET /api/questions/{id}/
```

**Response:**
```json
{
  "id": "uuid",
  "subject": {...},
  "question_text": "Magnitlar qanday turlarga bo'linadi?",
  "time_limit": 20,
  "cooldown": 5,
  "difficulty": "medium",
  "order": 1,
  "answers": [
    {
      "id": "uuid",
      "answer_text": "Tabiiy magnitlar",
      "is_correct": false,
      "order": 0
    },
    {
      "id": "uuid",
      "answer_text": "Tabiiy va sun'iy magnitlar",
      "is_correct": true,
      "order": 2
    }
  ]
}
```

### 2.3 Yangi savol yaratish
```http
POST /api/questions/
```

**Request Body:**
```json
{
  "subject": "uuid",
  "question_text": "Test savoli?",
  "time_limit": 30,
  "cooldown": 5,
  "difficulty": "medium",
  "order": 1,
  "answers": [
    {
      "answer_text": "Javob 1",
      "is_correct": false,
      "order": 0
    },
    {
      "answer_text": "Javob 2",
      "is_correct": true,
      "order": 1
    }
  ]
}
```

**Validation:**
- Kamida 2 ta javob bo'lishi kerak
- Faqat 1 ta to'g'ri javob bo'lishi kerak

### 2.4 Fan bo'yicha savollar
```http
GET /api/questions/by_subject/?subject_id={uuid}
```

---

## 3. Test Sessiyalari (Quizzes)

### 3.1 Test boshlash
```http
POST /api/quizzes/start_quiz/
```

**Request Body:**
```json
{
  "subject_id": "uuid",
  "questions_count": 10
}
```

**Response:**
```json
{
  "quiz_id": "uuid",
  "subject": {
    "id": "uuid",
    "name": "Elektromagnetizm",
    "description": "...",
    "questions_count": 13
  },
  "total_questions": 10,
  "questions": [
    {
      "id": "uuid",
      "question_text": "Magnitlar qanday turlarga bo'linadi?",
      "time_limit": 20,
      "cooldown": 5,
      "answers": [
        {
          "id": "uuid",
          "answer_text": "Tabiiy magnitlar",
          "order": 0
        },
        {
          "id": "uuid",
          "answer_text": "Sun'iy magnitlar",
          "order": 1
        },
        {
          "id": "uuid",
          "answer_text": "Tabiiy va sun'iy magnitlar",
          "order": 2
        },
        {
          "id": "uuid",
          "answer_text": "TJY",
          "order": 3
        }
      ]
    }
  ],
  "started_at": "2026-01-19T10:00:00Z"
}
```

**Note:** 
- Savollar tasodifiy tanlanadi
- Javoблар ichida `is_correct` field yo'q (studentdan yashirilgan)
- Student sifatida autentifikatsiya qilingan bo'lishi kerak

### 3.2 Javob yuborish
```http
POST /api/quizzes/submit_answer/
```

**Request Body:**
```json
{
  "quiz_id": "uuid",
  "question_id": "uuid",
  "answer_id": "uuid",
  "time_taken": 15
}
```

**Response:**
```json
{
  "id": "uuid",
  "question": "uuid",
  "question_text": "Magnitlar qanday turlarga bo'linadi?",
  "selected_answer": "uuid",
  "selected_answer_text": "Tabiiy va sun'iy magnitlar",
  "correct_answer": {
    "id": "uuid",
    "answer_text": "Tabiiy va sun'iy magnitlar"
  },
  "is_correct": true,
  "time_taken": 15,
  "answered_at": "2026-01-19T10:01:00Z"
}
```

**Validation:**
- Test tugatilmagan bo'lishi kerak
- Har bir savolga faqat bir marta javob berish mumkin
- Savol va javob test faniga mos kelishi kerak

### 3.3 Testni tugatish
```http
POST /api/quizzes/{quiz_id}/complete_quiz/
```

**Response:**
```json
{
  "id": "uuid",
  "student": {...},
  "subject": {...},
  "title": "Elektromagnetizm testi - 2026-01-19 10:00",
  "started_at": "2026-01-19T10:00:00Z",
  "completed_at": "2026-01-19T10:15:00Z",
  "is_completed": true,
  "total_questions": 10,
  "correct_answers": 8,
  "wrong_answers": 2,
  "score": 8.0,
  "percentage": 80.0,
  "student_answers": [
    {
      "id": "uuid",
      "question_text": "...",
      "selected_answer_text": "...",
      "correct_answer": {...},
      "is_correct": true,
      "time_taken": 15
    }
  ]
}
```

**Note:** Test tugagandan keyin:
- Statistika avtomatik yangilanadi
- O'rtacha ball va eng yaxshi ball hisoblanadi

### 3.4 Mening testlarim
```http
GET /api/quizzes/my_quizzes/
```

**Query Parameters:**
- `is_completed` - true/false (tugatilgan yoki davom etayotgan)

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "student": {...},
      "subject": "uuid",
      "subject_name": "Elektromagnetizm",
      "title": "Elektromagnetizm testi",
      "started_at": "2026-01-19T10:00:00Z",
      "completed_at": "2026-01-19T10:15:00Z",
      "is_completed": true,
      "total_questions": 10,
      "correct_answers": 8,
      "wrong_answers": 2,
      "score": 8.0,
      "percentage": 80.0
    }
  ]
}
```

### 3.5 Test sessiyalari ro'yxati (Admin)
```http
GET /api/quizzes/
```

**Query Parameters:**
- `subject` - Fan ID
- `student` - Student ID
- `is_completed` - true/false

### 3.6 Test tafsilotlari
```http
GET /api/quizzes/{id}/
```

---

## 4. Statistika (Statistics)

### 4.1 Mening statistikam
```http
GET /api/statistics/my_statistics/
```

**Response:**
```json
[
  {
    "id": "uuid",
    "student": {...},
    "subject": {
      "id": "uuid",
      "name": "Elektromagnetizm",
      "questions_count": 13
    },
    "total_attempts": 5,
    "total_questions_answered": 50,
    "total_correct": 40,
    "total_wrong": 10,
    "average_score": 8.0,
    "best_score": 10.0,
    "success_rate": 80.0,
    "last_attempt_date": "2026-01-19T10:15:00Z"
  }
]
```

### 4.2 Barcha statistika (Admin)
```http
GET /api/statistics/
```

**Query Parameters:**
- `student` - Student ID
- `subject` - Fan ID
- `ordering` - Tartiblash (total_attempts, average_score, best_score, last_attempt_date)

---

## 5. Management Commands

### JSON fayldan savollarni import qilish

```bash
docker exec django python manage.py import_questions <json_file_path>
```

**JSON format:**
```json
{
  "subject": "Fan nomi",
  "questions": [
    {
      "question": "Savol matni?",
      "answers": [
        "Javob 1",
        "Javob 2",
        "Javob 3",
        "Javob 4"
      ],
      "solution": 2,
      "cooldown": 5,
      "time": 20
    }
  ]
}
```

**Misol:**
```bash
docker exec django python manage.py import_questions elektromagnetizm.json
```

---

## Test Oqimi (Workflow)

### Student uchun test topshirish jarayoni:

1. **Fanlarni ko'rish**
   ```
   GET /api/subjects/
   ```

2. **Test boshlash**
   ```
   POST /api/quizzes/start_quiz/
   {
     "subject_id": "uuid",
     "questions_count": 10
   }
   ```

3. **Har bir savolga javob berish**
   ```
   POST /api/quizzes/submit_answer/
   {
     "quiz_id": "uuid",
     "question_id": "uuid",
     "answer_id": "uuid",
     "time_taken": 15
   }
   ```

4. **Testni tugatish**
   ```
   POST /api/quizzes/{quiz_id}/complete_quiz/
   ```

5. **Natijalarni ko'rish**
   ```
   GET /api/quizzes/{quiz_id}/
   ```

6. **Umumiy statistikani ko'rish**
   ```
   GET /api/statistics/my_statistics/
   ```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Test allaqachon tugatilgan"
}
```

### 403 Forbidden
```json
{
  "detail": "Bu test sizga tegishli emas"
}
```

### 404 Not Found
```json
{
  "detail": "Test sessiyasi topilmadi"
}
```

---

## Swagger/OpenAPI Documentation

Interactive API documentation:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

---

## Xususiyatlar

✅ **Tasodifiy savollar** - Har bir test sessiyasida tasodifiy savollar tanlanadi
✅ **To'g'ri javobni yashirish** - Studentlar uchun to'g'ri javob ko'rsatilmaydi (test davomida)
✅ **Vaqt nazorati** - Har bir savol uchun vaqt chegarasi
✅ **Cooldown** - Savollar orasida kutish vaqti
✅ **Statistika** - Har bir fan bo'yicha to'liq statistika
✅ **Bir marta javob berish** - Har bir savolga faqat bir marta javob berish mumkin
✅ **Soft delete** - Ma'lumotlar bazadan o'chirilmaydi
✅ **UUID keys** - Barcha modellar UUID primary key ishlatadi
✅ **Auto statistics** - Test tugagandan keyin statistika avtomatik yangilanadi
