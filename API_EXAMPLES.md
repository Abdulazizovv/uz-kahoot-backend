# API Test Examples

Bu faylda API endpointlarini test qilish uchun cURL va Python misollari keltirilgan.

## Authentication

Avval token olish:

```bash
# OTP so'rash
curl -X POST http://localhost:8000/api/auth/telegram/request-otp/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123456789"}'

# OTP tasdiqlash va token olish
curl -X POST http://localhost:8000/api/auth/telegram/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"otp": "12345"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

## Guruhlar API

### 1. Guruhlar ro'yxati

```bash
curl -X GET http://localhost:8000/api/groups/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Guruh yaratish

```bash
curl -X POST http://localhost:8000/api/groups/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "10-A sinf",
    "grade": 10
  }'
```

### 3. Guruh tafsilotlari

```bash
curl -X GET http://localhost:8000/api/groups/{group_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Guruhni yangilash

```bash
curl -X PATCH http://localhost:8000/api/groups/{group_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "10-B sinf"
  }'
```

### 5. Guruhni o'chirish

```bash
curl -X DELETE http://localhost:8000/api/groups/{group_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Guruh statistikasi

```bash
curl -X GET http://localhost:8000/api/groups/{group_id}/statistics/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Studentlar API

### 1. Studentlar ro'yxati

```bash
curl -X GET http://localhost:8000/api/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Filter va qidiruv

```bash
# Guruh bo'yicha filter
curl -X GET "http://localhost:8000/api/students/?group={group_id}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Qidiruv
curl -X GET "http://localhost:8000/api/students/?search=Ali" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Sinf bo'yicha filter
curl -X GET "http://localhost:8000/api/students/?group__grade=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Student yaratish

```bash
curl -X POST http://localhost:8000/api/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_UUID",
    "group": "GROUP_UUID",
    "date_of_birth": "2010-05-15",
    "address": "Toshkent shahar"
  }'
```

### 4. Student tafsilotlari

```bash
curl -X GET http://localhost:8000/api/students/{student_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Studentni yangilash

```bash
curl -X PATCH http://localhost:8000/api/students/{student_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Yangi manzil"
  }'
```

### 6. Mening profilim

```bash
curl -X GET http://localhost:8000/api/students/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Guruh bo'yicha studentlar

```bash
curl -X GET "http://localhost:8000/api/students/by_group/?group_id={group_id}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## O'qituvchilar API

### 1. O'qituvchilar ro'yxati

```bash
curl -X GET http://localhost:8000/api/teachers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. O'qituvchi yaratish

```bash
curl -X POST http://localhost:8000/api/teachers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_UUID",
    "subjects": "Matematika, Fizika",
    "experience_years": 10,
    "bio": "10 yillik tajribaga ega o'\''qituvchi"
  }'
```

### 3. O'qituvchi tafsilotlari

```bash
curl -X GET http://localhost:8000/api/teachers/{teacher_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. O'qituvchini yangilash

```bash
curl -X PATCH http://localhost:8000/api/teachers/{teacher_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subjects": "Matematika, Fizika, Astronomiya",
    "experience_years": 11
  }'
```

### 5. Mening profilim

```bash
curl -X GET http://localhost:8000/api/teachers/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Python Examples

### Setup

```python
import requests

BASE_URL = "http://localhost:8000/api"
ACCESS_TOKEN = "your_access_token_here"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
```

### Guruh yaratish

```python
response = requests.post(
    f"{BASE_URL}/groups/",
    headers=headers,
    json={
        "name": "10-A sinf",
        "grade": 10
    }
)
print(response.json())
```

### Studentlar ro'yxati

```python
response = requests.get(
    f"{BASE_URL}/students/",
    headers=headers,
    params={
        "group__grade": 10,
        "search": "Ali"
    }
)
print(response.json())
```

### Student yaratish

```python
response = requests.post(
    f"{BASE_URL}/students/",
    headers=headers,
    json={
        "user_id": "user-uuid-here",
        "group": "group-uuid-here",
        "date_of_birth": "2010-05-15",
        "address": "Toshkent shahar"
    }
)
print(response.json())
```

### Pagination

```python
response = requests.get(
    f"{BASE_URL}/students/",
    headers=headers,
    params={
        "page": 1,
        "page_size": 20
    }
)

data = response.json()
print(f"Total: {data['count']}")
print(f"Next: {data['next']}")
print(f"Previous: {data['previous']}")
print(f"Results: {len(data['results'])}")
```

## Postman Collection

Postman collection yaratish uchun:

1. Postman ochish
2. Import > Link > http://localhost:8000/api/schema/ kiriting
3. OpenAPI 3.0 formatida import qilish

Yoki qo'lda collection yaratish:

1. Environment yaratish:
   - `base_url`: http://localhost:8000/api
   - `access_token`: your_token

2. Har bir request uchun:
   - URL: `{{base_url}}/groups/`
   - Headers: `Authorization: Bearer {{access_token}}`

## Testing with HTTPie

HTTPie CLI tool orqali test qilish:

```bash
# Install
pip install httpie

# Guruhlar ro'yxati
http GET localhost:8000/api/groups/ "Authorization:Bearer YOUR_TOKEN"

# Guruh yaratish
http POST localhost:8000/api/groups/ \
  "Authorization:Bearer YOUR_TOKEN" \
  name="10-A sinf" grade:=10

# Student yaratish
http POST localhost:8000/api/students/ \
  "Authorization:Bearer YOUR_TOKEN" \
  user_id="uuid" \
  group="uuid" \
  date_of_birth="2010-05-15" \
  address="Toshkent"
```

## Common Errors

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solution:** Token headerga qo'shing

### 400 Bad Request

```json
{
  "name": ["This field is required."]
}
```

**Solution:** Required fieldlarni to'ldiring

### 404 Not Found

```json
{
  "detail": "Not found."
}
```

**Solution:** ID to'g'riligini tekshiring
