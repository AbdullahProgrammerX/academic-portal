# Katkı Kılavuzu

Editorial Submission System projesine katkıda bulunduğunuz için teşekkürler! 🎉

## 📋 İçindekiler

- [Geliştirme Ortamı](#geliştirme-ortamı)
- [Branch Stratejisi](#branch-stratejisi)
- [Commit Mesajları](#commit-mesajları)
- [Pull Request Süreci](#pull-request-süreci)
- [Kod Standartları](#kod-standartları)
- [Test Yazma](#test-yazma)

## 🔧 Geliştirme Ortamı

Kurulum için [SETUP.md](docs/SETUP.md) dökümanına bakın.

### Ön Koşullar

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Git 2.30+

## 🌿 Branch Stratejisi

Projenin branch yapısı Git Flow modelini takip eder:

### Ana Branch'ler

```
main (production)
  ↑
develop (staging)
  ↑
feature/* (geliştirme)
```

### Branch İsimlendirme

| Tip | Format | Örnek |
|-----|--------|-------|
| **Feature** | `feature/issue-number-description` | `feature/123-orcid-authentication` |
| **Bugfix** | `bugfix/issue-number-description` | `bugfix/456-pdf-upload-error` |
| **Hotfix** | `hotfix/issue-number-description` | `hotfix/789-security-patch` |
| **Docs** | `docs/description` | `docs/api-documentation-update` |
| **Refactor** | `refactor/description` | `refactor/celery-task-optimization` |

### Yeni Feature Başlatma

```bash
# develop'dan branch oluştur
git checkout develop
git pull origin develop

# Feature branch oluştur
git checkout -b feature/123-new-feature

# Değişiklikleri yap
# ...

# Push et
git push -u origin feature/123-new-feature
```

## 📝 Commit Mesajları

Semantic Commit Messages formatını kullanıyoruz:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Tipler

| Tip | Kullanım | Örnek |
|-----|----------|-------|
| `feat` | Yeni özellik | `feat(auth): add ORCID OAuth integration` |
| `fix` | Bug düzeltme | `fix(upload): resolve file size validation error` |
| `docs` | Dokümantasyon | `docs(api): update endpoint documentation` |
| `style` | Format değişikliği | `style(backend): apply black formatting` |
| `refactor` | Kod iyileştirme | `refactor(models): simplify submission model` |
| `perf` | Performans iyileştirme | `perf(api): optimize query with select_related` |
| `test` | Test ekleme | `test(submissions): add unit tests for create endpoint` |
| `chore` | Build/CI değişiklikleri | `chore(deps): update Django to 5.0.1` |

### Örnekler

**İyi Commit Mesajları:**

```bash
feat(submissions): implement multi-file upload support

- Add support for uploading multiple files in single submission
- Implement client-side file validation (size, type)
- Add progress tracking for batch uploads

Closes #123
```

```bash
fix(auth): resolve token refresh infinite loop

Token refresh was triggering repeatedly due to incorrect
expiry check in axios interceptor.

- Fix expiry time comparison logic
- Add unit tests for token refresh flow

Fixes #456
```

**Kötü Commit Mesajları:**

```bash
# ❌ Çok genel
Update files

# ❌ Detay yok
fix bug

# ❌ Çok uzun tek satır
feat: add new feature that allows users to upload multiple files at once and also adds validation for file types and sizes with progress tracking
```

## 🔄 Pull Request Süreci

### PR Oluşturma

1. **Feature branch'i güncel tut:**
```bash
git checkout feature/123-new-feature
git fetch origin
git rebase origin/develop
```

2. **Testleri çalıştır:**
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run test && npm run type-check
```

3. **Linting kontrol:**
```bash
# Backend
flake8 . && black . --check

# Frontend
npm run lint
```

4. **GitHub'da PR aç:**
   - Base branch: `develop`
   - Compare branch: `feature/123-new-feature`
   - Template'i doldur

### PR Template

```markdown
## 📋 Değişiklik Özeti

[Değişikliğin kısa açıklaması]

## 🎯 İlgili Issue

Closes #[issue number]

## 🔄 Değişiklik Tipi

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## ✅ Checklist

- [ ] Kod local'de test edildi
- [ ] Unit testler eklendi/güncellendi
- [ ] Dokümantasyon güncellendi
- [ ] Linting kurallarına uygun
- [ ] Migration dosyaları eklendi (varsa)
- [ ] CHANGELOG.md güncellendi

## 🧪 Test Planı

[Nasıl test edildiğini açıklayın]

## 📸 Screenshots (UI değişiklikleri için)

[Ekran görüntüleri ekleyin]

## 📝 Ekstra Notlar

[Reviewer'ların bilmesi gereken ek bilgiler]
```

### Review Süreci

#### PR Açan Kişi:

- ✅ Tüm CI kontrolleri geçmeli (lint, test, build)
- ✅ Conflict'ler çözülmeli
- ✅ En az 1 approval alınmalı
- ✅ Review yorumlarına cevap verilmeli

#### Reviewer:

- 🔍 Kod kalitesi ve okunabilirlik
- 🔍 Test coverage'ı yeterli mi?
- 🔍 Güvenlik zafiyeti var mı?
- 🔍 Performance impact?
- 🔍 Breaking change var mı?

### Approval ve Merge

```bash
# Squash merge (tavsiye - feature branch için)
# - Tüm commit'ler tek commit'e indirgenir
# - Develop branch'i temiz kalır

# Merge commit (hotfix için)
# - Commit history korunur

# Rebase merge (small fixes için)
# - Linear history
```

**Merge Sonrası:**
```bash
# Feature branch'i sil
git branch -d feature/123-new-feature
git push origin --delete feature/123-new-feature

# develop'ı güncelle
git checkout develop
git pull origin develop
```

## 💻 Kod Standartları

### Backend (Python)

#### PEP 8 + Black

```python
# ✅ İyi
def create_submission(
    user: User,
    title: str,
    manuscript_file: File,
    *,
    abstract: Optional[str] = None
) -> Submission:
    """
    Create a new manuscript submission.
    
    Args:
        user: The submitting user
        title: Manuscript title
        manuscript_file: Uploaded file
        abstract: Optional abstract text
        
    Returns:
        Created Submission instance
        
    Raises:
        ValidationError: If file is invalid
    """
    submission = Submission.objects.create(
        user=user,
        title=title,
        status=SubmissionStatus.DRAFT
    )
    submission.attach_file(manuscript_file)
    return submission


# ❌ Kötü
def create_submission(user,title,file):
    s=Submission.objects.create(user=user,title=title)
    s.file=file
    return s
```

#### Type Hints (Zorunlu)

```python
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet

def get_user_submissions(
    user: User,
    status: Optional[str] = None
) -> QuerySet[Submission]:
    """Get submissions for a user, optionally filtered by status."""
    qs = Submission.objects.filter(user=user)
    if status:
        qs = qs.filter(status=status)
    return qs
```

#### Docstrings (Google Style)

```python
def process_manuscript(file_path: str, extract_metadata: bool = True) -> Dict[str, Any]:
    """
    Process uploaded manuscript file.
    
    Extracts metadata from Word/PDF files and generates preview.
    
    Args:
        file_path: Absolute path to uploaded file
        extract_metadata: Whether to extract document metadata
        
    Returns:
        Dictionary containing:
            - title: Extracted document title
            - authors: List of author names
            - abstract: Document abstract
            - word_count: Total word count
            
    Raises:
        FileNotFoundError: If file doesn't exist
        UnsupportedFileType: If file type is not supported
        
    Example:
        >>> metadata = process_manuscript('/tmp/paper.docx')
        >>> print(metadata['title'])
        'Advanced Machine Learning Techniques'
    """
    ...
```

### Frontend (TypeScript/Vue)

#### ESLint + Prettier

```typescript
// ✅ İyi
interface Submission {
  id: number
  title: string
  status: SubmissionStatus
  createdAt: string
  updatedAt: string
}

export const createSubmission = async (
  data: CreateSubmissionRequest
): Promise<Submission> => {
  const response = await apiClient.post<Submission>('/submissions/', data)
  return response.data
}

// ❌ Kötü
export const createSubmission = async (data: any): Promise<any> => {
  const response = await apiClient.post('/submissions/', data);
  return response.data;
};
```

#### Vue 3 Composition API

```vue
<script setup lang="ts">
// ✅ İyi
import { ref, computed, onMounted } from 'vue'
import { useSubmissionStore } from '@/stores/submission'

interface Props {
  submissionId: number
}

const props = defineProps<Props>()
const submissionStore = useSubmissionStore()

const isLoading = ref(false)
const submission = computed(() => 
  submissionStore.getById(props.submissionId)
)

onMounted(async () => {
  if (!submission.value) {
    isLoading.value = true
    await submissionStore.fetchById(props.submissionId)
    isLoading.value = false
  }
})
</script>

<template>
  <div v-if="isLoading">Loading...</div>
  <div v-else-if="submission">
    <h1>{{ submission.title }}</h1>
  </div>
</template>
```

## 🧪 Test Yazma

### Backend (pytest + factory_boy)

```python
import pytest
from django.contrib.auth import get_user_model
from submissions.models import Submission, SubmissionStatus
from submissions.tests.factories import SubmissionFactory, UserFactory

User = get_user_model()

@pytest.mark.django_db
class TestSubmissionCreation:
    def test_create_submission_success(self):
        """Test successful submission creation."""
        user = UserFactory()
        submission = SubmissionFactory(user=user, title="Test Paper")
        
        assert submission.id is not None
        assert submission.status == SubmissionStatus.DRAFT
        assert submission.user == user
        
    def test_create_submission_without_user_fails(self):
        """Test that submission requires a user."""
        with pytest.raises(ValueError):
            Submission.objects.create(title="Test Paper")
            
    def test_submission_status_transition(self):
        """Test submission status transitions."""
        submission = SubmissionFactory(status=SubmissionStatus.DRAFT)
        
        submission.submit()
        submission.save()
        
        assert submission.status == SubmissionStatus.SUBMITTED
```

### Frontend (Vitest)

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSubmissionStore } from '@/stores/submission'

describe('Submission Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('creates a new submission', async () => {
    const store = useSubmissionStore()
    
    const newSubmission = {
      title: 'Test Paper',
      abstract: 'Test abstract'
    }
    
    await store.create(newSubmission)
    
    expect(store.submissions).toHaveLength(1)
    expect(store.submissions[0].title).toBe('Test Paper')
  })

  it('filters submissions by status', () => {
    const store = useSubmissionStore()
    
    store.submissions = [
      { id: 1, title: 'Draft', status: 'draft' },
      { id: 2, title: 'Submitted', status: 'submitted' }
    ]
    
    const drafts = store.getByStatus('draft')
    
    expect(drafts).toHaveLength(1)
    expect(drafts[0].title).toBe('Draft')
  })
})
```

## 📊 Code Coverage

Minimum coverage hedefleri:

- **Backend**: 80%
- **Frontend**: 70%

```bash
# Backend coverage
cd backend
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Frontend coverage
cd frontend
npm run test:coverage
```

## 🚀 Release Süreci

### Version Numbering (SemVer)

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Changelog Güncelleme

```markdown
## [1.2.0] - 2025-11-19

### Added
- ORCID authentication support (#123)
- Multi-file upload capability (#145)

### Changed
- Improved PDF metadata extraction performance (#156)

### Fixed
- File upload progress bar not updating (#167)

### Security
- Updated Django to 5.0.1 (CVE-2024-XXXX)
```

## 📞 İletişim

- **GitHub Issues**: Teknik sorular ve bug report
- **Discussions**: Genel tartışmalar, öneriler
- **Discord**: Real-time chat
- **Email**: dev@editorial-system.com

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.
