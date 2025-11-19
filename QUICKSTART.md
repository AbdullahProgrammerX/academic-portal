# Quick Start Commands

## Hızlı Başlangıç

### Windows
```powershell
# Setup script ile otomatik kurulum
.\setup.bat

# Manuel kurulum
python -m venv venv
.\venv\Scripts\Activate.ps1
cd backend; pip install -r requirements.txt; cd ..
cd frontend; npm install; cd ..
```

### Linux/Mac
```bash
# Setup script ile otomatik kurulum
chmod +x setup.sh
./setup.sh

# Manuel kurulum
python3 -m venv venv
source venv/bin/activate
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..
```

## Development Servisleri

### Backend (Django)
```bash
cd backend
python manage.py runserver
# http://localhost:8000
```

### Frontend (Vue)
```bash
cd frontend
npm run dev
# http://localhost:5173
```

### Celery Worker
```bash
cd backend
celery -A config worker --loglevel=info
```

### Celery Beat (Scheduled Tasks)
```bash
cd backend
celery -A config beat --loglevel=info
```

## Docker Compose (Tüm Servisler)

```bash
# Tüm servisleri başlat
docker-compose up -d

# Logları izle
docker-compose logs -f

# Sadece belirli servisleri başlat
docker-compose up -d postgres redis

# Durdur
docker-compose down

# Volume'lar ile birlikte sil
docker-compose down -v
```

## Database İşlemleri

```bash
cd backend

# Migrations oluştur
python manage.py makemigrations

# Migrations uygula
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell
```

## Test Çalıştırma

```bash
# Backend tests
cd backend
pytest
pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
npm run test
npm run test:coverage

# Linting
cd backend && flake8 .
cd frontend && npm run lint
```

## Sık Kullanılan Komutlar

```bash
# Backend static files toplama
cd backend
python manage.py collectstatic --no-input

# Frontend build
cd frontend
npm run build

# Type checking
cd frontend
npm run type-check

# Database flush (UYARI: Tüm veriyi siler!)
cd backend
python manage.py flush --no-input

# Redis flush
redis-cli FLUSHALL

# Docker logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

## Yardımcı Scriptler

```bash
# Makefile kullanımı
make help           # Tüm komutları göster
make setup          # Proje kurulumu
make install        # Dependencies yükle
make migrate        # Database migrate
make test           # Testleri çalıştır
make lint           # Linting
make clean          # Temizlik
```

## Environment Variables

```bash
# Backend .env oluştur
cp backend/.env.example backend/.env

# Frontend .env oluştur
cp frontend/.env.example frontend/.env

# SECRET_KEY oluştur
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## PostgreSQL (Docker olmadan)

```bash
# PostgreSQL başlat (Windows - PowerShell yönetici modunda)
Start-Service postgresql-x64-16

# PostgreSQL başlat (Linux)
sudo service postgresql start

# PostgreSQL başlat (Mac)
brew services start postgresql

# Database oluştur
psql -U postgres
CREATE DATABASE editorial_db;
CREATE USER editorial_user WITH PASSWORD 'editorial_pass';
GRANT ALL PRIVILEGES ON DATABASE editorial_db TO editorial_user;
\q
```

## Redis (Docker olmadan)

```bash
# Redis başlat (Linux)
sudo service redis-server start

# Redis başlat (Mac)
brew services start redis

# Redis bağlantı testi
redis-cli ping
```

## Troubleshooting

```bash
# Port kullanımda hatası
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Python cache temizle
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Node modules temizle
cd frontend
rm -rf node_modules package-lock.json
npm install

# Docker cache temizle
docker system prune -a

# Migration sıfırlama (UYARI!)
cd backend
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

```bash
# Production build
cd frontend
npm run build

# Static files toplama
cd backend
python manage.py collectstatic --no-input

# Gunicorn ile çalıştırma
cd backend
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Docker production build
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

```bash
# Celery task monitoring
cd backend
celery -A config flower

# Django debug toolbar
# settings.py'de DEBUG=True ve INSTALLED_APPS'e ekle

# Database query logging
# settings.py'de LOGGING yapılandırması
```

Detaylı bilgi için: [docs/SETUP.md](docs/SETUP.md)
