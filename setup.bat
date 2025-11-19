@echo off
REM Editorial System - Windows Setup Script
REM Bu script development ortamını hazırlar

echo ===============================================
echo Editorial Submission System - Setup
echo ===============================================
echo.

REM Python versiyonu kontrolü
echo [1/8] Python versiyonu kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi. Lutfen Python 3.11+ yukleyin.
    echo Indirme: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Node.js versiyonu kontrolü
echo [2/8] Node.js versiyonu kontrol ediliyor...
node --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Node.js bulunamadi. Lutfen Node.js 18+ yukleyin.
    echo Indirme: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo.

REM Python sanal ortam oluşturma
echo [3/8] Python sanal ortami olusturuluyor...
if exist venv (
    echo Sanal ortam zaten mevcut, atlaniyor...
) else (
    python -m venv venv
    echo Sanal ortam olusturuldu.
)
echo.

REM Sanal ortam aktivasyonu
echo [4/8] Sanal ortam aktive ediliyor...
call venv\Scripts\activate.bat
echo.

REM Backend bağımlılıkları kurulumu
echo [5/8] Backend bagimliliklari yukleniyor...
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..
echo.

REM Frontend bağımlılıkları kurulumu
echo [6/8] Frontend bagimliliklari yukleniyor...
cd frontend
call npm install
cd ..
echo.

REM Environment dosyaları oluşturma
echo [7/8] Environment dosyalari olusturuluyor...
if not exist backend\.env (
    copy backend\.env.example backend\.env
    echo backend/.env olusturuldu. LUTFEN DUZENLEYIN!
)
if not exist frontend\.env (
    copy frontend\.env.example frontend\.env
    echo frontend/.env olusturuldu. LUTFEN DUZENLEYIN!
)
echo.

REM Bilgilendirme
echo [8/8] Kurulum tamamlandi!
echo.
echo ===============================================
echo ONEMLI ADIMLAR:
echo ===============================================
echo.
echo 1. PostgreSQL yukleyin (eger yoksa):
echo    - Docker: docker run -d -p 5432:5432 --name editorial_postgres -e POSTGRES_DB=editorial_db -e POSTGRES_USER=editorial_user -e POSTGRES_PASSWORD=editorial_pass postgres:16-alpine
echo    - Manuel: https://www.postgresql.org/download/windows/
echo.
echo 2. Redis yukleyin (eger yoksa):
echo    - Docker: docker run -d -p 6379:6379 --name editorial_redis redis:7-alpine
echo    - Windows: https://github.com/microsoftarchive/redis/releases (veya WSL kullanin)
echo.
echo 3. Environment dosyalarini duzenleyin:
echo    - backend\.env (DATABASE_URL, SECRET_KEY, etc.)
echo    - frontend\.env (VITE_API_BASE_URL, etc.)
echo.
echo 4. SECRET_KEY olusturun:
echo    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
echo.
echo 5. Database migration calistirin:
echo    cd backend
echo    python manage.py migrate
echo    python manage.py createsuperuser
echo.
echo 6. Servisleri baslatin:
echo    Backend:  cd backend ^&^& python manage.py runserver
echo    Frontend: cd frontend ^&^& npm run dev
echo    Celery:   cd backend ^&^& celery -A config worker --loglevel=info
echo.
echo ===============================================
echo Detayli dokumantasyon: docs\SETUP.md
echo ===============================================
echo.
pause
