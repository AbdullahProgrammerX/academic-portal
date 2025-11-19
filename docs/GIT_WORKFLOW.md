# Git Workflow & Branch Protection Strategy

## 📋 Branch Yapısı

```
main (production)
  ↓
develop (staging)
  ↓
feature/* (geliştirme)
bugfix/* (hata düzeltme)
hotfix/* (acil düzeltme)
release/* (sürüm hazırlığı)
```

## 🌿 Branch Türleri

### 1. Main Branch (Production)
- **Korumalı**: Direkt push yasak
- **Merge Şartı**: Develop'dan PR + 2 approval
- **Tag**: Her merge versiyon tag'i alır (v1.0.0, v1.1.0)
- **CI/CD**: Otomatik production deployment
- **Rollback**: Her zaman önceki tag'e dönülebilir

**Kurallar:**
```yaml
# .github/branch-protection-rules.yml
main:
  required_reviews: 2
  require_code_owner_review: true
  required_status_checks:
    - lint-backend
    - lint-frontend
    - test-backend
    - test-frontend
    - build-docker
  enforce_admins: true
  require_linear_history: true
  allow_force_pushes: false
  allow_deletions: false
```

### 2. Develop Branch (Staging)
- **Korumalı**: Direkt push yasak
- **Merge Şartı**: Feature branch'lerden PR + 1 approval
- **CI/CD**: Otomatik staging deployment
- **Test**: Integration testleri çalışır

**Kurallar:**
```yaml
develop:
  required_reviews: 1
  required_status_checks:
    - lint-backend
    - lint-frontend
    - test-backend
    - test-frontend
  allow_force_pushes: false
```

### 3. Feature Branches
- **İsimlendirme**: `feature/issue-number-short-description`
- **Kaynak**: develop
- **Hedef**: develop
- **Ömür**: Merge sonrası silinir
- **Commit**: Squash merge (tercih)

**Örnekler:**
```bash
feature/123-orcid-authentication
feature/124-multi-file-upload
feature/125-dashboard-filters
```

**Workflow:**
```bash
# 1. develop'dan dal oluştur
git checkout develop
git pull origin develop
git checkout -b feature/123-orcid-authentication

# 2. Geliştirme yap
git add .
git commit -m "feat(auth): add ORCID OAuth flow"

# 3. Remote'a push
git push -u origin feature/123-orcid-authentication

# 4. GitHub'da PR aç (develop ← feature/123-orcid-authentication)

# 5. Review sonrası merge
# 6. Branch'i sil
git checkout develop
git pull origin develop
git branch -d feature/123-orcid-authentication
git push origin --delete feature/123-orcid-authentication
```

### 4. Bugfix Branches
- **İsimlendirme**: `bugfix/issue-number-short-description`
- **Kaynak**: develop
- **Hedef**: develop

**Örnekler:**
```bash
bugfix/456-pdf-upload-error
bugfix/457-dashboard-loading-issue
```

### 5. Hotfix Branches
- **İsimlendirme**: `hotfix/issue-number-short-description`
- **Kaynak**: main
- **Hedef**: main + develop (iki PR)
- **Aciliyet**: Yüksek (production bug)

**Workflow:**
```bash
# 1. main'den dal oluştur
git checkout main
git pull origin main
git checkout -b hotfix/789-security-vulnerability

# 2. Hızlı fix
git add .
git commit -m "fix(security): patch XSS vulnerability"

# 3. Test et
pytest
npm run test

# 4. İki PR aç:
#    - main ← hotfix/789-security-vulnerability
#    - develop ← hotfix/789-security-vulnerability

# 5. Merge sonrası tag oluştur
git checkout main
git pull origin main
git tag -a v1.0.1 -m "Hotfix: Security patch"
git push origin v1.0.1
```

### 6. Release Branches
- **İsimlendirme**: `release/version-number`
- **Kaynak**: develop
- **Hedef**: main + develop
- **Amaç**: Sürüm stabilizasyonu

**Workflow:**
```bash
# 1. develop'dan release branch
git checkout develop
git pull origin develop
git checkout -b release/1.2.0

# 2. Version bump
# package.json, __init__.py, etc. güncelle

# 3. CHANGELOG.md güncelle
# 4. Final testler
# 5. main'e merge + tag
# 6. develop'a back-merge
```

## 📝 Commit Message Convention

### Semantic Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add ORCID OAuth` |
| `fix` | Bug fix | `fix(upload): resolve timeout` |
| `docs` | Documentation | `docs(api): update endpoints` |
| `style` | Formatting | `style: apply black formatting` |
| `refactor` | Code restructure | `refactor(models): simplify queries` |
| `perf` | Performance | `perf(api): add caching layer` |
| `test` | Tests | `test(submissions): add unit tests` |
| `chore` | Maintenance | `chore(deps): update Django to 5.0.1` |
| `ci` | CI/CD | `ci: add GitHub Actions workflow` |
| `build` | Build system | `build: configure webpack` |
| `revert` | Revert commit | `revert: revert "feat: add feature"` |

### Scope Examples

- `auth` - Authentication/authorization
- `submissions` - Manuscript submissions
- `revisions` - Revision workflow
- `files` - File handling
- `api` - API endpoints
- `ui` - User interface
- `db` - Database
- `deps` - Dependencies

### Commit Examples

**Good ✅:**
```bash
feat(auth): implement ORCID OAuth integration

- Add ORCID client configuration
- Implement OAuth callback handler
- Create user profile from ORCID data
- Add tests for OAuth flow

Closes #123
```

```bash
fix(upload): resolve file upload timeout for large files

Previous implementation used synchronous upload which caused
timeouts for files >50MB. Now using chunked upload with
progress tracking.

- Implement chunked upload (5MB chunks)
- Add progress callback
- Update frontend progress bar

Fixes #456
```

**Bad ❌:**
```bash
# Too vague
update files

# No type/scope
fixed a bug

# Too long single line
feat: add new feature that allows users to upload multiple files and track progress with detailed analytics
```

## 🔄 Pull Request Process

### PR Template

```markdown
## 📋 Description
Brief description of changes

## 🎯 Related Issue
Closes #[issue-number]

## 🔄 Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## ✅ Checklist
- [ ] Code tested locally
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Linting passes
- [ ] Migrations created (if needed)
- [ ] CHANGELOG.md updated

## 🧪 Testing
How was this tested?

## 📸 Screenshots
(If UI changes)
```

### Review Requirements

**Feature/Bugfix (to develop):**
- ✅ 1 approval required
- ✅ All CI checks pass
- ✅ No merge conflicts
- ✅ Up-to-date with develop

**Release/Hotfix (to main):**
- ✅ 2 approvals required
- ✅ All CI checks pass
- ✅ Security scan clean
- ✅ Performance benchmarks pass
- ✅ Code owner approval

### Merge Strategies

**Squash Merge (Default for features):**
```bash
# All commits → 1 commit
# Clean history
git merge --squash feature/123-new-feature
```

**Merge Commit (Hotfixes):**
```bash
# Preserve commit history
# Good for tracking emergency fixes
git merge --no-ff hotfix/789-urgent-fix
```

**Rebase Merge (Small fixes):**
```bash
# Linear history
git rebase develop
git merge --ff-only feature/123-small-fix
```

## 🏷️ Tagging Strategy

### Version Format (SemVer)

```
v<MAJOR>.<MINOR>.<PATCH>[-<PRERELEASE>]

Examples:
v1.0.0         # Stable release
v1.1.0-beta.1  # Beta release
v1.0.1         # Patch release
v2.0.0         # Major release
```

### Tag Creation

```bash
# Annotated tag (recommended)
git tag -a v1.0.0 -m "Release version 1.0.0

- Feature A
- Feature B
- Bug fixes"

# Push tags
git push origin v1.0.0

# List tags
git tag -l

# Show tag details
git show v1.0.0
```

## 🚨 Emergency Procedures

### Hotfix Protocol

1. **Identify**: Critical bug in production
2. **Branch**: Create hotfix from main
3. **Fix**: Minimal code change
4. **Test**: Thorough testing
5. **PR**: Two PRs (main + develop)
6. **Deploy**: Fast-track approval
7. **Tag**: Version bump (patch)
8. **Monitor**: Post-deployment monitoring

### Rollback Procedure

```bash
# Option 1: Revert commit
git revert <commit-hash>
git push origin main

# Option 2: Reset to tag
git checkout main
git reset --hard v1.0.0
git push origin main --force  # Requires admin override

# Option 3: Deploy previous tag
git checkout v1.0.0
# Deploy from this detached HEAD
```

## 📊 Branch Management

### Stale Branch Cleanup

```bash
# List merged branches
git branch --merged develop

# Delete local merged branches
git branch --merged develop | grep -v "^\*\|main\|develop" | xargs git branch -d

# Delete remote branches
git push origin --delete feature/old-feature

# Prune remote tracking branches
git fetch --prune
```

### Branch Naming Rules

✅ **Good:**
- `feature/123-orcid-authentication`
- `bugfix/456-dashboard-crash`
- `hotfix/789-security-patch`
- `docs/update-api-documentation`

❌ **Bad:**
- `my-feature` (no issue number)
- `fix` (too generic)
- `john-dev` (personal branch)
- `test123` (unclear purpose)

## 🔐 Protected Branch Settings

### GitHub Settings

**Main Branch:**
```
☑ Require pull request reviews before merging
  ☑ Require approvals: 2
  ☑ Dismiss stale pull request approvals
  ☑ Require review from Code Owners
☑ Require status checks to pass
  ☑ Require branches to be up to date
  - lint-backend
  - lint-frontend
  - test-backend
  - test-frontend
☑ Require conversation resolution before merging
☑ Require signed commits
☑ Require linear history
☑ Include administrators
☐ Allow force pushes (NEVER)
☐ Allow deletions (NEVER)
```

**Develop Branch:**
```
☑ Require pull request reviews before merging
  ☑ Require approvals: 1
☑ Require status checks to pass
  - lint-backend
  - lint-frontend
  - test-backend
  - test-frontend
☑ Require conversation resolution before merging
☐ Allow force pushes (Only with force push allowance)
☐ Allow deletions (NEVER)
```

## 📚 Resources

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
