# API Dokümantasyonu

## Genel Bilgiler

Base URL: `http://localhost:8000/api`

Tüm API endpoint'leri JSON formatında veri döner ve JWT authentication gerektirir (login/ORCID callback hariç).

### Authentication

Bearer token kullanılır:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST `/auth/orcid/login/`
ORCID OAuth flow başlatır.

**Response:**
```json
{
  "authorization_url": "https://orcid.org/oauth/authorize?..."
}
```

#### POST `/auth/orcid/callback/`
ORCID callback handler.

**Request:**
```json
{
  "code": "oauth_code"
}
```

**Response:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "orcid": "0000-0001-2345-6789",
    "role": "author"
  }
}
```

#### POST `/token/refresh/`
Access token yeniler.

**Request:**
```json
{
  "refresh": "jwt_refresh_token"
}
```

**Response:**
```json
{
  "access": "new_jwt_access_token"
}
```

### Submissions

#### GET `/submissions/`
Kullanıcının manuscript'lerini listeler.

**Query Parameters:**
- `status` (optional): manuscript durumu filtresi
- `page` (optional): sayfa numarası

**Response:**
```json
{
  "count": 10,
  "next": "http://...",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Research Paper Title",
      "status": "submitted",
      "submitted_at": "2025-11-19T10:00:00Z"
    }
  ]
}
```

#### POST `/submissions/create/`
Yeni manuscript oluşturur.

**Request:**
```json
{
  "title": "Research Title",
  "abstract": "Abstract text...",
  "authors": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "orcid": "0000-0001-2345-6789",
      "is_corresponding": true
    }
  ]
}
```

### Files

#### POST `/files/upload/presigned/`
S3 presigned upload URL alır.

**Request:**
```json
{
  "filename": "manuscript.docx",
  "file_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}
```

**Response:**
```json
{
  "upload_url": "https://s3.amazonaws.com/...",
  "file_key": "uuid/manuscript.docx",
  "expires_in": 3600
}
```

## Error Responses

Tüm hatalar tutarlı formatta döner:

```json
{
  "error": true,
  "message": "Error description",
  "details": {},
  "status_code": 400
}
```

### HTTP Status Codes

- `200` - Başarılı
- `201` - Oluşturuldu
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
