# 🛡️ Project Name

![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci-cd.yml/badge.svg)
![Security Scan](https://img.shields.io/badge/security-gitleaks%20%7C%20trivy%20%7C%20OWASP-green)
![Docker](https://img.shields.io/badge/docker-multi--stage-blue)
![Deploy](https://img.shields.io/badge/deploy-railway-purple)



## 🔗 Live Demo

**[→ Відкрити застосунок](https://your-app.railway.app)**

## 🏗️ Архітектура

```
code push
    │
    ▼
GitHub Actions Pipeline
    │
    ├── 🔑 Gitleaks (secrets scan)
    ├── 🔍 Bandit + Semgrep (SAST)
    ├── 📦 Snyk (dependency scan)
    ├── 🐳 Docker build
    ├── 🛡️ Trivy + Checkov (container + IaC scan)
    ├── 🚀 Deploy → Railway
    └── 🎯 OWASP ZAP (DAST)
```

## 🚀 Швидкий старт

### Локально через Docker

```bash
# 1. Клонуй репо
git clone https://github.com/YOUR_USERNAME/YOUR_REPO
cd YOUR_REPO

# 2. Налаштуй змінні середовища
cp .env.example .env
# Відредагуй .env своїми значеннями

# 3. Запусти
docker-compose -f docker/docker-compose.yml up --build

# 4. Відкрий в браузері
# http://localhost:8000
```

### Локально без Docker

```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🔐 Security

Дивись [docs/SECURITY.md](docs/SECURITY.md) для повного опису security pipeline.

**Ключові практики:**
- Secrets scanning на кожен коміт (Gitleaks)
- SAST аналіз коду (Bandit + Semgrep)
- Dependency vulnerability scan (Snyk)
- Container scan (Trivy)
- IaC misconfiguration check (Checkov)
- DAST на живому деплої (OWASP ZAP)
- Multi-stage Docker build + non-root user

## 🌿 Git Flow

```
main          ──●────────────────●──  (production, protected)
                 \              /
develop       ────●────●────●──       (основна розробка)
                       \
feature/xxx   ──────────●────         (нові фічі)
```

## ⚙️ GitHub Secrets

Додай в Settings → Secrets and variables → Actions:

| Secret | Опис |
|--------|------|
| `RAILWAY_TOKEN` | Railway API токен |
| `SNYK_TOKEN` | Snyk API токен (optional) |
| `SEMGREP_APP_TOKEN` | Semgrep токен (optional) |

## 👥 Команда

| Роль | Відповідальність |
|------|-----------------|
| DevSecOps | CI/CD pipeline, Docker, security tools |
| Backend | API, бізнес-логіка |
| Frontend | UI/UX |