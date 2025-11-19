# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Real-time notifications (WebSockets)
- ML-based metadata extraction
- GraphQL API option
- Multi-language support
- Advanced analytics dashboard
- Plagiarism detection integration

## [0.1.0] - 2025-11-19

### Added - AŞAMA 0: Proje İskeleti

#### Infrastructure
- ✅ Project structure created (backend, frontend, infra, docs)
- ✅ Python 3.11+ virtual environment setup
- ✅ Node.js 18+ development environment
- ✅ Docker Compose configuration for all services
- ✅ PostgreSQL 16 database setup
- ✅ Redis 7 for caching and task queue

#### Backend (Django)
- ✅ Django 5.0 + Django REST Framework
- ✅ JWT authentication with SimpleJWT
- ✅ Custom User model
- ✅ Celery + Redis for async tasks
- ✅ PostgreSQL connection with pooling (conn_max_age=600)
- ✅ AWS S3 storage integration (django-storages + boto3)
- ✅ ORCID OAuth configuration
- ✅ File processing libraries (python-docx, PyPDF2, WeasyPrint)
- ✅ Django FSM for workflow state management
- ✅ CORS configuration for frontend
- ✅ Comprehensive logging setup
- ✅ Exception handling middleware

#### Frontend (Vue 3)
- ✅ Vue 3 with Composition API
- ✅ Vite 5 build tool
- ✅ Pinia state management
- ✅ Vue Router for SPA navigation
- ✅ Axios for API communication
- ✅ TypeScript support
- ✅ Tailwind CSS for styling
- ✅ VeeValidate + Yup for form validation
- ✅ ESLint + Prettier for code quality

#### Development Tools
- ✅ `.editorconfig` for consistent coding styles
- ✅ `.flake8` configuration for Python linting
- ✅ `.eslintrc.cjs` for JavaScript/TypeScript linting
- ✅ `pytest.ini` for test configuration
- ✅ `Makefile` with common development commands
- ✅ `.env.example` files for environment variables

#### Documentation
- ✅ Comprehensive README.md
- ✅ SETUP.md - Detailed installation guide
- ✅ ARCHITECTURE.md - System architecture and design
- ✅ CONTRIBUTING.md - Contribution guidelines
- ✅ API.md - API endpoint documentation
- ✅ DEPLOYMENT.md - Production deployment guide

#### Version Control
- ✅ `.gitignore` configured for Python, Node, Django, Vue
- ✅ Branch strategy documented (main/develop/feature)
- ✅ Commit message guidelines (Semantic Commits)
- ✅ PR template and review process

#### Apps Structure
- ✅ `users/` - User management and authentication
- ✅ `submissions/` - Manuscript submission handling
- ✅ `revisions/` - Revision workflow management
- ✅ `files/` - File upload and storage
- ✅ `tasks/` - Celery task definitions

#### Configuration Files
- ✅ `requirements.txt` - Complete Python dependencies
- ✅ `package.json` - Complete Node.js dependencies
- ✅ `docker-compose.yml` - Multi-service orchestration
- ✅ `Dockerfile` - Backend containerization
- ✅ `nginx.conf` - Reverse proxy configuration

#### Testing
- ✅ pytest + pytest-django setup
- ✅ factory_boy for test fixtures
- ✅ Coverage configuration
- ✅ Test markers (unit, integration, slow)

### Technical Specifications

#### Backend Stack
```
Django==5.0.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
boto3==1.34.14
python-docx==1.1.0
WeasyPrint==60.1
```

#### Frontend Stack
```
vue@3.4.0
vite@5.0.0
pinia@2.1.7
vue-router@4.2.5
axios@1.6.2
typescript@5.3.0
tailwindcss@3.4.0
```

#### Database Schema
- PostgreSQL with JSON/JSONB support
- Connection pooling with conn_max_age=600
- Health checks enabled

#### Performance Targets
- Dashboard load: <200ms
- API response: <100ms (avg)
- Concurrent users: 10,000+
- File upload: Direct to S3 (no backend bottleneck)

### Next Steps (AŞAMA 1)
- [ ] User model with ORCID integration
- [ ] JWT authentication endpoints
- [ ] ORCID OAuth flow implementation
- [ ] User registration and profile management
- [ ] Email verification system
- [ ] Password reset functionality

---

## Version History

### Version Numbering
This project uses Semantic Versioning:
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward compatible)
- **PATCH** version for bug fixes (backward compatible)

### Release Schedule
- **Alpha**: Internal testing (0.x.x)
- **Beta**: Public testing (1.0.0-beta.x)
- **Stable**: Production ready (1.0.0+)

### Support
- Current stable: Will be 1.0.0 (when released)
- Development: 0.1.0 (current)
- Python: 3.11+
- Node.js: 18 LTS, 20 LTS

---

**Legend:**
- ✅ Completed
- 🚧 In Progress
- ⏳ Planned
- ❌ Deprecated
- 🔒 Security fix
- ⚡ Performance improvement
