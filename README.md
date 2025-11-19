# Editorial Submission System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)
[![Vue 3](https://img.shields.io/badge/vue-3.4-brightgreen.svg)](https://vuejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, ölçeklenebilir makale gönderim platformu - **Editorial Manager** alternatifi.

> 🎯 **Hedef:** 10,000+ kullanıcıya hizmet verebilecek, ORCID entegreli, asenkron dosya işleme yetenekli, yüksek performanslı akademik makale yönetim sistemi.

---

## ✨ Temel Özellikler

### 🔐 Kimlik Doğrulama & Yetkilendirme
- **ORCID OAuth 2.0** entegrasyonu
- JWT tabanlı stateless authentication
- Role-based access control (RBAC)

### 📄 Makale Gönderim & Yönetimi
- Tek-sayfa gönderim arayüzü (SPA)
- Çoklu dosya desteği (Word, PDF, LaTeX)
- Asenkron metadata çıkarma (python-docx, PyPDF2)
- S3 üzerinde güvenli dosya depolama

### 🔄 Revision İş Akışı
- Django FSM ile state management
- Otomatik email bildirimleri
- Version tracking

### 📊 Dashboard & Raporlama
- Hızlı filtreleme (<200ms)
- Advanced analytics
- Export to Excel/PDF

---

## 🏗️ Teknoloji Stack

### Backend
```text
🐍 Python 3.11+
🎯 Django 5.0 + DRF 3.14
🔑 JWT (SimpleJWT)
🗄️ PostgreSQL 16
⚡ Redis 7
📦 Celery 5.3
☁️ AWS S3
```

### Frontend
```text
💚 Vue 3.4
⚡ Vite 5.0
🗂️ Pinia
🛣️ Vue Router 4.2
📡 Axios
🎨 Tailwind CSS 3.4
📝 TypeScript 5.3
```

---

## 📁 Proje Yapısı

```text
editorial_system/
├── backend/              # Django REST API
│   ├── users/            # Kullanıcı, ORCID auth
│   ├── submissions/      # Makale gönderimi
│   ├── revisions/        # Revizyon iş akışı
│   ├── files/            # Dosya yönetimi
│   └── tasks/            # Celery task'lar
├── frontend/             # Vue 3 SPA
│   └── src/
│       ├── api/          # API clients
│       ├── stores/       # Pinia stores
│       ├── router/       # Vue Router
│       └── views/        # Components
├── infra/                # Infrastructure
│   └── nginx/            # Nginx configs
├── docs/                 # Dokümantasyon
└── docker-compose.yml    # Services
```

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

| Araç | Minimum | Tavsiye |
|------|---------|---------|
| Python | 3.11 | 3.11+ |
| Node.js | 18 LTS | 20 LTS |
| PostgreSQL | 14 | 16 |
| Redis | 7 | 7+ |

### Otomatik Kurulum

**Windows:**
```powershell
.\setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Docker Compose (Tavsiye)

```bash
# Tüm servisleri başlat
docker-compose up -d

# Migration
docker-compose exec backend python manage.py migrate

# Superuser
docker-compose exec backend python manage.py createsuperuser
```

**Servis URL'leri:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Admin: http://localhost:8000/admin

---

## 📚 Dokümantasyon

| Dokuman | İçerik |
|---------|--------|
| [SETUP.md](docs/SETUP.md) | Detaylı kurulum |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Sistem mimarisi |
| [API.md](docs/API.md) | API referansı |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment |
| [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) | Git stratejisi |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Katkı kılavuzu |

---

## 🧪 Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run test

# Linting
flake8 .
npm run lint
```

---

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'feat: add feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

Detaylar: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📊 Roadmap

- [x] **AŞAMA 0:** Proje iskeleti ✅
- [ ] **AŞAMA 1:** ORCID authentication 🚧
- [ ] **AŞAMA 2:** Gönderim sistemi
- [ ] **AŞAMA 3:** Revizyon workflow
- [ ] **AŞAMA 4:** Production ready

---

## 📜 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 📞 İletişim

- Email: dev@editorial-system.com
- GitHub Issues: Bug reports
- Discussions: Feature requests

---

<div align="center">

**[⭐ Star](https://github.com/your-org/editorial_system)** • **[🐛 Bug Report](https://github.com/your-org/editorial_system/issues)** • **[✨ Feature Request](https://github.com/your-org/editorial_system/discussions)**

Made with ❤️ by Editorial System Team

</div>
