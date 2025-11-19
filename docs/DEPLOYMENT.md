# Deployment Kılavuzu

## Gereksinimler

- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+
- AWS S3 bucket (veya uyumlu object storage)
- ORCID OAuth credentials

## Kurulum Adımları

### 1. Repository'yi Clone Edin

```bash
git clone https://github.com/your-org/editorial_system.git
cd editorial_system
```

### 2. Environment Variables

Backend `.env` dosyası:

```bash
cp backend/.env.example backend/.env
```

Düzenleyin:
- `SECRET_KEY` - Yeni bir Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `AWS_*` - S3 credentials
- `ORCID_*` - ORCID OAuth credentials

Frontend `.env` dosyası:

```bash
cp frontend/.env.example frontend/.env
```

### 3. Docker ile Başlatma

**Development:**

```bash
docker-compose up -d
```

**Production:**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Database Migration

```bash
docker-compose exec backend python manage.py migrate
```

### 5. Superuser Oluşturma

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Static Files

```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

## Production Checklist

- [ ] `DEBUG=False` ayarla
- [ ] Güçlü `SECRET_KEY` kullan
- [ ] HTTPS kur (SSL/TLS)
- [ ] `ALLOWED_HOSTS` doğru ayarla
- [ ] Database backup planı
- [ ] Monitoring & logging kur
- [ ] Rate limiting ekle
- [ ] CORS ayarlarını sıkılaştır
- [ ] S3 bucket permissions kontrol et
- [ ] Email servis kur

## Ölçeklendirme

### Horizontal Scaling

- Nginx load balancer
- Multiple backend instances
- Redis cluster
- PostgreSQL replication

### Performance

- Redis caching
- CDN for static files
- Database indexing
- Celery task optimization

## Monitoring

Önerilen araçlar:
- Sentry (error tracking)
- Prometheus + Grafana (metrics)
- ELK Stack (logging)
- New Relic / DataDog (APM)

## Backup Stratejisi

### Database Backup

```bash
docker-compose exec postgres pg_dump -U editorial_user editorial_db > backup.sql
```

### S3 Backup

AWS S3 versioning ve lifecycle policies kullanın.

## Rollback

```bash
docker-compose down
git checkout <previous-version>
docker-compose up -d
docker-compose exec backend python manage.py migrate
```
