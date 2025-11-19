# Kurulum Kılavuzu - Detaylı Geliştirme Ortamı Hazırlığı

## 📋 Gereksinimler ve Neden

### Sistem Gereksinimleri

| Araç | Minimum Versiyon | Tavsiye | Neden |
|------|------------------|---------|-------|
| **Python** | 3.11 | 3.11+ | Type hints, performance improvements |
| **Node.js** | 18 LTS | 20 LTS | Vite compatibility, ES modules |
| **PostgreSQL** | 14 | 16 | JSON/JSONB support, GIN indexes |
| **Redis** | 7 | 7+ | ACL support, RediSearch |
| **Git** | 2.30+ | Latest | Advanced hooks, security patches |

### IDE Tavsiye Edilen Eklentiler (VS Code)

#### Python Development
- `ms-python.python` - Python IntelliSense, linting
- `ms-python.vscode-pylance` - Type checking, auto-completion
- `ms-python.black-formatter` - Code formatting
- `charliermarsh.ruff` - Fast linting

#### Frontend Development
- `Vue.volar` - Vue 3 language support
- `dbaeumer.vscode-eslint` - JavaScript/TypeScript linting
- `esbenp.prettier-vscode` - Code formatting
- `bradlc.vscode-tailwindcss` - Tailwind IntelliSense

#### DevOps & Utilities
- `ms-azuretools.vscode-docker` - Docker support
- `eamodio.gitlens` - Advanced Git features
- `GitHub.copilot` - AI pair programming
- `redhat.vscode-yaml` - YAML support
- `tamasfe.even-better-toml` - TOML support

## 🔧 Adım Adım Kurulum

### 1. Repository Klonlama

```bash
# SSH (Tavsiye)
git clone git@github.com:your-org/editorial_system.git
cd editorial_system

# HTTPS
git clone https://github.com/your-org/editorial_system.git
cd editorial_system
```

### 2. Backend Kurulumu

#### 2.1 Python Sanal Ortamı

**Windows:**
```powershell
# Sanal ortam oluştur
python -m venv venv

# Aktif et
.\venv\Scripts\Activate.ps1

# PowerShell execution policy hatası alırsanız:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
```bash
# Sanal ortam oluştur
python3.11 -m venv venv

# Aktif et
source venv/bin/activate
```

**Doğrulama:**
```bash
# Python versiyonu kontrol
python --version  # Output: Python 3.11.x

# pip güncellemesi
pip install --upgrade pip
```

#### 2.2 Backend Dependencies

```bash
cd backend

# Tüm bağımlılıkları yükle
pip install -r requirements.txt

# Development bağımlılıkları
pip install black isort flake8 mypy

# Kurulum doğrulaması
python -c "import django; print(django.VERSION)"
```

**Paket Açıklamaları:**

| Kategori | Paketler | Amaç |
|----------|----------|------|
| **Core Framework** | Django, DRF | Web framework, REST API |
| **Auth** | simplejwt | JWT authentication |
| **Database** | psycopg2-binary | PostgreSQL driver |
| **Async** | celery, redis | Task queue, caching |
| **Storage** | boto3, django-storages | S3 integration |
| **File Processing** | python-docx, PyPDF2, WeasyPrint | Document parsing, PDF generation |
| **State Machine** | django-fsm | Workflow management |
| **Testing** | pytest, pytest-django, factory-boy | Unit/integration tests |

#### 2.3 PostgreSQL Kurulumu

**Docker ile (Tavsiye):**
```bash
# PostgreSQL container başlat
docker run --name editorial_postgres \
  -e POSTGRES_DB=editorial_db \
  -e POSTGRES_USER=editorial_user \
  -e POSTGRES_PASSWORD=editorial_pass \
  -p 5432:5432 \
  -d postgres:16-alpine

# Bağlantı testi
docker exec -it editorial_postgres psql -U editorial_user -d editorial_db
```

**Manuel Kurulum (Windows):**
1. PostgreSQL installer indir: https://www.postgresql.org/download/windows/
2. Kurulum sırasında:
   - Port: 5432
   - Locale: C
3. pgAdmin ile veritabanı oluştur:
```sql
CREATE DATABASE editorial_db;
CREATE USER editorial_user WITH PASSWORD 'editorial_pass';
GRANT ALL PRIVILEGES ON DATABASE editorial_db TO editorial_user;
```

**Manuel Kurulum (Linux):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# Kullanıcı ve veritabanı oluştur
sudo -u postgres psql
CREATE DATABASE editorial_db;
CREATE USER editorial_user WITH PASSWORD 'editorial_pass';
GRANT ALL PRIVILEGES ON DATABASE editorial_db TO editorial_user;
\q
```

#### 2.4 Redis Kurulumu

**Docker ile:**
```bash
docker run --name editorial_redis -p 6379:6379 -d redis:7-alpine

# Bağlantı testi
docker exec -it editorial_redis redis-cli ping
# Output: PONG
```

**Windows (WSL veya Docker gerekli):**
```powershell
# Docker Desktop kullanın veya WSL2'de:
wsl
sudo apt install redis-server
sudo service redis-server start
redis-cli ping
```

#### 2.5 Environment Variables

```bash
cd backend

# .env.example'dan .env oluştur
cp .env.example .env

# .env dosyasını düzenle:
# - SECRET_KEY oluştur: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# - DATABASE_URL kontrol et
# - ORCID credentials ekle (isteğe bağlı)
```

**.env Örnek (Development):**
```env
SECRET_KEY=django-insecure-RANDOM-KEY-HERE
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://editorial_user:editorial_pass@localhost:5432/editorial_db

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

USE_S3=False

ORCID_CLIENT_ID=APP-XXXXXXXXXXXXXX
ORCID_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### 2.6 Database Migration

```bash
cd backend

# Migrations oluştur
python manage.py makemigrations

# Migrations uygula
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser

# Sunucu başlat (test)
python manage.py runserver
# http://localhost:8000/admin/ adresine gidin
```

### 3. Frontend Kurulumu

#### 3.1 Node.js ve npm

**Versiyon Kontrolü:**
```bash
node --version  # v18+ veya v20+
npm --version   # 9+
```

**Node.js Kurulum (eğer yoksa):**
- Windows: https://nodejs.org/en/download/
- Linux: `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -; sudo apt install -y nodejs`
- Mac: `brew install node@20`

#### 3.2 Dependencies Installation

```bash
cd frontend

# Dependencies yükle
npm install

# Alternatif (daha hızlı):
npm ci  # package-lock.json'dan tam kurulum
```

**Paket Açıklamaları:**

| Kategori | Paketler | Amaç |
|----------|----------|------|
| **Framework** | vue, vue-router, pinia | SPA framework, routing, state |
| **HTTP Client** | axios | API communication |
| **Form Validation** | vee-validate, yup | Form handling |
| **Styling** | tailwindcss | Utility-first CSS |
| **Build Tool** | vite | Fast dev server, bundler |
| **Type Safety** | typescript | Static typing |

#### 3.3 Environment Variables

```bash
cd frontend

# .env oluştur
cp .env.example .env

# .env düzenle
```

**.env Örnek:**
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_ORCID_CLIENT_ID=APP-XXXXXXXXXXXXXX
VITE_ORCID_REDIRECT_URI=http://localhost:5173/auth/orcid/callback
```

#### 3.4 Development Server

```bash
npm run dev
# ➜  Local:   http://localhost:5173/
```

### 4. Docker Compose ile Tüm Stack

**Tek Komutla Başlatma:**
```bash
# Tüm servisleri başlat
docker-compose up -d

# Logları izle
docker-compose logs -f

# Servis durumu
docker-compose ps

# Backend migration
docker-compose exec backend python manage.py migrate

# Durdur
docker-compose down

# Volume'ları da sil
docker-compose down -v
```

**Servisler:**
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Nginx: `http://localhost`

## 🧪 Kurulum Doğrulama

### Backend Health Check

```bash
cd backend

# Test suite çalıştır
pytest

# Linting kontrol
flake8 .

# Type checking
mypy .

# API endpoint testi
curl http://localhost:8000/api/health/
```

### Frontend Health Check

```bash
cd frontend

# Type check
npm run type-check

# Linting
npm run lint

# Build test
npm run build
```

## 🔍 Troubleshooting

### PostgreSQL Bağlantı Hatası

**Hata:** `psycopg2.OperationalError: could not connect to server`

**Çözüm:**
```bash
# PostgreSQL çalışıyor mu?
sudo service postgresql status  # Linux
# veya
docker ps  # Docker kullanıyorsanız

# Port dinliyor mu?
netstat -an | grep 5432  # Linux
# veya
netstat -an | findstr 5432  # Windows

# pg_hba.conf kontrolü (manuel kurulum)
# IPv4 local connections için:
# host    all             all             127.0.0.1/32            md5
```

### Redis Bağlantı Hatası

**Hata:** `redis.exceptions.ConnectionError`

**Çözüm:**
```bash
# Redis çalışıyor mu?
redis-cli ping

# Port kontrol
netstat -an | grep 6379

# Docker log kontrol
docker logs editorial_redis
```

### npm Install Hatası

**Hata:** `EACCES: permission denied`

**Çözüm:**
```bash
# npm cache temizle
npm cache clean --force

# node_modules sil ve tekrar dene
rm -rf node_modules package-lock.json
npm install
```

### CORS Hatası

**Hata:** `Access to XMLHttpRequest blocked by CORS policy`

**Çözüm:**
```python
# backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

## 📚 Sonraki Adımlar

1. ✅ [API Dokümantasyonu](API.md) - Endpoint referansları
2. ✅ [Mimari Tasarım](ARCHITECTURE.md) - Sistem mimarisi
3. ✅ [Deployment](DEPLOYMENT.md) - Production deployment
4. ✅ [Contributing](../CONTRIBUTING.md) - Katkı kılavuzu

## 🆘 Yardım

- **Issues:** GitHub Issues açın
- **Discord:** [Community Channel](https://discord.gg/editorial)
- **Email:** dev@editorial-system.com
