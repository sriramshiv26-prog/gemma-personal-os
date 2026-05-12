---
name: compliance-mapping
version: 1.0
domain: Regulatory Compliance
description: Framework mapping for GDPR, HIPAA, SOC2, PCI-DSS, ISO27001
dependencies:
  - regulatory-frameworks
  - compliance-standards
  - audit-templates
---

# Compliance Mapping SKILL

Framework for identifying compliance requirements and mapping organizational controls to regulatory standards.

## Supported Frameworks

### GDPR (General Data Protection Regulation - EU)

**Scope:** Any organization processing data of EU residents

**Key Requirements:**
- Data minimization (collect only necessary data)
- Purpose limitation (use data only for stated purpose)
- Storage limitation (delete after purpose met)
- Subject access rights (user can request their data)
- Data breach notification (72 hours)
- Privacy by design
- Data Protection Impact Assessment (DPIA)

**Critical Controls:**
- [ ] Document lawful basis for each data collection
- [ ] Maintain record of processing (register of activities)
- [ ] Data subject consent and withdrawal mechanism
- [ ] DPA with data processors (article 28 agreement)
- [ ] Data retention policy (auto-delete after period)
- [ ] Breach notification process (legal+technical notification)
- [ ] Privacy policy with clear language

**Compliance Gaps Example:**
```
MISSING: Data retention policy
REQUIRED: Clear statement on how long data retained
FIX: Implement auto-deletion after 12 months (or justify longer retention)

MISSING: Breach notification process
REQUIRED: 72-hour notification to authorities
FIX: Create incident response plan with escalation path
```

### HIPAA (Health Insurance Portability & Accountability - USA)

**Scope:** Healthcare providers, insurers, health plans

**Key Requirements:**
- Protected Health Information (PHI) encryption
- Access controls and authentication (MFA)
- Audit logging of all PHI access
- Breach notification (60 days)
- Business Associate Agreements (BAAs)
- Disaster recovery and backup

**Critical Controls:**
- [ ] Encrypt PHI in transit (TLS 1.2+) and at rest (AES-256)
- [ ] Implement role-based access control (RBAC)
- [ ] Enable audit logging with 6-year retention
- [ ] MFA for all system access
- [ ] BAAs signed with all third parties accessing PHI
- [ ] Incident response plan with breach assessment
- [ ] Annual risk assessment and documentation

**Compliance Gaps Example:**
```
MISSING: Audit logging
REQUIRED: All PHI access logged with user/timestamp/action
FIX: Enable database audit logs, log application access

MISSING: Encryption at rest
REQUIRED: AES-256 for all stored PHI
FIX: Enable database encryption, verify backups encrypted
```

### SOC2 (Service Organization Control)

**Scope:** Service providers (SaaS, cloud, hosting)

**Key Areas:**
- Security (protect against unauthorized access)
- Availability (systems operate and perform as intended)
- Processing Integrity (complete, accurate, timely processing)
- Confidentiality (protected against unauthorized disclosure)
- Privacy (personal information collected per privacy notice)

**Critical Controls:**
- [ ] Network segmentation and firewalls
- [ ] Vulnerability scanning and patch management
- [ ] Access controls with MFA
- [ ] Change management process
- [ ] Monitoring and alerting
- [ ] Incident response procedure
- [ ] Business continuity and disaster recovery
- [ ] Annual third-party audit

### PCI-DSS (Payment Card Industry Data Security Standard)

**Scope:** Any organization processing payment cards

**Key Requirements:**
- Network security and firewalls
- Protect cardholder data encryption
- Vulnerability management program
- Access control and RBAC
- Regular security testing
- Information security policy
- Card data never stored unencrypted

**Critical Controls:**
- [ ] PCI-compliant infrastructure (firewalls, IDS/IPS)
- [ ] Encrypt cardholder data in transit (TLS) and at rest
- [ ] Never store CVV/PIN
- [ ] Vulnerability scans quarterly, penetration test annually
- [ ] Employee training on PCI compliance
- [ ] Incident response plan

### ISO 27001 (Information Security Management)

**Scope:** Any organization with information security needs

**Key Controls (114 total):**
- Organizational controls (policies, roles)
- People controls (training, awareness)
- Physical controls (access, surveillance)
- Technical controls (encryption, authentication, logging)

**Critical Controls:**
- [ ] Information security policy and governance
- [ ] Asset inventory and classification
- [ ] Access control and RBAC
- [ ] Encryption standards (transit/at-rest)
- [ ] Incident management procedure
- [ ] Business continuity planning
- [ ] Annual management review

## Compliance Mapping Process

### Step 1: Identify Applicable Frameworks
```
QUESTION: What regulations apply?
ANSWER: 
- GDPR (if any EU residents data)
- HIPAA (if healthcare data)
- SOC2 (if SaaS provider)
- PCI-DSS (if payment cards)
- Custom (industry-specific)
```

### Step 2: Document Current Controls
```
For each requirement:
1. Identify existing control (automated, manual, missing)
2. Assess implementation status (Implemented/Partial/Missing)
3. Document evidence (screenshots, logs, policies)
```

### Step 3: Identify Gaps
```
Gap = Requirement - Current Control

Example:
REQUIREMENT: Audit logging of all system access
CURRENT: No centralized audit logging
GAP: Missing audit infrastructure
PRIORITY: Critical (required for compliance)
```

### Step 4: Remediation Plan
```
For each gap:
1. Determine effort (low/medium/high)
2. Assign owner and timeline
3. Identify dependencies
4. Document success criteria
```

## Output Format

```json
{
  "assessment_date": "2026-05-12",
  "organization": "company-name",
  "frameworks_assessed": ["GDPR", "HIPAA"],
  "findings": [
    {
      "framework": "GDPR",
      "requirement": "Data retention policy (Article 5)",
      "status": "Missing",
      "priority": "Critical",
      "remediation": "Implement 12-month auto-delete for user data",
      "timeline": "30 days",
      "owner": "Data Protection Officer"
    }
  ],
  "summary": {
    "total_requirements": 45,
    "implemented": 28,
    "partial": 10,
    "missing": 7,
    "overall_compliance": "62%"
  }
}
```

## Audit Evidence Checklist

- [ ] Documented policies and procedures
- [ ] Risk assessment and risk register
- [ ] Data flow diagrams
- [ ] System inventory with classifications
- [ ] Access control matrix (who can access what)
- [ ] Encryption inventory (in-transit, at-rest)
- [ ] Incident logs and response procedures
- [ ] Training records
- [ ] Penetration test reports
- [ ] Business continuity plan and test results
- [ ] Third-party audit reports (SOC2, ISO27001)

---

**Last Updated:** May 2026
