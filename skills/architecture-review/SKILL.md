---
name: architecture-review
version: 1.0
domain: Software Architecture
description: Framework for reviewing system architecture, trade-offs, and design patterns
dependencies:
  - design-patterns
  - architecture-principles
  - technology-radar
---

# Architecture Review SKILL

Framework for evaluating system architecture, assessing design decisions, and recommending improvements.

## Architecture Review Dimensions

### 1. Scalability Assessment

**Vertical Scaling (single machine):**
- Current capacity: N users, M RPS (requests per second)
- Bottleneck analysis (CPU, memory, disk, network)
- Upgrade path (RAM, CPU, storage)
- Limits (typical: 10K users on single machine)

**Horizontal Scaling (multiple machines):**
- Stateless vs stateful components
- Database sharding strategy
- Load balancing approach (round-robin, least-conn, sticky)
- Cache layer (Redis, Memcached)
- Message queue for async (RabbitMQ, Kafka)

**Evaluation Checklist:**
- [ ] Can add more servers without code changes?
- [ ] Are sessions/state distributed or centralized?
- [ ] Is database replication/sharding planned?
- [ ] Are async jobs decoupled (message queue)?
- [ ] Is caching strategy documented?

### 2. Reliability & Fault Tolerance

**Failure Modes:**
- Database unavailable → fallback to read-only cache
- Service down → circuit breaker with fallback
- Network latency → timeout and retry logic
- Cascading failures → rate limiting and bulkheads

**Resilience Patterns:**
```
Circuit Breaker: Fail fast if service unhealthy
Retry with backoff: Exponential backoff (1s, 2s, 4s...)
Timeout: 30s for external APIs, 5s for internal
Fallback: Cached result or degraded functionality
Bulkhead: Isolate thread pools per service
```

**Checklist:**
- [ ] Database replication/failover configured?
- [ ] Circuit breakers for external calls?
- [ ] Retry logic with exponential backoff?
- [ ] Request timeouts defined?
- [ ] Monitoring and alerting in place?
- [ ] Disaster recovery plan tested annually?

### 3. Technology & Framework Choices

**Evaluation Criteria:**
- **Maturity:** Stable, battle-tested, not bleeding-edge
- **Community:** Active maintenance, large ecosystem
- **Hiring:** Can you find engineers for this stack?
- **Licensing:** Open source, commercial support available
- **Performance:** Meets requirements, benchmarked
- **Maintainability:** Clear patterns, good documentation

**Red Flags:**
- ✗ Bleeding-edge tech with no production use
- ✗ Dead/abandoned projects (no commits in 1+ year)
- ✗ Overly complex for problem size
- ✗ Single vendor lock-in without escape hatch
- ✗ Custom framework instead of established solution

### 4. Data Architecture

**Database Selection:**
- Relational (PostgreSQL, MySQL): Structured, ACID, joins needed
- NoSQL (MongoDB, DynamoDB): Unstructured, eventual consistency, horizontal scaling
- Cache (Redis, Memcached): Sub-millisecond latency, volatile
- Search (Elasticsearch): Full-text search, analytics
- Time-series (InfluxDB, TimescaleDB): Metrics, logs, events

**Design Issues:**
- ✗ Denormalization causing inconsistency
- ✗ N+1 query problem in application
- ✗ Missing database indexes
- ✗ No query optimization (execution plans)
- ✗ Unsharded database at scale

**Checklist:**
- [ ] Database choice justified (relational vs NoSQL)?
- [ ] Schema normalized (3NF minimum)?
- [ ] Indexes on foreign keys, common filters?
- [ ] Query performance reviewed (slow queries logged)?
- [ ] Backup/recovery strategy documented?
- [ ] Replication/failover configured?

### 5. API Design & Integration

**REST API Best Practices:**
- Resource-based URLs (not verb-based)
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Versioning (v1, v2 in URL or header)
- Pagination for large results
- Consistent error responses

**Example:**
```
GOOD: GET /api/v1/users/{id}/orders?page=1&limit=20
BAD: GET /api/getUser?user_id=123

GOOD: POST /api/v1/orders { ... } -> 201 Created
BAD: POST /api/createOrder { ... } -> 200 OK
```

**Checklist:**
- [ ] Resources are nouns, not verbs?
- [ ] HTTP methods match semantics (idempotency)?
- [ ] Version strategy documented?
- [ ] Rate limiting implemented?
- [ ] Error responses consistent (status code + error object)?
- [ ] Authentication/authorization on all endpoints?

### 6. Security Architecture

**Defense Layers:**
```
1. Network: Firewalls, VPN, DDoS protection
2. Application: Input validation, output encoding, CSRF tokens
3. Data: Encryption (transit, at rest), secrets management
4. Access: Authentication, authorization, audit logging
5. Monitoring: Intrusion detection, anomaly detection
```

**Checklist:**
- [ ] Network segmentation (DMZ, internal, database)?
- [ ] WAF (Web Application Firewall) in front?
- [ ] All data encrypted in transit (HTTPS, TLS)?
- [ ] Sensitive data encrypted at rest?
- [ ] Secrets not in code (environment variables)?
- [ ] MFA for critical systems?
- [ ] Audit logging enabled and reviewed?
- [ ] Security headers configured (HSTS, CSP, X-Frame)?

### 7. Operational Concerns

**Deployment:**
- Infrastructure as Code (Terraform, CloudFormation)
- Containerization (Docker) and orchestration (Kubernetes)
- Continuous Integration/Deployment (CI/CD pipeline)
- Blue-green or canary deployments for zero-downtime

**Monitoring:**
- Application metrics (latency, throughput, errors)
- Infrastructure metrics (CPU, memory, disk, network)
- Business metrics (user signups, conversion, revenue)
- Centralized logging (ELK, Splunk, CloudWatch)

**Runbook:** 
- How to scale up/down?
- How to deploy new version?
- How to roll back?
- How to handle outage?
- Who to contact on-call?

**Checklist:**
- [ ] Infrastructure as Code version controlled?
- [ ] Automated deployment pipeline in place?
- [ ] Canary/blue-green deployment possible?
- [ ] Monitoring dashboards show key metrics?
- [ ] Alerting configured for critical events?
- [ ] Centralized logs queryable?
- [ ] Runbooks documented for common operations?

## Review Output Format

```json
{
  "review_date": "2026-05-12",
  "system": "gemma-personal-os",
  "aspects": [
    {
      "dimension": "Scalability",
      "status": "Good",
      "score": "8/10",
      "strengths": [
        "Stateless design enables horizontal scaling",
        "Database read replicas configured"
      ],
      "risks": [
        "No message queue for async jobs yet",
        "Cache invalidation strategy not documented"
      ],
      "recommendations": [
        "Implement message queue (Kafka, RabbitMQ) for background tasks",
        "Document cache invalidation strategy"
      ]
    }
  ],
  "overall_score": "7.5/10",
  "priority_actions": [
    {
      "action": "Implement distributed caching layer",
      "rationale": "Current single-instance cache is bottleneck at scale",
      "effort": "Medium (2 weeks)",
      "impact": "High (30% latency reduction expected)"
    }
  ]
}
```

## Design Pattern Evaluation

**Common Patterns:**
- MVC/MVVM: Separation of concerns
- Microservices: Independent scaling and deployment
- CQRS: Separate read/write models for optimization
- Event sourcing: Immutable event log for replay/recovery
- Saga: Distributed transaction coordination

**Anti-patterns (to avoid):**
- ✗ God object/class (too many responsibilities)
- ✗ Circular dependencies
- ✗ Deep inheritance hierarchies
- ✗ Magic strings/numbers (use constants)
- ✗ Hidden side effects in functions

---

**Last Updated:** May 2026
