# API Documentation - Education Platform

Bu hujjat Education Platform ning barcha API endpointlari haqida ma'lumot beradi.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Barcha protected endpointlar uchun JWT token kerak.

**Header:**
```
Authorization: Bearer {access_token}
```

## API Endpoints

### 1. Guruhlar (Student Groups)

#### 1.1 Guruhlar ro'yxati
```http
GET /api/groups/
```

**Query Parameters:**
- `grade` (integer, optional): Sinf raqami bo'yicha filter
- `search` (string, optional): Guruh nomi bo'yicha qidiruv
- `ordering` (string, optional): Tartiblash (name, grade, created_at)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "10-A sinf",
    "grade": 10,
    "students_count": 25,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  }
]
```

#### 1.2 Guruh tafsilotlari
```http
GET /api/groups/{id}/
```

**Response:**
```json
{
  "id": "uuid",
  "name": "10-A sinf",
  "grade": 10,
  "students_count": 25,
  "students": [
    {
      "id": "uuid",
      "full_name": "Aliyev Ali",
      "user": {...},
      "group_name": "10-A sinf",
      "date_of_birth": "2010-05-15",
      "address": "Toshkent shahar"
    }
  ],
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z"
}
```

#### 1.3 Yangi guruh yaratish
```http
POST /api/groups/
```

**Request Body:**
```json
{
  "name": "10-A sinf",
  "grade": 10
}
```

**Response:** `201 Created`

#### 1.4 Guruhni yangilash
```http
PUT /api/groups/{id}/
PATCH /api/groups/{id}/
```

**Request Body:**
```json
{
  "name": "10-B sinf",
  "grade": 10
}
```

#### 1.5 Guruhni o'chirish
```http
DELETE /api/groups/{id}/
```

**Response:** `204 No Content`

> **Note:** Soft delete amalga oshiriladi (deleted_at field o'rnatiladi)

#### 1.6 Guruh statistikasi
```http
GET /api/groups/{id}/statistics/
```

**Response:**
```json
{
  "students_count": 25,
  "active_students": 23,
  "group_info": {
    "name": "10-A sinf",
    "grade": 10,
    "created_at": "2026-01-15T10:00:00Z"
  }
}
```

---

### 2. Studentlar (Students)

#### 2.1 Studentlar ro'yxati
```http
GET /api/students/
```

**Query Parameters:**
- `group` (uuid, optional): Guruh ID bo'yicha filter
- `group__grade` (integer, optional): Sinf raqami bo'yicha filter
- `search` (string, optional): Ism, familiya, telefon yoki manzil bo'yicha qidiruv
- `ordering` (string, optional): Tartiblash (created_at, date_of_birth, user__first_name)

**Response:**
```json
[
  {
    "id": "uuid",
    "user": {
      "id": "uuid",
      "phone_number": "+998901234567",
      "first_name": "Ali",
      "last_name": "Aliyev",
      "is_active": true
    },
    "full_name": "Ali Aliyev",
    "group": "uuid",
    "group_name": "10-A sinf",
    "date_of_birth": "2010-05-15",
    "address": "Toshkent shahar",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  }
]
```

#### 2.2 Student tafsilotlari
```http
GET /api/students/{id}/
```

**Response:**
```json
{
  "id": "uuid",
  "user": {
    "id": "uuid",
    "phone_number": "+998901234567",
    "first_name": "Ali",
    "last_name": "Aliyev",
    "is_active": true
  },
  "group": {
    "id": "uuid",
    "name": "10-A sinf",
    "grade": 10,
    "students_count": 25
  },
  "date_of_birth": "2010-05-15",
  "age": 15,
  "address": "Toshkent shahar",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z"
}
```

#### 2.3 Yangi student yaratish
```http
POST /api/students/
```

**Request Body:**
```json
{
  "user_id": "uuid",
  "group": "uuid",
  "date_of_birth": "2010-05-15",
  "address": "Toshkent shahar"
}
```

**Response:** `201 Created`

#### 2.4 Studentni yangilash
```http
PUT /api/students/{id}/
PATCH /api/students/{id}/
```

**Request Body:**
```json
{
  "group": "uuid",
  "date_of_birth": "2010-05-15",
  "address": "Toshkent shahar, Yunusobod tumani"
}
```

#### 2.5 Studentni o'chirish
```http
DELETE /api/students/{id}/
```

**Response:** `204 No Content`

#### 2.6 Mening profilim (Student)
```http
GET /api/students/me/
```

Joriy autentifikatsiya qilingan foydalanuvchining student profilini qaytaradi.

**Response:**
```json
{
  "id": "uuid",
  "user": {...},
  "group": {...},
  "date_of_birth": "2010-05-15",
  "age": 15,
  "address": "Toshkent shahar"
}
```

#### 2.7 Guruh bo'yicha studentlar
```http
GET /api/students/by_group/?group_id={uuid}
```

**Query Parameters:**
- `group_id` (uuid, required): Guruh ID

**Response:** Studentlar ro'yxati

---

### 3. O'qituvchilar (Teachers)

#### 3.1 O'qituvchilar ro'yxati
```http
GET /api/teachers/
```

**Query Parameters:**
- `search` (string, optional): Ism, familiya, telefon yoki fanlar bo'yicha qidiruv
- `ordering` (string, optional): Tartiblash (created_at, experience_years, user__first_name)

**Response:**
```json
[
  {
    "id": "uuid",
    "user": {
      "id": "uuid",
      "phone_number": "+998901234567",
      "first_name": "Vali",
      "last_name": "Valiyev",
      "is_active": true
    },
    "full_name": "Vali Valiyev",
    "subjects": "Matematika, Fizika",
    "experience_years": 10,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  }
]
```

#### 3.2 O'qituvchi tafsilotlari
```http
GET /api/teachers/{id}/
```

**Response:**
```json
{
  "id": "uuid",
  "user": {
    "id": "uuid",
    "phone_number": "+998901234567",
    "first_name": "Vali",
    "last_name": "Valiyev",
    "is_active": true
  },
  "subjects": "Matematika, Fizika",
  "experience_years": 10,
  "bio": "10 yillik tajribaga ega o'qituvchi",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z"
}
```

#### 3.3 Yangi o'qituvchi yaratish
```http
POST /api/teachers/
```

**Request Body:**
```json
{
  "user_id": "uuid",
  "subjects": "Matematika, Fizika",
  "experience_years": 10,
  "bio": "10 yillik tajribaga ega o'qituvchi"
}
```

**Response:** `201 Created`

#### 3.4 O'qituvchini yangilash
```http
PUT /api/teachers/{id}/
PATCH /api/teachers/{id}/
```

**Request Body:**
```json
{
  "subjects": "Matematika, Fizika, Astronomiya",
  "experience_years": 11,
  "bio": "Yangilangan ma'lumot"
}
```

#### 3.5 O'qituvchini o'chirish
```http
DELETE /api/teachers/{id}/
```

**Response:** `204 No Content`

#### 3.6 Mening profilim (Teacher)
```http
GET /api/teachers/me/
```

Joriy autentifikatsiya qilingan foydalanuvchining o'qituvchi profilini qaytaradi.

**Response:**
```json
{
  "id": "uuid",
  "user": {...},
  "subjects": "Matematika, Fizika",
  "experience_years": 10,
  "bio": "10 yillik tajribaga ega o'qituvchi"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error."
}
```

---

## Pagination

Barcha list endpointlari paginatsiya qilangan (default: 10 ta obyekt har sahifada).

**Query Parameters:**
- `page` (integer): Sahifa raqami
- `page_size` (integer): Har sahifadagi obyektlar soni (max: 100)

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/students/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Swagger/OpenAPI Documentation

Interactive API documentation mavjud:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

---

## Qo'shimcha Ma'lumotlar

### Soft Delete
Barcha DELETE operatsiyalari soft delete amalga oshiradi. Ya'ni, ma'lumotlar bazadan o'chirilmaydi, faqat `deleted_at` field o'rnatiladi.

### UUID Primary Keys
Barcha modellar UUID primary key ishlatadi.

### Timestamp Fields
Barcha modellar quyidagi fieldlarga ega:
- `created_at`: Yaratilgan vaqt
- `updated_at`: Oxirgi yangilangan vaqt
- `deleted_at`: O'chirilgan vaqt (soft delete uchun)

### Validation
- Sinf raqami 1 dan 11 gacha bo'lishi kerak
- User bir vaqtning o'zida faqat bitta student yoki teacher profiliga ega bo'lishi mumkin
- Telefon raqami formati: `+998901234567`
