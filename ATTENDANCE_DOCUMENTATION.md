# Davomat Tizimi - Avtomatik Test-Davomat Integratsiyasi

## Tizim Arxitekturasi

Davomat tizimi **4 ta asosiy model**dan iborat:

### 1. Schedule (Jadval)
- Takrorlanadigan darslar jadvali
- Masalan: Har dushanba 09:00 da Matematika darsi
- Guruh, fan, hafta kuni, vaqt

### 2. Lesson (Dars)
- Aniq dars sessiyasi (ma'lum kun va vaqt)
- Jadvалdan avtomatik yaratilishi mumkin
- Test bilan bog'lash imkoniyati
- Davomat oynasi sozlamalari

### 3. Attendance (Davomat)
- Talabaning aniq bir darsdagi davomat qaydi
- Qo'lda yoki avtomatik belgilanishi mumkin
- Test bilan bog'lanishi mumkin

### 4. AttendanceStatistics (Statistika)
- Har bir talabaning fan bo'yicha davomat statistikasi
- Avtomatik hisoblanadi

---

## 🚀 Avtomatik Davomat Mexanizmi

### Qanday ishlaydi?

1. **Student test topshiradi** (`Quiz.is_completed = True`)
2. **Signal ishga tushadi** (`post_save` signal)
3. **Bugungi darslar tekshiriladi**:
   - Guruh mos kelishi kerak
   - Fan mos kelishi kerak
   - Davomat oynasi ochiq bo'lishi kerak
4. **Davomat avtomatik belgilanadi**:
   - Status: `present` (keldi)
   - `is_auto_marked = True`
   - Test bilan bog'lanadi

### Davomat Oynasi

Har bir darsda sozlanadi:
- `attendance_window_before` - Darsdan necha daqiqa oldin (default: 30 daqiqa)
- `attendance_window_after` - Darsdan necha daqiqa keyin (default: 30 daqiqa)

Misol:
- Dars: 09:00 - 10:00
- Oyna: 08:30 - 10:30
- Agar student 08:45 da yoki 10:15 da test topshirsa, davomat olinadi ✅

---

## API Endpoints

### Jadval (Schedule)

#### Jadval yaratish
```http
POST /api/schedules/
```

```json
{
  "group": "uuid",
  "subject": "uuid",
  "teacher": "uuid",
  "day_of_week": "monday",
  "start_time": "09:00:00",
  "end_time": "10:30:00",
  "room": "101",
  "is_active": true
}
```

#### Guruh jadvali
```http
GET /api/schedules/by_group/?group_id={uuid}
```

---

### Darslar (Lessons)

#### Dars yaratish
```http
POST /api/lessons/
```

```json
{
  "group": "uuid",
  "subject": "uuid",
  "teacher": "uuid",
  "date": "2026-01-20",
  "start_time": "09:00:00",
  "end_time": "10:30:00",
  "room": "101",
  "topic": "Elektromagnetizm",
  "auto_attendance_enabled": true,
  "related_quiz_subject": "uuid",
  "attendance_window_before": 30,
  "attendance_window_after": 30
}
```

#### Jadvалdan darslar yaratish (Avtomatik)
```http
POST /api/lessons/generate_from_schedule/
```

```json
{
  "start_date": "2026-01-20",
  "end_date": "2026-01-26",
  "group_id": "uuid"
}
```

**Response:** Bir haftalik barcha darslar jadvаldan avtomatik yaratiladi

#### Bugungi darslar
```http
GET /api/lessons/today/?group_id={uuid}
```

#### Haftalik darslar
```http
GET /api/lessons/this_week/?group_id={uuid}
```

---

### Davomat (Attendance)

#### Qo'lda davomat belgilash
```http
POST /api/attendance/
```

```json
{
  "lesson": "uuid",
  "student": "uuid",
  "status": "present",
  "notes": "Vaqtida keldi"
}
```

**Status variantlari:**
- `present` - Keldi
- `absent` - Kelmadi
- `late` - Kech qoldi
- `excused` - Sababli

#### Bir nechta talabaga davomat belgilash
```http
POST /api/attendance/bulk_create/
```

```json
{
  "lesson_id": "uuid",
  "students_status": [
    {
      "student_id": "uuid",
      "status": "present"
    },
    {
      "student_id": "uuid",
      "status": "late",
      "notes": "10 daqiqa kech qoldi"
    },
    {
      "student_id": "uuid",
      "status": "absent"
    }
  ]
}
```

#### Mening davomatim
```http
GET /api/attendance/my_attendance/
```

**Query Parameters:**
- `start_date` - Boshlanish sanasi
- `end_date` - Tugash sanasi

---

### Statistika

#### Mening statistikam
```http
GET /api/attendance-statistics/my_statistics/
```

**Response:**
```json
[
  {
    "id": "uuid",
    "student": {...},
    "subject": {
      "id": "uuid",
      "name": "Elektromagnetizm"
    },
    "total_lessons": 20,
    "present_count": 18,
    "absent_count": 1,
    "late_count": 1,
    "excused_count": 0,
    "attendance_rate": 90.0,
    "last_updated": "2026-01-19T15:00:00Z"
  }
]
```

#### Davomat hisoboti
```http
POST /api/attendance-statistics/report/
```

```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-31",
  "group_id": "uuid",
  "subject_id": "uuid"
}
```

**Response:**
```json
{
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "summary": {
    "total_records": 100,
    "present": 85,
    "absent": 10,
    "late": 5,
    "excused": 0,
    "attendance_rate": 85.0
  }
}
```

---

## Frontend Uchun Workflow

### 1. Admin: Jadval yaratish

```javascript
// Haftalik jadval yaratish
const schedules = [
  {
    group: groupId,
    subject: mathSubjectId,
    day_of_week: 'monday',
    start_time: '09:00:00',
    end_time: '10:30:00',
  },
  {
    group: groupId,
    subject: physicsSubjectId,
    day_of_week: 'tuesday',
    start_time: '11:00:00',
    end_time: '12:30:00',
  }
];

for (const schedule of schedules) {
  await api.post('/api/schedules/', schedule);
}
```

### 2. Admin: Bir haftalik darslar yaratish

```javascript
// Jadvаldan avtomatik darslar yaratish
const response = await api.post('/api/lessons/generate_from_schedule/', {
  start_date: '2026-01-20',
  end_date: '2026-01-26',
  group_id: groupId
});

console.log(`${response.data.created_count} ta dars yaratildi`);
```

### 3. Student: Test topshirish

```javascript
// 1. Test boshlash
const quiz = await api.post('/api/quizzes/start_quiz/', {
  subject_id: subjectId,
  questions_count: 10
});

// 2. Javoblar yuborish
for (const question of quiz.questions) {
  await api.post('/api/quizzes/submit_answer/', {
    quiz_id: quiz.quiz_id,
    question_id: question.id,
    answer_id: selectedAnswerId,
    time_taken: 15
  });
}

// 3. Testni tugatish
const result = await api.post(`/api/quizzes/${quiz.quiz_id}/complete_quiz/`);

// ✅ AVTOMATIK davomat belgilandi!
// Signal ishga tushib, agar bugun dars bo'lsa va vaqt mos kelsa davomat avtomatik olinadi
```

### 4. Student: Davomatni ko'rish

```javascript
// Mening davomatim
const attendance = await api.get('/api/attendance/my_attendance/', {
  params: {
    start_date: '2026-01-01',
    end_date: '2026-01-31'
  }
});

// Statistikam
const stats = await api.get('/api/attendance-statistics/my_statistics/');

stats.forEach(stat => {
  console.log(`${stat.subject.name}: ${stat.attendance_rate}%`);
});
```

### 5. Teacher: Davomat belgilash (qo'lda)

```javascript
// Bugungi darsni olish
const todayLessons = await api.get('/api/lessons/today/', {
  params: { group_id: groupId }
});

const lesson = todayLessons[0];

// Bir nechta talabaga davomat belgilash
await api.post('/api/attendance/bulk_create/', {
  lesson_id: lesson.id,
  students_status: [
    { student_id: student1Id, status: 'present' },
    { student_id: student2Id, status: 'late' },
    { student_id: student3Id, status: 'absent' }
  ]
});
```

---

## Afzalliklar

✅ **Avtomatik** - Student test topshirsa, davomat avtomatik olinadi
✅ **Ikki tomonlama** - Qo'lda ham belgilash mumkin
✅ **Moslashuvchan** - Davomat oynasi har bir dars uchun sozlanadi
✅ **Statistika** - Avtomatik hisoblangan davomat foizi
✅ **Hisobot** - Ma'lum davr uchun to'liq hisobot
✅ **Jadval** - Takrorlanadigan jadvaldan avtomatik darslar yaratish
✅ **Integratsiya** - Test tizimi bilan to'liq integratsiya

---

## Misol Senарiy

**Dushanba, 20-Yanvar 2026, 09:00**

1. **Admin** jadval yaratgan:
   - 10-A guruh, Elektromagnetizm, Dushanba 09:00-10:30

2. **Admin** darslar yaratgan:
   - 20-Yanvar, 09:00-10:30, 10-A, Elektromagnetizm

3. **Student Ali** 08:50 da test boshladi:
   - Elektromagnetizm fani
   - 10 ta savol

4. **Student Ali** 09:05 da testni tugatdi:
   - Natija: 8/10 to'g'ri
   - ✅ **Avtomatik davomat olinadi!**
   - Chunki:
     - Guruh mos keladi ✓
     - Fan mos keladi ✓
     - Vaqt oynada (08:30-11:00) ✓

5. **Teacher** davomatni ko'radi:
   - Ali: Keldi (test orqali avtomatik)
   - Vali: (hali belgilanmagan)

6. **Teacher** qolgan talabalarni qo'lda belgilaydi:
   - Vali: Keldi
   - Sardor: Kech qoldi

---

## Integration Example (React/Next.js)

```typescript
// services/attendance.service.ts
export class AttendanceService {
  // Davomat olinganligini tekshirish
  async checkTodayAttendance() {
    const today = new Date().toISOString().split('T')[0];
    const response = await api.get('/api/attendance/my_attendance/', {
      params: {
        start_date: today,
        end_date: today
      }
    });
    return response.data.results;
  }
  
  // Test topshirgandan keyin davomatni refresh qilish
  async refreshAttendanceAfterQuiz(quizId: string) {
    // Biroz kutish (signal ishlashi uchun)
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Davomatni yangilash
    const attendance = await this.checkTodayAttendance();
    return attendance;
  }
}

// components/QuizComplete.tsx
const QuizComplete = ({ quiz }) => {
  const [attendance, setAttendance] = useState(null);
  
  useEffect(() => {
    if (quiz.is_completed) {
      // Davomat avtomatik olinganligini tekshirish
      attendanceService.refreshAttendanceAfterQuiz(quiz.id)
        .then(att => {
          if (att.length > 0) {
            setAttendance(att[0]);
          }
        });
    }
  }, [quiz]);
  
  return (
    <div>
      <h2>Test tugadi!</h2>
      <p>Ball: {quiz.score}/{quiz.total_questions}</p>
      
      {attendance && (
        <div className="success-message">
          ✅ Davomat avtomatik olinд!
          <p>Dars: {attendance.lesson_info.subject}</p>
          <p>Holat: {attendance.status}</p>
        </div>
      )}
    </div>
  );
};
```

---

## Xavfsizlik

- ✅ JWT authentication
- ✅ Student faqat o'z davomatini ko'radi
- ✅ Teacher o'z guruhining davomatini boshqaradi
- ✅ Bir darsga bir marta davomat
- ✅ Guruh validatsiyasi

---

## Qo'shimcha Imkoniyatlar

1. **Push notification** - Dars boshlanganda xabar yuborish
2. **QR kod** - Sinfda QR kod skanerlash orqali davomat
3. **Geolocation** - Joylashuv orqali davomat
4. **Face recognition** - Yuz tanish orqali davomat
5. **Export** - Excel/PDF formatda hisobot

Hozirda **Test orqali avtomatik davomat** to'liq ishlamoqda! 🎉
