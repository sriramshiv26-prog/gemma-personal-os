---
name: security-auditing
version: 1.0
domain: Application Security
description: Comprehensive security code auditing and vulnerability detection
dependencies: 
  - owasp-top-10
  - cwe-database
  - secure-coding-standards
---

# Security Auditing SKILL

Comprehensive framework for identifying, analyzing, and remediating security vulnerabilities.

## Core Vulnerability Categories

### 1. Input Validation & Injection (CWE-89, CWE-79)

**SQL Injection:**
- User input concatenated into SQL queries
- Dynamic query building without parameterization
- Framework ORM bypass vulnerabilities

**Detection Patterns:**
- String concatenation with user input in queries
- Format strings in SQL
- f-strings/templates without escaping

**Remediation:**
- Use parameterized queries/prepared statements
- Use ORM with parameterized outputs
- Validate and whitelist input

### 2. Authentication & Session Management (CWE-287)

**Issues:**
- Plaintext password storage
- Weak hashing (MD5, SHA1)
- Predictable session tokens
- Missing CSRF protection
- No session timeout

**Remediation:**
- Use bcrypt/scrypt/PBKDF2 with salt
- Implement CSRF tokens
- Set HttpOnly, Secure, SameSite flags
- Session expiry: 15-30 min inactivity

### 3. Authorization & Access Control (CWE-639)

**Common Issues:**
- Missing authorization checks
- Direct object reference (no ownership validation)
- Privilege escalation paths
- Role-based access not enforced

**Detection:**
- Check every protected endpoint for role validation
- Verify user owns resource before allowing access
- Audit permission matrices

### 4. Data Protection & Encryption (CWE-311)

**Issues:**
- Sensitive data in logs (passwords, tokens, PII)
- Hardcoded credentials
- Unencrypted transmission
- Plaintext storage of sensitive data

**Remediation:**
- Never log passwords/tokens/PII
- Use environment variables for secrets
- Enforce HTTPS/TLS 1.3
- Encrypt sensitive data at rest (AES-256)

### 5. Error Handling & Information Disclosure (CWE-209)

**Issues:**
- Stack traces shown to users
- Detailed error messages (user enumeration)
- Debug mode in production
- Verbose API responses

**Remediation:**
- Generic error messages to users
- Log detailed errors server-side only
- Disable debug mode
- Sanitize API responses

### 6. Dependency Vulnerabilities (CWE-1035)

**Detection:**
- npm audit, pip check, gradle dependencyCheck
- OWASP Dependency-Check
- Snyk scanning

## Severity Classification

| Level | CVSS | Impact | Example |
|-------|------|--------|---------|
| Critical | 9.0-10.0 | System compromise | SQL injection, auth bypass |
| High | 7.0-8.9 | Major functionality broken | XSS, privilege escalation |
| Medium | 4.0-6.9 | Partial compromise | Weak hashing, info leak |
| Low | 0.1-3.9 | Minor impact | Outdated library |

## Audit Checklist

- [ ] No SQL injection vulnerabilities found
- [ ] Password hashing uses bcrypt/scrypt
- [ ] CSRF protection implemented
- [ ] All sensitive data encrypted
- [ ] Error messages don't leak information
- [ ] Dependencies scanned and up-to-date
- [ ] Authorization checks on all endpoints
- [ ] Secure headers (HSTS, CSP, X-Frame-Options)
- [ ] Input validation on all entry points
- [ ] Secrets not in version control

## Output Format

```json
{
  "findings": [
    {
      "id": "SEC-001",
      "type": "SQL Injection",
      "severity": "Critical",
      "cvss_score": 9.1,
      "location": "src/api/auth.py:45",
      "description": "User input concatenated in SQL",
      "fix": "Use parameterized queries"
    }
  ],
  "summary": {
    "total": 12,
    "critical": 2,
    "high": 5,
    "medium": 4,
    "low": 1
  }
}
```

---

**Last Updated:** May 2026
