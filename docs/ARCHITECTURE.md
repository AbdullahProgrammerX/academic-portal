# Mimari Tasarım

## Genel Bakış

Editorial Submission System, modern mikroservis prensiplerine dayanan, yüksek performanslı bir makale gönderim platformudur.

## Sistem Mimarisi

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Nginx    │ (Reverse Proxy / Load Balancer)
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│  Vue 3   │   │  Django  │   │   S3     │
│ Frontend │   │  Backend │   │  Storage │
└──────────┘   └─────┬────┘   └──────────┘
                     │
                     ├─────────┬─────────┐
                     ▼         ▼         ▼
              ┌──────────┐ ┌─────┐ ┌─────────┐
              │PostgreSQL│ │Redis│ │ Celery  │
              └──────────┘ └─────┘ └─────────┘
```

## Backend Katmanları

### 1. API Layer (Django REST Framework)

- **Views**: Request handling, validation
- **Serializers**: Data transformation, validation
- **Permissions**: Role-based access control

### 2. Business Logic Layer

- **Models**: Database schema, business rules
- **Services**: Complex business logic
- **django-fsm**: State machine for workflows

### 3. Data Layer

- **PostgreSQL**: Relational data, transactions
- **Redis**: Caching, session storage
- **S3**: File storage (manuscripts, PDFs)

### 4. Async Processing

- **Celery**: Background tasks
  - PDF metadata extraction
  - Email notifications
  - Document processing

## Frontend Mimarisi

### Vue 3 Composition API

```
src/
├── api/           # API clients (axios)
├── stores/        # Pinia state management
├── router/        # Vue Router
├── views/         # Page components
├── components/    # Reusable components
└── types/         # TypeScript interfaces
```

### State Management (Pinia)

- **auth**: Authentication, user session
- **submissions**: Manuscript data
- **ui**: UI state (modals, notifications)

### API Communication

- **Axios interceptors**
  - Auto token refresh
  - Error handling
  - Request/response logging

## Veri Akışları

### 1. Manuscript Submission Flow

```
1. User uploads file → Frontend
2. Get presigned URL → Backend API
3. Upload to S3 → Direct from browser
4. Create submission → Backend API
5. Trigger metadata extraction → Celery task
6. Update submission metadata → Background
7. Notify user → Email/WebSocket
```

### 2. ORCID Authentication Flow

```
1. User clicks "Login with ORCID" → Frontend
2. Redirect to ORCID → OAuth provider
3. User authorizes → ORCID
4. Callback with code → Frontend
5. Exchange code for token → Backend API
6. Create/update user → Django
7. Return JWT tokens → Frontend
8. Store tokens → localStorage
```

### 3. File Processing Pipeline

```
┌─────────────┐
│   Upload    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  S3 Storage │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Celery Task  │ (async)
│Extract Meta │
└──────┬──────┘
       │
       ├─────────┬─────────┐
       ▼         ▼         ▼
   [.docx]   [.pdf]   [.tex]
       │         │         │
       ▼         ▼         ▼
┌──────────────────────────┐
│  python-docx / PyPDF2    │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Update DB Metadata      │
└──────────────────────────┘
```

## Performans Optimizasyonları

### Database

- **Indexing**: Email, ORCID, status fields
- **Query optimization**: select_related, prefetch_related
- **Connection pooling**: pgbouncer

### Caching Strategy

```python
# Redis caching layers
1. User sessions (15 min TTL)
2. API responses (5 min TTL)
3. File metadata (1 hour TTL)
4. Dashboard queries (2 min TTL)
```

### Frontend

- **Code splitting**: Route-based lazy loading
- **Asset optimization**: Vite build optimization
- **API debouncing**: Search, autocomplete
- **Pagination**: Virtual scrolling for lists

## Güvenlik

### Backend

- JWT authentication (1h access, 7d refresh)
- CORS whitelist
- Rate limiting (django-ratelimit)
- SQL injection protection (ORM)
- XSS protection (DRF serializers)

### Frontend

- XSS prevention (Vue sanitization)
- CSRF tokens
- Secure localStorage (encrypted tokens)
- Input validation (vee-validate + yup)

### File Security

- Presigned URLs (1h expiry)
- Virus scanning (ClamAV)
- File type validation
- Size limits (100MB)

## Ölçeklenebilirlik

### Horizontal Scaling

- Stateless backend (JWT)
- Redis session store
- S3 distributed storage
- Celery workers (auto-scale)

### Vertical Scaling

- Database connection pooling
- Redis clustering
- Celery concurrency tuning

### Target Performance

- **Dashboard load**: <200ms
- **API response**: <100ms (avg)
- **File upload**: Direct S3 (no backend bottleneck)
- **Concurrent users**: 10,000+

## Monitoring & Logging

### Metrics

- Request latency (p50, p95, p99)
- Error rates
- Celery task success/failure
- Database query time

### Logs

```python
# Structured logging
{
  "timestamp": "2025-11-19T10:00:00Z",
  "level": "INFO",
  "user_id": 123,
  "action": "submission_created",
  "manuscript_id": 456,
  "duration_ms": 150
}
```

## Future Enhancements

- [ ] Real-time notifications (WebSockets)
- [ ] GraphQL API option
- [ ] ML-based metadata extraction
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Plagiarism detection integration
