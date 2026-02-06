# Project Chimera - Security Specification
**Version:** 1.0.0  
**Status:** DRAFT → REVIEW → RATIFIED  
**Last Updated:** 2026-02-06  
**Addresses:** Feedback Gap - Formalized Security & Acceptance Criteria

---

## 1. Security Architecture Overview

### 1.1 Defense in Depth Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    LAYER 7: Monitoring                   │
│  [Audit Logs] [Intrusion Detection] [Anomaly Detection] │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  LAYER 6: Data Protection                │
│  [Encryption at Rest] [Encryption in Transit] [Secrets] │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                LAYER 5: Application Security             │
│  [Input Validation] [Output Encoding] [CSRF Protection] │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   LAYER 4: API Security                  │
│  [JWT Auth] [Rate Limiting] [API Gateway] [CORS]        │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                 LAYER 3: Network Security                │
│  [Firewall] [VPC] [TLS 1.3] [DDoS Protection]          │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              LAYER 2: Infrastructure Security            │
│  [Container Isolation] [Least Privilege] [Hardening]    │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                 LAYER 1: Physical Security               │
│  [Cloud Provider SOC2] [Multi-AZ] [Backups]            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Authentication & Authorization

### 2.1 User Authentication (Human Operators)

**Requirement:** SEC-001  
**Priority:** P0 (Critical)

**Specification:**
```yaml
authentication:
  method: JWT (JSON Web Tokens)
  provider: Auth0 / AWS Cognito
  mfa_required: true
  session_timeout: 30 minutes
  refresh_token_ttl: 7 days
  
jwt_claims:
  sub: user_id
  email: user_email
  roles: [admin, operator, viewer]
  permissions: [agent:create, agent:delete, hitl:approve]
  
password_requirements:
  min_length: 12
  require_uppercase: true
  require_lowercase: true
  require_numbers: true
  require_special_chars: true
  prevent_reuse: 5 previous passwords
```

**Acceptance Criteria:**
- [ ] Users cannot log in without valid credentials
- [ ] MFA is enforced for all production accounts
- [ ] JWT tokens expire after 30 minutes
- [ ] Refresh tokens allow seamless session extension
- [ ] Failed login attempts are logged (audit trail)
- [ ] Account lockout after 5 failed attempts (15 min cooldown)
- [ ] Password reset flow requires email verification
- [ ] All authentication events logged to audit_log table

**Test Cases:**
```python
def test_authentication_requires_valid_jwt():
    """SEC-001-TC1: Verify JWT required for API access"""
    response = client.get("/api/v1/agents", headers={})
    assert response.status_code == 401
    assert response.json()["error"] == "Unauthorized"

def test_mfa_enforced_for_production():
    """SEC-001-TC2: MFA required in production environment"""
    if ENVIRONMENT == "production":
        user = authenticate(email, password)
        assert user.mfa_enabled is True

def test_jwt_expiration_enforced():
    """SEC-001-TC3: Expired tokens rejected"""
    expired_token = generate_jwt(exp=datetime.now() - timedelta(hours=1))
    response = client.get("/api/v1/agents", 
                         headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
```

---

### 2.2 Agent Authorization (Autonomous Agents)

**Requirement:** SEC-002  
**Priority:** P0 (Critical)

**Specification:**
```yaml
agent_authentication:
  method: API Key + Agent ID
  rotation_period: 90 days
  key_format: "chimera_agent_{agent_id}_{random_32_chars}"
  
agent_permissions:
  scoped_by: agent_id
  allowed_actions:
    - read_own_profile
    - create_tasks (for self)
    - read_own_tasks
    - call_mcp_tools (whitelisted)
  forbidden_actions:
    - modify_other_agents
    - delete_agents
    - change_budgets
    - approve_hitl (requires human)
```

**Acceptance Criteria:**
- [ ] Each agent has unique API key
- [ ] Agent can only access own data (agent_id scoped)
- [ ] Agent cannot modify other agents' data
- [ ] Agent cannot escalate own permissions
- [ ] Agent API keys rotate every 90 days
- [ ] Revoked keys immediately invalidated
- [ ] All agent API calls logged with trace_id

**Test Cases:**
```python
def test_agent_cannot_access_other_agents():
    """SEC-002-TC1: Agent data isolation"""
    agent_a_key = create_agent_key("agent-001")
    response = client.get("/api/v1/agents/agent-002",
                         headers={"X-Agent-Key": agent_a_key})
    assert response.status_code == 403

def test_agent_key_rotation_enforced():
    """SEC-002-TC2: Keys expire after 90 days"""
    old_key = create_agent_key("agent-001", 
                               created_at=datetime.now() - timedelta(days=91))
    response = client.get("/api/v1/agents/agent-001",
                         headers={"X-Agent-Key": old_key})
    assert response.status_code == 401
    assert "key_expired" in response.json()["error"]
```

---

## 3. Data Security

### 3.1 Encryption at Rest

**Requirement:** SEC-003  
**Priority:** P0 (Critical)

**Specification:**
```yaml
encryption_at_rest:
  database:
    provider: AWS RDS / Azure Database
    algorithm: AES-256
    key_management: AWS KMS / Azure Key Vault
    key_rotation: Automatic (365 days)
    
  secrets:
    provider: HashiCorp Vault / AWS Secrets Manager
    encrypted_fields:
      - api_keys (Anthropic, Google, OpenAI)
      - wallet_private_keys
      - mcp_server_credentials
      - oauth_tokens
    
  file_storage:
    provider: AWS S3 / Azure Blob Storage
    algorithm: AES-256
    server_side_encryption: true
    bucket_policies: enforce_encryption
```

**Acceptance Criteria:**
- [ ] All databases encrypted at rest (AES-256)
- [ ] API keys stored in secrets manager (not environment variables)
- [ ] Wallet private keys encrypted with agent-specific KEK
- [ ] File uploads encrypted before storage
- [ ] Encryption keys rotated annually
- [ ] Backup data encrypted with same standards
- [ ] No plaintext secrets in logs or error messages

**Test Cases:**
```python
def test_database_encryption_enabled():
    """SEC-003-TC1: PostgreSQL encrypted at rest"""
    db_config = get_database_config()
    assert db_config.encryption_enabled is True
    assert db_config.encryption_algorithm == "AES-256"

def test_secrets_not_in_environment():
    """SEC-003-TC2: No secrets in env vars"""
    env_vars = os.environ
    forbidden_patterns = [
        r"sk-ant-",  # Anthropic API key
        r"sk-proj-", # OpenAI API key
        r"AIza",     # Google API key
    ]
    for var_value in env_vars.values():
        for pattern in forbidden_patterns:
            assert not re.search(pattern, var_value), \
                f"Secret found in environment: {pattern}"
```

---

### 3.2 Encryption in Transit

**Requirement:** SEC-004  
**Priority:** P0 (Critical)

**Specification:**
```yaml
encryption_in_transit:
  tls_version: TLS 1.3 (minimum 1.2)
  cipher_suites:
    - TLS_AES_256_GCM_SHA384
    - TLS_CHACHA20_POLY1305_SHA256
  certificate_provider: Let's Encrypt / AWS ACM
  hsts_enabled: true
  hsts_max_age: 31536000 # 1 year
  
  internal_communication:
    service_to_service: mTLS (mutual TLS)
    agent_to_orchestrator: TLS 1.3
    orchestrator_to_db: TLS 1.3
```

**Acceptance Criteria:**
- [ ] All HTTP traffic redirects to HTTPS
- [ ] TLS 1.3 enforced (1.2 minimum)
- [ ] Weak cipher suites disabled
- [ ] HSTS header present on all responses
- [ ] Internal service communication uses mTLS
- [ ] Certificate auto-renewal configured
- [ ] Certificate expiration monitoring enabled

**Test Cases:**
```python
def test_http_redirects_to_https():
    """SEC-004-TC1: HTTP traffic redirected"""
    response = requests.get("http://api.chimera.local", 
                           allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["Location"].startswith("https://")

def test_tls_version_enforced():
    """SEC-004-TC2: TLS 1.3 required"""
    context = ssl.create_default_context()
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    with pytest.raises(ssl.SSLError):
        requests.get("https://api.chimera.local", 
                    verify=context)
```

---

## 4. Input Validation & Sanitization

### 4.1 API Input Validation

**Requirement:** SEC-005  
**Priority:** P0 (Critical)

**Specification:**
```python
# All API inputs validated using Pydantic

from pydantic import BaseModel, Field, validator
from typing import Literal

class CreateAgentRequest(BaseModel):
    """
    SEC-005: Input validation for agent creation
    """
    name: str = Field(..., min_length=3, max_length=100, 
                     regex=r'^[a-zA-Z0-9\s\-_]+$')
    bio: str = Field(None, max_length=500)
    persona_file: str = Field(..., regex=r'^[a-zA-Z0-9\-_/]+\.md$')
    
    @validator('name')
    def name_no_special_chars(cls, v):
        """Prevent XSS via agent names"""
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Special characters not allowed in name')
        return v
    
    @validator('persona_file')
    def persona_file_path_traversal_check(cls, v):
        """Prevent directory traversal attacks"""
        if '..' in v or v.startswith('/'):
            raise ValueError('Invalid file path')
        return v

class CreateTaskRequest(BaseModel):
    """SEC-005: Input validation for task creation"""
    task_type: Literal["generate_post", "generate_image", "analyze_trends"]
    input_data: dict = Field(..., max_length=10000)  # Prevent DoS
    priority: int = Field(default=5, ge=1, le=10)
    
    @validator('input_data')
    def validate_input_data_size(cls, v):
        """Prevent memory exhaustion attacks"""
        import json
        json_str = json.dumps(v)
        if len(json_str) > 10000:
            raise ValueError('Input data too large')
        return v
```

**Acceptance Criteria:**
- [ ] All API inputs validated with Pydantic models
- [ ] String inputs have max length limits
- [ ] File paths validated (no directory traversal)
- [ ] Special characters escaped/rejected
- [ ] Numeric inputs have range limits
- [ ] JSON payloads size-limited (prevent DoS)
- [ ] Invalid inputs return 422 (not 500)
- [ ] Validation errors logged (without sensitive data)

**Test Cases:**
```python
def test_xss_prevention_in_agent_name():
    """SEC-005-TC1: XSS chars rejected"""
    malicious_name = "<script>alert('xss')</script>"
    response = client.post("/api/v1/agents", json={
        "name": malicious_name,
        "persona_file": "test.md"
    })
    assert response.status_code == 422
    assert "Special characters not allowed" in response.json()["detail"]

def test_path_traversal_prevention():
    """SEC-005-TC2: Directory traversal blocked"""
    response = client.post("/api/v1/agents", json={
        "name": "TestAgent",
        "persona_file": "../../etc/passwd"
    })
    assert response.status_code == 422

def test_json_size_limit_enforced():
    """SEC-005-TC3: Large payloads rejected"""
    huge_payload = {"data": "x" * 100000}
    response = client.post("/api/v1/tasks", json={
        "task_type": "generate_post",
        "input_data": huge_payload
    })
    assert response.status_code == 422
```

---

### 4.2 SQL Injection Prevention

**Requirement:** SEC-006  
**Priority:** P0 (Critical)

**Specification:**
```python
# NEVER use string formatting in SQL queries

# ❌ WRONG: Vulnerable to SQL injection
def get_agent_by_name_UNSAFE(name: str):
    query = f"SELECT * FROM agents WHERE name = '{name}'"
    return db.execute(query)

# ✅ CORRECT: Use ORM or parameterized queries
def get_agent_by_name_SAFE(name: str):
    # Option 1: SQLAlchemy ORM (preferred)
    return db.query(Agent).filter(Agent.name == name).first()
    
    # Option 2: Parameterized query
    query = "SELECT * FROM agents WHERE name = :name"
    return db.execute(query, {"name": name})
```

**Acceptance Criteria:**
- [ ] All database queries use ORM (SQLAlchemy)
- [ ] If raw SQL needed, use parameterized queries
- [ ] No string concatenation in SQL queries
- [ ] Static analysis (Semgrep) detects SQL injection patterns
- [ ] Code review checklist includes SQL injection check
- [ ] All queries logged (sanitized) for audit

**Test Cases:**
```python
def test_sql_injection_prevention():
    """SEC-006-TC1: SQL injection blocked"""
    malicious_input = "'; DROP TABLE agents; --"
    agent = get_agent_by_name(malicious_input)
    # Should safely return None, not execute DROP TABLE
    assert agent is None
    # Verify table still exists
    assert db.query(Agent).count() > 0
```

---

## 5. Rate Limiting & DoS Prevention

### 5.1 API Rate Limiting

**Requirement:** SEC-007  
**Priority:** P1 (High)

**Specification:**
```yaml
rate_limiting:
  global:
    requests_per_minute: 1000
    burst: 100
    
  per_user:
    requests_per_minute: 100
    requests_per_hour: 1000
    burst: 20
    
  per_agent:
    mcp_calls_per_minute: 60
    budget_checks_per_minute: 10
    
  per_ip:
    requests_per_minute: 60
    requests_per_hour: 500
    ban_threshold: 10000 requests/hour
    ban_duration: 1 hour
    
  implementation:
    storage: Redis
    algorithm: Token Bucket
    headers:
      - X-RateLimit-Limit
      - X-RateLimit-Remaining
      - X-RateLimit-Reset
```

**Acceptance Criteria:**
- [ ] Rate limits enforced at API gateway
- [ ] Authenticated users have higher limits than anonymous
- [ ] Rate limit headers returned in all responses
- [ ] 429 status code when limit exceeded
- [ ] Rate limit state stored in Redis (distributed)
- [ ] Burst allowance for legitimate traffic spikes
- [ ] IP bans for extreme abuse (10x normal rate)

**Test Cases:**
```python
def test_rate_limit_enforced():
    """SEC-007-TC1: Rate limit blocks excess requests"""
    # Make 101 requests (limit is 100/min for users)
    for i in range(101):
        response = client.get("/api/v1/agents", headers=auth_headers)
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429

def test_rate_limit_headers_present():
    """SEC-007-TC2: Rate limit headers returned"""
    response = client.get("/api/v1/agents")
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
```

---

### 5.2 Resource Limits (DoS Prevention)

**Requirement:** SEC-008  
**Priority:** P1 (High)

**Specification:**
```yaml
resource_limits:
  request_timeout: 30 seconds
  max_request_size: 10 MB
  max_response_size: 50 MB
  max_concurrent_connections: 1000
  
  worker_limits:
    max_task_execution_time: 300 seconds
    max_memory_per_task: 1 GB
    max_workers_per_agent: 10
    
  database_limits:
    max_query_time: 10 seconds
    max_connections: 100
    connection_timeout: 5 seconds
```

**Acceptance Criteria:**
- [ ] Requests timeout after 30 seconds
- [ ] Large uploads (>10MB) rejected
- [ ] Database queries killed if >10 seconds
- [ ] Worker tasks killed if >5 minutes
- [ ] Connection pool size limited
- [ ] Memory limits enforced (container level)

---

## 6. Secrets Management

### 6.1 API Key Management

**Requirement:** SEC-009  
**Priority:** P0 (Critical)

**Specification:**
```yaml
secrets_management:
  provider: HashiCorp Vault / AWS Secrets Manager
  
  secret_types:
    llm_api_keys:
      - ANTHROPIC_API_KEY
      - GOOGLE_API_KEY
      - OPENAI_API_KEY
    rotation: Manual (90 days)
    access: Orchestrator service only
    
    database_credentials:
      - DATABASE_URL
      - REDIS_PASSWORD
    rotation: Automatic (30 days)
    access: All services
    
    wallet_keys:
      - AGENT_WALLET_PRIVATE_KEY
    rotation: Never (agent-controlled)
    encryption: Agent-specific KEK
    access: Worker service + Agent
    
  access_control:
    principle: Least Privilege
    authentication: Service Account
    authorization: IAM Roles
    audit: All access logged
```

**Acceptance Criteria:**
- [ ] No secrets in code or environment variables
- [ ] All secrets retrieved from Vault/Secrets Manager
- [ ] Secrets injected at runtime (not build time)
- [ ] Failed secret access triggers alert
- [ ] Secret access logged to audit trail
- [ ] Secrets rotated per schedule
- [ ] Old secrets invalidated immediately after rotation

**Test Cases:**
```python
def test_secrets_not_in_code():
    """SEC-009-TC1: No hardcoded secrets"""
    codebase_files = glob.glob("src/**/*.py", recursive=True)
    secret_patterns = [
        r'sk-ant-[a-zA-Z0-9]{48}',  # Anthropic
        r'sk-proj-[a-zA-Z0-9]{48}', # OpenAI
        r'AIza[a-zA-Z0-9]{35}',     # Google
    ]
    for file_path in codebase_files:
        with open(file_path) as f:
            content = f.read()
            for pattern in secret_patterns:
                assert not re.search(pattern, content), \
                    f"Secret found in {file_path}"
```

---

## 7. Wallet Security (Economic Agency)

### 7.1 Non-Custodial Wallet Security

**Requirement:** SEC-010  
**Priority:** P0 (Critical)

**Specification:**
```yaml
wallet_security:
  architecture: Non-custodial (agent controls private keys)
  key_generation: BIP-39 mnemonic (24 words)
  key_storage:
    encryption: AES-256-GCM
    kek_derivation: PBKDF2 (agent_id + salt, 100k iterations)
    backup: Encrypted, stored in Vault
  
  transaction_signing:
    method: Multi-Party Computation (MPC)
    threshold: 2-of-3 (Agent + CFO Judge + Backup Key)
    timeout: 5 minutes
    
  budget_enforcement:
    daily_limit: $50 (configurable per agent)
    per_transaction_limit: $10
    approval_required: > $10 (human HITL)
    
  monitoring:
    anomaly_detection: ML-based (Chainalysis)
    suspicious_activity: Auto-freeze wallet
    large_transactions: Alert human operator
```

**Acceptance Criteria:**
- [ ] Private keys never stored in plaintext
- [ ] Keys encrypted with agent-specific KEK
- [ ] Agent can sign transactions independently
- [ ] CFO Judge validates all transactions
- [ ] Transactions >$10 require human approval
- [ ] Wallet freeze capability (emergency)
- [ ] All transactions logged on-chain + off-chain
- [ ] Failed transactions don't leak private keys

**Test Cases:**
```python
def test_wallet_keys_encrypted():
    """SEC-010-TC1: Private keys encrypted"""
    agent = create_agent("test-agent")
    wallet = create_wallet(agent.agent_id)
    
    # Private key should be encrypted in database
    db_record = db.query(WalletKey).filter_by(
        agent_id=agent.agent_id
    ).first()
    
    # Should NOT be readable without decryption
    assert db_record.private_key_encrypted.startswith("encrypted:")
    with pytest.raises(ValueError):
        # Attempting to use encrypted key should fail
        sign_transaction(db_record.private_key_encrypted)

def test_budget_limit_enforced():
    """SEC-010-TC2: Budget limits prevent overspend"""
    agent = create_agent_with_wallet("test-agent", daily_limit=50)
    
    # Try to send $60 (exceeds daily limit)
    with pytest.raises(BudgetExceededError):
        send_transaction(agent.agent_id, amount=60, to_address="0x...")
```

---

## 8. Audit Logging & Monitoring

### 8.1 Comprehensive Audit Trail

**Requirement:** SEC-011  
**Priority:** P0 (Critical)

**Specification:**
```yaml
audit_logging:
  events_logged:
    authentication:
      - login_success
      - login_failure
      - logout
      - mfa_enabled
      - password_reset
      
    authorization:
      - permission_granted
      - permission_denied
      - role_changed
      
    data_access:
      - agent_created
      - agent_deleted
      - agent_modified
      - task_created
      - hitl_decision_made
      
    financial:
      - transaction_initiated
      - transaction_completed
      - transaction_failed
      - budget_exceeded
      
    security:
      - api_key_rotated
      - wallet_frozen
      - anomaly_detected
      - rate_limit_exceeded
  
  log_format:
    timestamp: ISO 8601 UTC
    event_type: string
    actor: user_id / agent_id
    resource: affected entity
    action: what was done
    outcome: success / failure
    ip_address: source IP
    trace_id: distributed tracing ID
    metadata: JSON (context)
  
  storage:
    retention: 90 days (hot), 2 years (cold)
    immutability: Write-once (WORM)
    encryption: AES-256
    access: Admin only
```

**Acceptance Criteria:**
- [ ] All security events logged (authentication, authorization)
- [ ] All financial transactions logged
- [ ] All HITL decisions logged
- [ ] Logs immutable (tamper-evident)
- [ ] Logs retained per compliance requirements
- [ ] Log access restricted (admin only)
- [ ] Failed log writes trigger alerts
- [ ] Logs searchable (Elasticsearch)

**Test Cases:**
```python
def test_failed_login_logged():
    """SEC-011-TC1: Failed auth attempts logged"""
    # Attempt login with wrong password
    response = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "wrong_password"
    })
    
    # Check audit log
    log_entry = db.query(AuditLog).filter_by(
        event_type="login_failure",
        actor="user@example.com"
    ).order_by(AuditLog.timestamp.desc()).first()
    
    assert log_entry is not None
    assert log_entry.ip_address is not None

def test_logs_immutable():
    """SEC-011-TC2: Audit logs cannot be modified"""
    log = create_audit_log("test_event")
    original_timestamp = log.timestamp
    
    # Attempt to modify
    with pytest.raises(IntegrityError):
        log.timestamp = datetime.now()
        db.commit()
```

---

## 9. Security Testing & Validation

### 9.1 Automated Security Testing

**Requirement:** SEC-012  
**Priority:** P1 (High)

**Specification:**
```yaml
security_testing:
  static_analysis:
    tool: Semgrep
    rules:
      - detect_sql_injection
      - detect_xss
      - detect_hardcoded_secrets
      - detect_insecure_crypto
    frequency: Every commit
    
  dependency_scanning:
    tool: Snyk / Dependabot
    scope: Python + JavaScript dependencies
    severity_threshold: Medium
    auto_fix: Patch versions only
    frequency: Daily
    
  container_scanning:
    tool: Trivy / Aqua Security
    scope: Docker images
    checks:
      - Known CVEs
      - Malware
      - Misconfigurations
    frequency: Every build
    
  penetration_testing:
    tool: OWASP ZAP / Burp Suite
    scope: API endpoints
    frequency: Before each release
    
  compliance_checks:
    frameworks:
      - OWASP Top 10
      - CWE Top 25
      - GDPR (data privacy)
    frequency: Quarterly
```

**Acceptance Criteria:**
- [ ] Static analysis runs on every commit
- [ ] Dependency vulnerabilities scanned daily
- [ ] Container images scanned before deployment
- [ ] High severity issues block deployment
- [ ] Penetration test report before production release
- [ ] Compliance audit quarterly
- [ ] All findings tracked in security backlog

---

### 9.2 Security Acceptance Criteria (Per User Story)

**Every user story must satisfy:**

```yaml
security_acceptance_template:
  authentication:
    - [ ] Feature requires valid JWT token (if user-facing)
    - [ ] Agent actions require valid API key (if agent-facing)
    
  authorization:
    - [ ] User can only access own resources
    - [ ] Agent can only modify own data
    - [ ] Admin actions require admin role
    
  input_validation:
    - [ ] All inputs validated with Pydantic
    - [ ] String inputs have max length
    - [ ] Numeric inputs have range limits
    - [ ] File paths validated (no traversal)
    
  data_protection:
    - [ ] Sensitive data encrypted at rest
    - [ ] API communications use TLS 1.3
    - [ ] No secrets in logs or error messages
    
  audit:
    - [ ] Security-relevant actions logged
    - [ ] Logs include actor, resource, action, outcome
    - [ ] Trace ID included for correlation
    
  rate_limiting:
    - [ ] API endpoints rate-limited
    - [ ] Resource limits prevent DoS
```

**Example Applied to US-001 (Agent Creation):**

```markdown
### US-001: Agent Persona Instantiation

**Functional Acceptance Criteria:**
- [ ] Agent persona defined via SOUL.md file
- [ ] Unique agent_id generated
- [ ] Wallet address created
- [ ] Profile stored in PostgreSQL

**SECURITY Acceptance Criteria:**
- [x] SEC-001: Valid JWT required to create agent
- [x] SEC-002: Agent API key generated and stored encrypted
- [x] SEC-003: Wallet private key encrypted with agent-specific KEK
- [x] SEC-005: Agent name validated (no XSS chars, max 100 chars)
- [x] SEC-006: Database insert uses ORM (no SQL injection)
- [x] SEC-009: No secrets in code or logs
- [x] SEC-010: Wallet keys never stored in plaintext
- [x] SEC-011: Agent creation logged to audit_log
```

---

## 10. Compliance & Regulatory

### 10.1 GDPR Compliance (Data Privacy)

**Requirement:** SEC-013  
**Priority:** P0 (Critical - if EU users)

**Specification:**
```yaml
gdpr_compliance:
  data_subject_rights:
    right_to_access:
      endpoint: GET /api/v1/users/{id}/data
      response: All user data in JSON
      
    right_to_rectification:
      endpoint: PATCH /api/v1/users/{id}
      validation: User confirms changes
      
    right_to_erasure:
      endpoint: DELETE /api/v1/users/{id}
      process: Anonymize (not hard delete)
      retention: Audit logs kept (legal basis)
      
    right_to_portability:
      endpoint: GET /api/v1/users/{id}/export
      format: JSON / CSV
      
  consent_management:
    required_for:
      - Data collection
      - Marketing communications
      - Third-party data sharing
    consent_storage: Versioned, auditable
    
  data_retention:
    user_data: Deleted 30 days after account closure
    audit_logs: 2 years (legal requirement)
    financial_records: 7 years (tax law)
```

**Acceptance Criteria:**
- [ ] Users can export all their data (JSON format)
- [ ] Users can request data deletion
- [ ] Data deletion completes within 30 days
- [ ] Audit logs retained despite deletion
- [ ] Consent tracked and versioned
- [ ] Privacy policy link in all user flows
- [ ] Data breach notification process documented

---

## 11. Incident Response

### 11.1 Security Incident Response Plan

**Requirement:** SEC-014  
**Priority:** P1 (High)

**Specification:**
```yaml
incident_response:
  detection:
    - Automated monitoring (anomaly detection)
    - User reports (security@chimera.ai)
    - Third-party disclosures (bug bounty)
    
  classification:
    critical: Data breach, wallet compromise
    high: Authentication bypass, privilege escalation
    medium: DoS, XSS, information disclosure
    low: Missing security headers
    
  response_time:
    critical: 1 hour
    high: 4 hours
    medium: 1 day
    low: 1 week
    
  escalation_path:
    1. On-call engineer
    2. Security lead
    3. CTO
    4. Legal / PR (if breach)
    
  containment:
    - Isolate affected systems
    - Revoke compromised credentials
    - Freeze affected wallets
    - Enable maintenance mode if needed
    
  eradication:
    - Patch vulnerability
    - Remove malicious code
    - Restore from backup if needed
    
  recovery:
    - Gradual service restoration
    - Enhanced monitoring
    - Post-incident review
    
  communication:
    internal: Slack #security-incidents
    external: Status page + email (if user-impacting)
    legal: Notify within 72 hours (GDPR)
```

---

## 12. Security Checklist (Pre-Deployment)

**Before deploying to production:**

### Infrastructure
- [ ] TLS 1.3 enabled on all endpoints
- [ ] Firewalls configured (VPC security groups)
- [ ] DDoS protection enabled (CloudFlare / AWS Shield)
- [ ] Backup system tested and automated
- [ ] Disaster recovery plan documented

### Application
- [ ] All secrets in Vault/Secrets Manager
- [ ] No hardcoded credentials in code
- [ ] Static analysis passing (Semgrep)
- [ ] Dependency scan clean (Snyk)
- [ ] Container scan clean (Trivy)

### Authentication
- [ ] JWT implementation tested
- [ ] MFA enforced for admins
- [ ] Password policy enforced
- [ ] Session timeout configured
- [ ] Account lockout enabled

### Authorization
- [ ] Role-based access control (RBAC) implemented
- [ ] Least privilege principle applied
- [ ] Agent data isolation verified
- [ ] Admin actions audited

### Data Protection
- [ ] Database encryption at rest enabled
- [ ] Backup encryption enabled
- [ ] Wallet keys encrypted
- [ ] PII identified and protected

### Monitoring
- [ ] Audit logging enabled
- [ ] Security alerts configured
- [ ] Log retention policy active
- [ ] Anomaly detection running

### Compliance
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] GDPR compliance verified (if EU)
- [ ] Security documentation complete

---

## 13. Security Metrics & KPIs

**Track quarterly:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mean Time to Detect (MTTD) | <1 hour | Time from incident to detection |
| Mean Time to Respond (MTTR) | <4 hours | Time from detection to containment |
| Vulnerability Remediation Time | <7 days | High severity patches |
| Failed Login Attempts | <1% | Login failures / total logins |
| API Errors (4xx/5xx) | <0.1% | Error rate |
| Security Incidents | 0 critical | Per quarter |
| Penetration Test Findings | 0 critical | Per test cycle |
| Compliance Violations | 0 | Audit results |

---

## Appendix A: Threat Model

### Assets to Protect
1. Agent wallet private keys ($$$)
2. User credentials (PII)
3. API keys (service access)
4. Agent personas (IP)
5. Financial transaction data

### Threat Actors
1. External attackers (opportunistic)
2. Competitors (targeted)
3. Malicious insiders (employees)
4. Compromised agents (AI jailbreak)

### Attack Vectors
1. API exploitation (injection, auth bypass)
2. Social engineering (phishing)
3. Supply chain (compromised dependencies)
4. DDoS (availability)
5. Wallet theft (crypto)

---

## Appendix B: Security Review Checklist

**Use for code reviews:**

```markdown
## Security Code Review Checklist

### Authentication & Authorization
- [ ] Endpoints protected by JWT middleware
- [ ] Agent actions validated with API key
- [ ] User can only access own resources
- [ ] No hardcoded credentials

### Input Validation
- [ ] All inputs validated with Pydantic
- [ ] String inputs have max length
- [ ] File paths validated (no traversal)
- [ ] JSON payloads size-limited

### Data Protection
- [ ] Sensitive data encrypted before storage
- [ ] No secrets in logs or errors
- [ ] TLS used for external API calls

### Database Security
- [ ] ORM used (no raw SQL)
- [ ] If raw SQL, parameterized queries
- [ ] No string concatenation in queries

### Error Handling
- [ ] Generic error messages (no info leak)
- [ ] Errors logged with context
- [ ] Stack traces not exposed to users

### Audit Logging
- [ ] Security events logged
- [ ] Logs include trace_id
- [ ] Actor and resource identified
```

---

**Status:** DRAFT → Ready for Security Review  
**Next Steps:**
1. Security team review
2. Penetration testing
3. Compliance audit
4. Ratify specification
5. Implement controls
6. Validate with tests

---

*"Security is not a feature. It's a foundation."*
