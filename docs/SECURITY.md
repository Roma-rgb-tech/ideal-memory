# Security

## Pipeline Security Gates

| Крок | Інструмент | Що перевіряє |
|------|-----------|--------------|
| 1 | **Gitleaks** | Secrets та токени в коді |
| 2 | **Bandit** | Вразливості в Python коді (SAST) |
| 3 | **Semgrep** | Статичний аналіз коду |
| 4 | **Snyk** | Вразливості в залежностях |
| 5 | **Checkov** | Misconfigurations в IaC та Dockerfile |
| 6 | **Trivy** | CVE вразливості в Docker образі |
| 7 | **OWASP ZAP** | Динамічне тестування живого деплою (DAST) |

## Docker Security

- ✅ Multi-stage build — менший образ, менша attack surface
- ✅ Non-root user — контейнер не запускається від root
- ✅ Read-only filesystem — захист від запису
- ✅ Resource limits — обмеження CPU та пам'яті
- ✅ Health check — моніторинг стану контейнера

## Secrets Management

- ✅ Всі секрети зберігаються в GitHub Secrets
- ✅ `.env` файл додано в `.gitignore`
- ✅ `.env.example` — шаблон без реальних значень
- ✅ Gitleaks перевіряє кожен коміт

## Security Reports

Всі звіти зберігаються як артефакти в GitHub Actions:
- `bandit-report.json` — SAST результати
- `snyk-report.json` — dependency vulnerabilities
- `trivy-report.sarif` — container scan (видно в Security tab)
- `checkov-report.json` — IaC misconfigurations
- `report_html.html` — OWASP ZAP DAST результати