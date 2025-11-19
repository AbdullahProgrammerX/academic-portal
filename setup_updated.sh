#!/bin/bash

# Editorial System - Linux/Mac Setup Script
# Bu script development ortamını hazırlar

set -e

echo "==============================================="
echo "Editorial Submission System - Setup"
echo "==============================================="
echo ""

# Python versiyonu kontrolü
echo "[1/8] Python versiyonu kontrol ediliyor..."
if ! command -v python3 &> /dev/null; then
    echo "HATA: Python3 bulunamadı. Lütfen Python 3.11+ yükleyin."
    exit 1
fi
python3 --version
echo ""

# Node.js versiyonu kontrolü
echo "[2/8] Node.js versiyonu kontrol ediliyor..."
if ! command -v node &> /dev/null; then
    echo "HATA: Node.js bulunamadı. Lütfen Node.js 18+ yükleyin."
    exit 1
fi
node --version
echo ""

# Python sanal ortam oluşturma
echo "[3/8] Python sanal ortamı oluşturuluyor..."
if [ -d "venv" ]; then
    echo "Sanal ortam zaten mevcut, atlanıyor..."
else
    python3 -m venv venv
    echo "Sanal ortam oluşturuldu."
fi
echo ""

# Sanal ortam aktivasyonu
echo "[4/8] Sanal ortam aktive ediliyor..."
source venv/bin/activate
echo ""

# Backend bağımlılıkları kurulumu
echo "[5/8] Backend bağımlılıkları yükleniyor..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..
echo ""

# Frontend bağımlılıkları kurulumu
echo "[6/8] Frontend bağımlılıkları yükleniyor..."
cd frontend
npm install
cd ..
echo ""

# Environment dosyaları oluşturma
echo "[7/8] Environment dosyaları oluşturuluyor..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "backend/.env oluşturuldu. LÜTFEN DÜZENLEYİN!"
fi
if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "frontend/.env oluşturuldu. LÜTFEN DÜZENLEYİN!"
fi
echo ""

# Bilgilendirme
echo "[8/8] Kurulum tamamlandı!"
echo ""
echo "==============================================="
echo "ÖNEMLİ ADIMLAR:"
echo "==============================================="
echo ""
echo "1. PostgreSQL yükleyin (eğer yoksa):"
echo "   Docker: docker run -d -p 5432:5432 --name editorial_postgres \\"
echo "           -e POSTGRES_DB=editorial_db \\"
echo "           -e POSTGRES_USER=editorial_user \\"
echo "           -e POSTGRES_PASSWORD=editorial_pass \\"
echo "           postgres:16-alpine"
echo "   veya"
echo "   sudo apt install postgresql (Linux)"
echo "   brew install postgresql (Mac)"
echo ""
echo "2. Redis yükleyin (eğer yoksa):"
echo "   Docker: docker run -d -p 6379:6379 --name editorial_redis redis:7-alpine"
echo "   veya"
echo "   sudo apt install redis-server (Linux)"
echo "   brew install redis (Mac)"
echo ""
echo "3. Environment dosyalarını düzenleyin:"
echo "   backend/.env (DATABASE_URL, SECRET_KEY, etc.)"
echo "   frontend/.env (VITE_API_BASE_URL, etc.)"
echo ""
echo "4. SECRET_KEY oluşturun:"
echo "   python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
echo ""
echo "5. Database migration çalıştırın:"
echo "   cd backend"
echo "   python manage.py migrate"
echo "   python manage.py createsuperuser"
echo ""
echo "6. Servisleri başlatın:"
echo "   Backend:  cd backend && python manage.py runserver"
echo "   Frontend: cd frontend && npm run dev"
echo "   Celery:   cd backend && celery -A config worker --loglevel=info"
echo ""
echo "7. Docker Compose ile (alternatif):"
echo "   docker-compose up -d"
echo ""
echo "==============================================="
echo "Detaylı dokümantasyon: docs/SETUP.md"
echo "==============================================="
echo ""
