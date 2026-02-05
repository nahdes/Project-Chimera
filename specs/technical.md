# Project Chimera - Technical Specification

**Version:** 1.0.0  
**Status:** DRAFT  
**Last Updated:** 2026-02-05

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Campaign   │  │  GlobalState │  │   Dashboard  │      │
│  │   Manager    │  │   Manager    │  │      UI      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      SWARM LAYER                             │
│  ┌───────────┐    ┌───────────┐    ┌────────────┐          │
│  │  Planner  │───▶│  Workers  │───▶│   Judges   │          │
│  │  Service  │    │   Pool    │    │  Service   │          │
│  └───────────┘    └───────────┘    └────────────┘          │
│       │                │                   │                 │
│       ▼                ▼                   ▼                 │
│  [TaskQueue]     [MCP Tools]        [ReviewQueue]           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER (MCP)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ mcp-twitter  │ │mcp-ideogram  │ │mcp-weaviate  │ ...    │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  [Redis Cache] [PostgreSQL] [Weaviate] [Blockchain]         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. API Contracts

### 2.1 Core Data Models

#### Agent Profile

```json
{
  "agent_id": "string (UUID)",
  "name": "string",
  "bio": "string (max 500 chars)",
  "persona": {
    "soul_md_path": "string (file path)",
    "voice_tone": ["adjective1", "adjective2"],
    "core_values": ["value1", "value2"],
    "directives": ["directive1", "directive2"]
  },
  "social_handles": {
    "twitter": "string (optional)",
    "instagram": "string (optional)",
    "tiktok": "string (optional)"
  },
  "wallet_address": "string (Ethereum/Base address)",
  "character_reference_id": "string (LoRA identifier)",
  "created_at": "timestamp (ISO 8601)",
  "updated_at": "timestamp (ISO 8601)",
  "status": "enum (active|paused|archived)"
}
```

---

#### Task Object

```json
{
  "task_id": "string (UUID)",
  "agent_id": "string (UUID)",
  "campaign_id": "string (UUID, optional)",
  "type": "enum (generate_post|generate_image|generate_video|post_content|reply_comment|execute_transaction|analyze_trend)",
  "priority": "integer (1-10, 10=highest)",
  "status": "enum (pending|in_progress|completed|failed|escalated)",
  "input_data": {
    // Type-specific fields (see Task Input Schemas below)
  },
  "dependencies": ["task_id1", "task_id2"],
  "assigned_worker_id": "string (UUID, optional)",
  "created_at": "timestamp",
  "started_at": "timestamp (optional)",
  "completed_at": "timestamp (optional)",
  "retry_count": "integer (default: 0)",
  "max_retries": "integer (default: 3)",
  "timeout_seconds": "integer (default: 300)",
  "trace_id": "string (for distributed tracing)"
}
```

---

#### Result Object

```json
{
  "result_id": "string (UUID)",
  "task_id": "string (UUID)",
  "worker_id": "string (UUID)",
  "status": "enum (success|failure|needs_review)",
  "output_data": {
    // Type-specific output (see Task Output Schemas below)
  },
  "metadata": {
    "execution_time_ms": "integer",
    "cost_usd": "float",
    "confidence_score": "float (0.0-1.0)",
    "model_used": "string (e.g., 'gemini-3-pro')",
    "tokens_consumed": "integer (optional)"
  },
  "error_details": {
    "error_type": "string (optional)",
    "error_message": "string (optional)",
    "stack_trace": "string (optional)"
  },
  "created_at": "timestamp",
  "trace_id": "string"
}
```

---

### 2.2 Task Input/Output Schemas

#### Task Type: generate_post

**Input:**

```json
{
  "topic": "string (main subject)",
  "platform": "enum (twitter|instagram|tiktok)",
  "tone": "string (optional, e.g., 'humorous', 'educational')",
  "max_length": "integer (platform-specific default)",
  "context": {
    "trend_alert": "object (optional)",
    "related_posts": ["post_id1", "post_id2"]
  }
}
```

**Output:**

```json
{
  "text_content": "string",
  "hashtags": ["#tag1", "#tag2"],
  "estimated_engagement_score": "float (0.0-1.0)",
  "safety_check": {
    "passed": "boolean",
    "flags": ["flag1", "flag2"]
  }
}
```

---

#### Task Type: generate_image

**Input:**

```json
{
  "prompt": "string",
  "character_reference_id": "string (auto-populated from agent profile)",
  "style": "enum (portrait|landscape|square|story)",
  "aspect_ratio": "string (e.g., '16:9', '1:1')",
  "quality": "enum (standard|high)"
}
```

**Output:**

```json
{
  "image_url": "string (cloud storage URL)",
  "image_metadata": {
    "width": "integer",
    "height": "integer",
    "file_size_bytes": "integer",
    "format": "string (e.g., 'png', 'jpg')"
  },
  "generation_model": "string (e.g., 'ideogram-v2')",
  "cost_usd": "float"
}
```

---

#### Task Type: generate_video

**Input:**

```json
{
  "video_type": "enum (living_portrait|text_to_video)",
  "input": {
    // For living_portrait:
    "static_image_url": "string",
    "motion_instructions": "string",
    // For text_to_video:
    "text_prompt": "string"
  },
  "duration_seconds": "integer (5-60)",
  "quality": "enum (720p|1080p|4k)"
}
```

**Output:**

```json
{
  "video_url": "string",
  "video_metadata": {
    "duration_seconds": "integer",
    "resolution": "string",
    "file_size_bytes": "integer",
    "format": "string (e.g., 'mp4')"
  },
  "generation_model": "string",
  "cost_usd": "float",
  "generation_time_seconds": "integer"
}
```

---

#### Task Type: post_content

**Input:**

```json
{
  "platform": "enum (twitter|instagram|tiktok)",
  "content": {
    "text": "string (optional)",
    "media_urls": ["url1", "url2"],
    "media_types": ["image", "video"]
  },
  "scheduling": {
    "post_now": "boolean (default: true)",
    "scheduled_time": "timestamp (optional)"
  }
}
```

**Output:**

```json
{
  "post_id": "string (platform-specific ID)",
  "post_url": "string (public URL)",
  "posted_at": "timestamp",
  "initial_metrics": {
    "views": "integer (optional)",
    "likes": "integer (optional)",
    "comments": "integer (optional)"
  }
}
```

---

#### Task Type: execute_transaction

**Input:**

```json
{
  "transaction_type": "enum (transfer|token_deploy|swap)",
  "from_wallet": "string (agent wallet address)",
  "to_address": "string",
  "amount": "string (in wei or smallest unit)",
  "token_type": "enum (ETH|BASE|USDC|custom)",
  "reason": "string (for audit trail)",
  "max_gas_price_gwei": "integer (optional)"
}
```

**Output:**

```json
{
  "transaction_hash": "string",
  "status": "enum (pending|confirmed|failed)",
  "block_number": "integer (optional)",
  "gas_used": "integer",
  "gas_cost_usd": "float",
  "confirmed_at": "timestamp (optional)"
}
```

---

### 2.3 MCP Tool Definitions

#### Tool: generate_image (mcp-server-ideogram)

**Function Signature:**

```typescript
async function generate_image(params: {
  prompt: string;
  character_reference_id?: string;
  style?: "realistic" | "anime" | "artistic";
  aspect_ratio?: "1:1" | "16:9" | "9:16";
}): Promise<{
  image_url: string;
  metadata: ImageMetadata;
}>;
```

**Error Handling:**

- `RATE_LIMIT_EXCEEDED`: Retry with exponential backoff
- `INVALID_PROMPT`: Return to Planner for revision
- `NSFW_DETECTED`: Reject and escalate to HITL

---

#### Tool: post_tweet (mcp-server-twitter)

**Function Signature:**

```typescript
async function post_tweet(params: {
  text: string;
  media_ids?: string[];
  reply_to?: string; // tweet_id for replies
}): Promise<{
  tweet_id: string;
  tweet_url: string;
  posted_at: string;
}>;
```

**Error Handling:**

- `AUTH_FAILED`: Alert operator, pause agent
- `DUPLICATE_CONTENT`: Log and skip
- `RATE_LIMIT`: Queue for later (use Redis)

---

#### Tool: semantic_search (mcp-server-weaviate)

**Function Signature:**

```typescript
async function semantic_search(params: {
  query: string;
  collection: "memories" | "world_knowledge";
  limit?: number; // default: 5
  filters?: Record<string, any>;
}): Promise<{
  results: Array<{
    id: string;
    content: string;
    relevance_score: number;
    metadata: Record<string, any>;
  }>;
}>;
```

---

#### Tool: send_transaction (mcp-server-coinbase)

**Function Signature:**

```typescript
async function send_transaction(params: {
  from_wallet: string;
  to_address: string;
  amount: string;
  token: "ETH" | "BASE" | "USDC";
}): Promise<{
  transaction_hash: string;
  status: "pending" | "confirmed" | "failed";
  gas_cost: string;
}>;
```

---

### 2.4 MCP Resource Definitions

#### Resource: twitter://mentions

**Schema:**

```json
{
  "resource_type": "twitter_mentions",
  "poll_interval_seconds": 120,
  "data_format": {
    "mentions": [
      {
        "mention_id": "string",
        "author": {
          "username": "string",
          "display_name": "string",
          "verified": "boolean",
          "follower_count": "integer"
        },
        "content": "string",
        "created_at": "timestamp",
        "engagement": {
          "likes": "integer",
          "retweets": "integer",
          "replies": "integer"
        }
      }
    ]
  }
}
```

---

#### Resource: news://trending

**Schema:**

```json
{
  "resource_type": "news_trends",
  "poll_interval_seconds": 300,
  "data_format": {
    "trending_topics": [
      {
        "topic": "string",
        "category": "string (e.g., 'technology', 'politics')",
        "relevance_score": "float (0.0-1.0)",
        "sources": [
          {
            "url": "string",
            "title": "string",
            "published_at": "timestamp"
          }
        ],
        "sentiment": "enum (positive|neutral|negative)"
      }
    ]
  }
}
```

---

## 3. Database Schemas

### 3.1 PostgreSQL Schema (Transactional Data)

#### Table: agents

```sql
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    bio TEXT,
    soul_md_path VARCHAR(500) NOT NULL,
    character_reference_id VARCHAR(255),
    wallet_address VARCHAR(255) UNIQUE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_wallet ON agents(wallet_address);
```

---

#### Table: campaigns

```sql
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    agent_ids UUID[] NOT NULL, -- Array of participating agents
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    budget_usd DECIMAL(10, 2),
    spent_usd DECIMAL(10, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active',
    goals JSONB, -- Campaign objectives
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_dates ON campaigns(start_date, end_date);
```

---

#### Table: tasks

```sql
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    task_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    input_data JSONB NOT NULL,
    dependencies UUID[],
    assigned_worker_id UUID,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 300,
    trace_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_details JSONB
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_agent ON tasks(agent_id);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC);
CREATE INDEX idx_tasks_trace ON tasks(trace_id);
```

---

#### Table: results

```sql
CREATE TABLE results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(task_id),
    worker_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    output_data JSONB,
    metadata JSONB,
    error_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trace_id VARCHAR(100)
);

CREATE INDEX idx_results_task ON results(task_id);
CREATE INDEX idx_results_status ON results(status);
```

---

#### Table: transactions

```sql
CREATE TABLE transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id),
    from_wallet VARCHAR(255) NOT NULL,
    to_wallet VARCHAR(255) NOT NULL,
    amount_wei VARCHAR(100) NOT NULL,
    token_type VARCHAR(20) NOT NULL,
    transaction_hash VARCHAR(255) UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',
    gas_cost_wei VARCHAR(100),
    block_number BIGINT,
    reason TEXT,
    approved_by VARCHAR(50), -- 'cfo_judge' or 'human'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP
);

CREATE INDEX idx_transactions_agent ON transactions(agent_id);
CREATE INDEX idx_transactions_hash ON transactions(transaction_hash);
CREATE INDEX idx_transactions_status ON transactions(status);
```

---

#### Table: hitl_queue

```sql
CREATE TABLE hitl_queue (
    hitl_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(task_id),
    result_id UUID REFERENCES results(result_id),
    escalation_reason VARCHAR(100) NOT NULL,
    context_data JSONB NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    assigned_to VARCHAR(100), -- Human operator
    decision VARCHAR(20), -- 'approve', 'reject', 'modify'
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

CREATE INDEX idx_hitl_status ON hitl_queue(status);
CREATE INDEX idx_hitl_priority ON hitl_queue(priority DESC);
```

---

#### Table: audit_log

```sql
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    trace_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_audit_agent ON audit_log(agent_id);
CREATE INDEX idx_audit_type ON audit_log(event_type);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_trace ON audit_log(trace_id);
```

---

### 3.2 Weaviate Schema (Vector Database)

#### Collection: agent_memories

```json
{
  "class": "AgentMemory",
  "description": "Long-term semantic memories for agents",
  "vectorizer": "text2vec-openai",
  "properties": [
    {
      "name": "agent_id",
      "dataType": ["string"],
      "description": "UUID of the agent"
    },
    {
      "name": "content",
      "dataType": ["text"],
      "description": "The memory content"
    },
    {
      "name": "memory_type",
      "dataType": ["string"],
      "description": "Type: 'episodic', 'semantic', 'learned'"
    },
    {
      "name": "context_tags",
      "dataType": ["string[]"],
      "description": "Tags for filtering (e.g., ['social_media', 'campaign_x'])"
    },
    {
      "name": "created_at",
      "dataType": ["date"],
      "description": "When the memory was formed"
    },
    {
      "name": "relevance_score",
      "dataType": ["number"],
      "description": "Importance weight (0.0-1.0)"
    }
  ]
}
```

---

#### Collection: world_knowledge

```json
{
  "class": "WorldKnowledge",
  "description": "General knowledge base for all agents",
  "vectorizer": "text2vec-openai",
  "properties": [
    {
      "name": "topic",
      "dataType": ["string"],
      "description": "Knowledge topic/category"
    },
    {
      "name": "content",
      "dataType": ["text"],
      "description": "The knowledge content"
    },
    {
      "name": "source_url",
      "dataType": ["string"],
      "description": "Original source"
    },
    {
      "name": "last_updated",
      "dataType": ["date"],
      "description": "Freshness indicator"
    },
    {
      "name": "verified",
      "dataType": ["boolean"],
      "description": "Has this been fact-checked?"
    }
  ]
}
```

---

### 3.3 Redis Data Structures

#### TaskQueue (List)

```
Key: taskqueue:{agent_id}
Type: LIST
Operations:
  - LPUSH taskqueue:{agent_id} <task_json>  # Planner pushes
  - BRPOP taskqueue:{agent_id} 60           # Worker pops (blocking)
```

#### ReviewQueue (List)

```
Key: reviewqueue
Type: LIST
Operations:
  - LPUSH reviewqueue <result_json>  # Worker pushes
  - BRPOP reviewqueue 60             # Judge pops
```

#### Episodic Memory (Hash)

```
Key: memory:episodic:{agent_id}
Type: HASH
Fields:
  - last_hour: JSON array of recent interactions
  - conversation_context: Current conversation state
TTL: 3600 seconds (1 hour)
```

#### Rate Limiting (String with TTL)

```
Key: ratelimit:mcp:{server_name}
Type: STRING
Value: request_count
TTL: 3600 seconds
Operations:
  - INCR ratelimit:mcp:{server_name}
  - EXPIRE ratelimit:mcp:{server_name} 3600
  - If count > threshold → sleep/backoff
```

---

### 3.4 Entity Relationship Diagram (ERD)

```
┌──────────────┐
│   agents     │
│--------------│
│ agent_id (PK)│
│ name         │
│ wallet_addr  │
└──────────────┘
      │ 1
      │
      │ N
      ▼
┌──────────────┐       ┌──────────────┐
│   tasks      │───────│   results    │
│--------------│  1:1  │--------------│
│ task_id (PK) │       │ result_id(PK)│
│ agent_id(FK) │       │ task_id (FK) │
│ campaign_id  │       │ worker_id    │
└──────────────┘       └──────────────┘
      │                      │
      │                      │
      ▼                      ▼
┌──────────────┐       ┌──────────────┐
│  campaigns   │       │  hitl_queue  │
│--------------│       │--------------│
│campaign_id(PK)       │ hitl_id (PK) │
│ agent_ids[]  │       │ result_id(FK)│
└──────────────┘       └──────────────┘

┌──────────────┐
│transactions  │
│--------------│
│transaction_id│
│ agent_id (FK)│
│ tx_hash      │
└──────────────┘
```

---

## 4. Service Architecture

### 4.1 Orchestrator Service

**Responsibilities:**

- Manage agent lifecycle (create, pause, delete)
- Maintain GlobalState
- Provide dashboard API

**API Endpoints:**

```
POST   /api/v1/agents              # Create new agent
GET    /api/v1/agents              # List all agents
GET    /api/v1/agents/{id}         # Get agent details
PATCH  /api/v1/agents/{id}         # Update agent
DELETE /api/v1/agents/{id}         # Archive agent

POST   /api/v1/campaigns           # Create campaign
GET    /api/v1/campaigns           # List campaigns
GET    /api/v1/campaigns/{id}      # Get campaign details
```

**Technology Stack:**

- Language: Python 3.12+
- Framework: FastAPI
- Database: PostgreSQL (SQLAlchemy ORM)
- Cache: Redis
- Deployment: Docker + Kubernetes

---

### 4.2 Planner Service

**Responsibilities:**

- Decompose goals into tasks
- Monitor system state
- Re-plan dynamically

**Internal API:**

```python
class PlannerService:
    async def create_plan(
        self,
        campaign: Campaign,
        constraints: PlanConstraints
    ) -> List[Task]:
        """Decompose campaign into tasks"""

    async def monitor_and_replan(self):
        """Continuous monitoring loop"""

    async def handle_worker_failure(
        self,
        failed_task: Task
    ) -> Task:
        """Generate alternative approach"""
```

**Technology Stack:**

- Language: Python
- LLM: Gemini 3 Pro (planning requires reasoning)
- Message Queue: Redis (TaskQueue)

---

### 4.3 Worker Pool

**Responsibilities:**

- Execute tasks in parallel
- Call MCP Tools
- Handle retries

**Scaling:**

- Horizontal: Deploy N worker instances
- Auto-scaling: Based on TaskQueue depth

**Worker Lifecycle:**

```python
async def worker_lifecycle():
    while True:
        task = await pop_from_queue(timeout=60)
        if not task:
            continue

        try:
            result = await execute_task(task)
            await push_to_review_queue(result)
        except Exception as e:
            await handle_error(task, e)
```

---

### 4.4 Judge Service

**Responsibilities:**

- Validate Worker outputs
- Update GlobalState with OCC
- Escalate to HITL

**Validation Pipeline:**

```python
class JudgeService:
    async def validate_result(self, result: Result) -> Decision:
        # 1. Persona consistency check
        persona_check = await self.check_persona(result)

        # 2. Content safety check
        safety_check = await self.check_safety(result)

        # 3. Budget check (if transaction)
        if result.task_type == 'execute_transaction':
            budget_check = await self.cfo_judge(result)

        # 4. Make decision
        if all_checks_pass:
            return Decision.APPROVE
        elif high_risk:
            return Decision.ESCALATE
        else:
            return Decision.REJECT
```

---

## 5. Deployment Architecture

### 5.1 Container Structure

```yaml
# docker-compose.yml
version: "3.8"

services:
  orchestrator:
    build: ./services/orchestrator
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis

  planner:
    build: ./services/planner
    environment:
      - REDIS_URL=${REDIS_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - redis

  worker:
    build: ./services/worker
    deploy:
      replicas: 3 # Start with 3 workers
    environment:
      - REDIS_URL=${REDIS_URL}
      - MCP_SERVERS=${MCP_SERVERS}
    depends_on:
      - redis

  judge:
    build: ./services/judge
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=chimera
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate

volumes:
  postgres_data:
  redis_data:
```

---

### 5.2 Kubernetes Manifests (Production)

```yaml
# orchestrator-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: orchestrator
  template:
    metadata:
      labels:
        app: orchestrator
    spec:
      containers:
        - name: orchestrator
          image: chimera/orchestrator:latest
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: chimera-secrets
                  key: database-url
---
# worker-deployment.yaml (with HPA)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
    spec:
      containers:
        - name: worker
          image: chimera/worker:latest
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: worker
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: External
      external:
        metric:
          name: redis_queue_depth
        target:
          type: Value
          value: "10" # Scale up if queue > 10 tasks
```

---

## 6. Security Considerations

### 6.1 Secrets Management

- Use HashiCorp Vault or AWS Secrets Manager
- Never commit secrets to Git
- Rotate API keys quarterly

### 6.2 Wallet Security

- Private keys stored encrypted (AES-256)
- MPC (Multi-Party Computation) for transaction signing
- Hardware Security Modules (HSM) for production

### 6.3 API Security

- JWT authentication for all endpoints
- Rate limiting per agent (1000 req/hour)
- CORS restrictions for dashboard

---

## 7. Monitoring & Observability

### 7.1 Metrics to Track

- Task throughput (tasks/minute)
- Task latency (p50, p95, p99)
- Worker utilization (%)
- Queue depths (TaskQueue, ReviewQueue)
- Cost per agent (USD/day)
- Error rates by type

### 7.2 Alerting Rules

- Queue depth > 1000 → scale workers
- Error rate > 5% → investigate
- Cost > budget → pause agents
- HITL queue > 50 → notify operator

---

**Next Steps:**

1. Review and ratify technical spec
2. Generate database migration scripts
3. Create OpenAPI spec for REST endpoints
4. Write integration tests for swarm coordination

---

_"Good architecture makes the right thing easy and the wrong thing hard."_
