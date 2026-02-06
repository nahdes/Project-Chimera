# Project Chimera - OpenClaw Integration Specification

**Version:** 1.0.0  
**Status:** DRAFT  
**Last Updated:** 2026-02-05  
**Target Phase:** Phase 2 (Post-MVP)

---

## 1. Executive Summary

This specification details how Project Chimera agents will integrate with the OpenClaw decentralized agent network. OpenClaw enables agent-to-agent discovery, communication, and economic collaboration—transforming Chimera from isolated influencers to participants in a broader agent economy.

**Integration Timeline:**

- **Phase 0 (Current):** No OpenClaw - focus on core Chimera functionality
- **Phase 1 (Month 3-4):** Read-only discovery - observe the network
- **Phase 2 (Month 5-6):** Human-approved delegation - hire other agents with oversight
- **Phase 3 (Month 7-9):** Autonomous delegation - Judge auto-approves within constraints
- **Phase 4 (Month 10+):** Service provider - Chimera agents offer capabilities to network

---

## 2. OpenClaw Protocol Overview

### 2.1 Core Concepts

**Decentralized Identity (DID)**

- Each agent has a unique, cryptographically verifiable identifier
- Format: `did:openclaw:{network}:{agent_hash}`
- Example: `did:openclaw:base:0x7a8f...3e2d`
- Portable across platforms - agents own their identity

**Capability Manifest**

- JSON document describing what an agent can do
- Published to distributed registry (IPFS + on-chain pointer)
- Includes: skills, pricing, SLAs, reputation scores

**Reputation System**

- On-chain record of successful/failed interactions
- Domain-specific (content creation ≠ financial advice)
- Weighted by transaction value and recency

---

### 2.2 Protocol Layers

```
┌─────────────────────────────────────────────────────────┐
│                REPUTATION LAYER                          │
│  [On-chain Reviews] [Trust Scores] [Dispute Resolution] │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│                TRANSACTION LAYER                         │
│  [Payment Rails] [Escrow] [Completion Verification]     │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│               COMMUNICATION LAYER                        │
│  [Message Protocol] [Authentication] [Encryption]       │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│                DISCOVERY LAYER                           │
│  [Agent Registry] [Capability Search] [Availability]    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Integration Architecture

### 3.1 MCP Server: mcp-server-openclaw

**Purpose:** Wrap OpenClaw protocol interactions in standard MCP interface

**Location:** External service (separate from core Chimera services)

**Communication:** HTTP/WebSocket + blockchain RPC

---

### 3.2 MCP Resources (Read-Only Data)

#### Resource: openclaw://agents/search

**Description:** Discover agents by capability

**Parameters:**

```json
{
  "capability": "string (e.g., 'content_creation', 'trend_analysis')",
  "min_reputation": "float (0.0-1.0)",
  "max_price_per_hour": "float (USD)",
  "availability": "enum (now|within_1h|within_24h)",
  "network": "enum (base|ethereum|solana)"
}
```

**Response:**

```json
{
  "agents": [
    {
      "did": "string",
      "name": "string",
      "capabilities": ["cap1", "cap2"],
      "reputation": {
        "overall_score": "float (0.0-5.0)",
        "total_interactions": "integer",
        "success_rate": "float (0.0-1.0)",
        "specialties": [
          {
            "domain": "string",
            "score": "float"
          }
        ]
      },
      "pricing": {
        "base_rate_usd": "float",
        "model": "enum (per_hour|per_task|per_output)"
      },
      "availability": {
        "status": "enum (available|busy|offline)",
        "next_available": "timestamp (optional)"
      },
      "wallet_address": "string"
    }
  ],
  "total_results": "integer",
  "page": "integer"
}
```

---

#### Resource: openclaw://agent/{did}/profile

**Description:** Get detailed agent information

**Response:**

```json
{
  "did": "string",
  "profile": {
    "name": "string",
    "bio": "string",
    "specialties": ["specialty1", "specialty2"],
    "languages": ["en", "am"], // ISO language codes
    "created_at": "timestamp",
    "last_active": "timestamp"
  },
  "capabilities": [
    {
      "skill_name": "string",
      "description": "string",
      "input_schema": "JSON Schema",
      "output_schema": "JSON Schema",
      "pricing": {
        "amount": "float",
        "currency": "USD",
        "model": "per_task"
      },
      "sla": {
        "typical_response_time_minutes": "integer",
        "success_rate": "float"
      }
    }
  ],
  "reputation": {
    "overall_score": "float",
    "reviews": [
      {
        "from_agent": "string (DID)",
        "rating": "integer (1-5)",
        "comment": "string",
        "transaction_hash": "string",
        "timestamp": "timestamp"
      }
    ]
  },
  "verification": {
    "identity_verified": "boolean",
    "kyc_completed": "boolean",
    "stake_locked": "float (USD)"
  }
}
```

---

#### Resource: openclaw://agent/{did}/reputation

**Description:** Get reputation history

**Response:**

```json
{
  "agent_did": "string",
  "reputation_data": {
    "overall_score": "float (0.0-5.0)",
    "total_interactions": "integer",
    "successful_interactions": "integer",
    "failed_interactions": "integer",
    "disputed_interactions": "integer",
    "specialties": [
      {
        "domain": "string (e.g., 'content_creation')",
        "score": "float",
        "sample_size": "integer"
      }
    ],
    "recent_reviews": [
      {
        "rating": "integer (1-5)",
        "from_agent": "string",
        "comment": "string",
        "timestamp": "timestamp",
        "verified": "boolean"
      }
    ],
    "trust_signals": {
      "stake_locked_usd": "float",
      "identity_verified": "boolean",
      "uptime_percentage": "float",
      "response_time_avg_minutes": "float"
    }
  }
}
```

---

#### Resource: openclaw://network/trending

**Description:** See popular collaborations and patterns

**Response:**

```json
{
  "trending_collaborations": [
    {
      "skill_combination": ["skill1", "skill2"],
      "usage_count_last_7_days": "integer",
      "avg_success_rate": "float",
      "avg_cost_usd": "float"
    }
  ],
  "top_agents": [
    {
      "did": "string",
      "specialty": "string",
      "interactions_last_30_days": "integer",
      "avg_rating": "float"
    }
  ]
}
```

---

### 3.3 MCP Tools (Actions)

#### Tool: request_service

**Description:** Hire another agent to perform a task

**Function Signature:**

```typescript
async function request_service(params: {
  agent_did: string;
  task_specification: {
    skill_name: string;
    input_data: Record<string, any>;
    expected_output_schema: JSONSchema;
    deadline?: string; // ISO timestamp
  };
  payment: {
    max_price_usd: number;
    escrow_duration_hours: number;
  };
  requester_did: string; // Chimera agent's DID
}): Promise<{
  request_id: string;
  status: "pending" | "accepted" | "rejected";
  estimated_completion: string;
  escrow_tx_hash?: string;
}>;
```

**Flow:**

1. Chimera agent creates request via MCP Tool
2. Request routed through CFO Judge for budget approval
3. If approved, funds moved to escrow smart contract
4. Target agent receives request, accepts/rejects
5. On acceptance, work begins
6. On completion, escrow releases payment

---

#### Tool: publish_capability

**Description:** Advertise a Chimera agent's services to the network

**Function Signature:**

```typescript
async function publish_capability(params: {
  agent_did: string;
  capability: {
    skill_name: string;
    description: string;
    input_schema: JSONSchema;
    output_schema: JSONSchema;
    examples: Array<{ input: any; output: any }>;
  };
  pricing: {
    amount: number;
    currency: "USD";
    model: "per_task" | "per_hour";
  };
  sla: {
    typical_response_time_minutes: number;
    uptime_commitment_percentage: number;
  };
}): Promise<{
  capability_id: string;
  published_at: string;
  registry_url: string;
}>;
```

**Example Capabilities Chimera Could Offer:**

- `generate_influencer_content`: Create social media posts with consistent character
- `trend_analysis`: Analyze trending topics and provide content recommendations
- `audience_insights`: Provide engagement analytics from managed accounts
- `character_image_generation`: Generate images with maintained character consistency

---

#### Tool: rate_interaction

**Description:** Update reputation after collaboration

**Function Signature:**

```typescript
async function rate_interaction(params: {
  interaction_id: string;
  other_agent_did: string;
  rating: number; // 1-5 stars
  review_text: string;
  categories: {
    communication: number; // 1-5
    quality: number; // 1-5
    timeliness: number; // 1-5
    professionalism: number; // 1-5
  };
  would_work_again: boolean;
}): Promise<{
  review_id: string;
  on_chain_tx_hash: string;
  reputation_updated: boolean;
}>;
```

---

#### Tool: establish_connection

**Description:** Form persistent collaboration relationship

**Function Signature:**

```typescript
async function establish_connection(params: {
  agent_did: string;
  connection_type: "preferred_vendor" | "regular_partner" | "watchlist";
  notes: string;
}): Promise<{
  connection_id: string;
  created_at: string;
}>;
```

---

#### Tool: dispute_resolution

**Description:** Escalate failed interaction

**Function Signature:**

```typescript
async function dispute_resolution(params: {
  interaction_id: string;
  dispute_reason: string;
  evidence: Array<{
    type: "message" | "file" | "transaction";
    url: string;
  }>;
  requested_resolution: "refund" | "partial_payment" | "reputation_adjustment";
}): Promise<{
  dispute_id: string;
  status: "pending" | "under_review";
  arbitrator_assigned: boolean;
}>;
```

---

## 4. Phased Rollout Plan

### Phase 1: Read-Only Discovery (Month 3-4)

**Objective:** Observe and learn from the network without taking actions

**Capabilities Enabled:**

- ✅ Search for agents by capability
- ✅ View agent profiles and reputation
- ✅ Monitor trending collaborations
- ❌ No delegation (cannot hire other agents)
- ❌ No publishing (cannot offer services)

**Implementation Tasks:**

1. Deploy mcp-server-openclaw in read-only mode
2. Integrate discovery data into Perception system
3. Create analytics dashboard for network insights
4. Monitor for potential collaborators

**Success Criteria:**

- Successfully discover 100+ agents in network
- Identify 10+ agents with relevant capabilities
- Zero errors in protocol communication

---

### Phase 2: Human-Approved Delegation (Month 5-6)

**Objective:** Hire other agents with human oversight

**Capabilities Enabled:**

- ✅ Request services from other agents
- ✅ Escrow-based payments
- ✅ Rate completed interactions
- ⚠️ All requests require HITL approval
- ❌ Still no autonomous service provision

**Implementation Tasks:**

1. Enable `request_service` tool with HITL gate
2. Build escrow management into wallet system
3. Create approval interface for human operators
4. Implement post-interaction rating workflow

**Approval Workflow:**

```
Planner identifies need → generates service request
                       ↓
              CFO Judge reviews budget
                       ↓
              Push to HITL Queue
                       ↓
         Human reviews: agent reputation,
         price, task specification
                       ↓
    [Approve] → Execute escrow → Request sent
        |
    [Reject] → Cancel, re-plan
```

**Success Criteria:**

- Complete 10+ successful agent collaborations
- <5% dispute rate
- Positive ROI (value received > cost paid)
- Human approval time <10 minutes average

---

### Phase 3: Autonomous Delegation (Month 7-9)

**Objective:** Judge can auto-approve agent hiring within constraints

**Capabilities Enabled:**

- ✅ Autonomous service requests for trusted agents
- ✅ Auto-approval up to budget limit ($50/task)
- ✅ Blacklist/whitelist management
- ⚠️ High-risk requests still escalate to HITL

**Auto-Approval Criteria:**

```python
def should_auto_approve(request: ServiceRequest) -> bool:
    # 1. Agent is on whitelist OR has high reputation
    if not (request.agent_did in WHITELIST or
            request.agent_reputation > 4.5):
        return False

    # 2. Cost within limits
    if request.cost_usd > DAILY_DELEGATION_BUDGET:
        return False

    # 3. Task type is approved for delegation
    if request.task_type not in DELEGATABLE_TASKS:
        return False

    # 4. Recent success rate with this agent is high
    if get_success_rate(request.agent_did) < 0.9:
        return False

    return True
```

**Success Criteria:**

- 50+ autonomous delegations
- <2% HITL escalation rate
- Maintained or improved success rate vs Phase 2

---

### Phase 4: Service Provider (Month 10+)

**Objective:** Chimera agents offer capabilities to the network

**Capabilities Enabled:**

- ✅ Publish capability manifests
- ✅ Receive and fulfill service requests
- ✅ Earn revenue from other agents
- ✅ Build reputation as service provider

**Services Chimera Could Offer:**

**1. Influencer Content Generation**

```json
{
  "skill_name": "generate_influencer_content",
  "description": "Create social media posts (text + image) with consistent character persona",
  "pricing": {
    "amount": 5.0,
    "currency": "USD",
    "model": "per_task"
  },
  "sla": {
    "typical_response_time_minutes": 15,
    "uptime_commitment_percentage": 99.0
  }
}
```

**2. Trend Analysis & Content Recommendations**

```json
{
  "skill_name": "trend_analysis_content_strategy",
  "description": "Analyze trending topics in a domain and provide content strategy recommendations",
  "pricing": {
    "amount": 10.0,
    "currency": "USD",
    "model": "per_task"
  },
  "sla": {
    "typical_response_time_minutes": 30
  }
}
```

**3. Character-Consistent Image Generation**

```json
{
  "skill_name": "character_consistent_image",
  "description": "Generate images featuring established character with maintained visual consistency",
  "pricing": {
    "amount": 3.0,
    "currency": "USD",
    "model": "per_task"
  }
}
```

**Request Handling Flow:**

```
External agent sends request to Chimera agent DID
                    ↓
         mcp-server-openclaw receives request
                    ↓
         Validate: budget check, capability match
                    ↓
         Create Task in Chimera's TaskQueue
                    ↓
         Worker executes (same as internal tasks)
                    ↓
         Judge validates output
                    ↓
         Return result + invoice to requester
                    ↓
         Escrow releases payment to Chimera wallet
```

**Success Criteria:**

- 20+ service requests from external agents
- 4.5+ average rating
- Positive P&L (revenue > operational costs)

---

## 5. Data Models

### 5.1 OpenClaw Interaction Record

```sql
CREATE TABLE openclaw_interactions (
    interaction_id UUID PRIMARY KEY,
    chimera_agent_id UUID NOT NULL REFERENCES agents(agent_id),
    other_agent_did VARCHAR(255) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL, -- 'service_request', 'service_provided'
    request_data JSONB,
    response_data JSONB,
    status VARCHAR(50) NOT NULL,
    cost_usd DECIMAL(10, 2),
    escrow_tx_hash VARCHAR(255),
    payment_tx_hash VARCHAR(255),
    rating_given INTEGER,
    rating_received INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_openclaw_agent ON openclaw_interactions(chimera_agent_id);
CREATE INDEX idx_openclaw_other ON openclaw_interactions(other_agent_did);
CREATE INDEX idx_openclaw_type ON openclaw_interactions(interaction_type);
```

---

### 5.2 Agent Whitelist/Blacklist

```sql
CREATE TABLE agent_trust_list (
    list_id UUID PRIMARY KEY,
    agent_did VARCHAR(255) NOT NULL UNIQUE,
    list_type VARCHAR(20) NOT NULL, -- 'whitelist', 'blacklist', 'watchlist'
    reason TEXT,
    added_by VARCHAR(50), -- 'judge' or 'human'
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_trust_list_type ON agent_trust_list(list_type);
CREATE INDEX idx_trust_list_did ON agent_trust_list(agent_did);
```

---

## 6. Security Considerations

### 6.1 Agent Verification

**Problem:** How do we trust unknown agents?

**Mitigations:**

- Start with high-reputation agents only (>4.5 stars, 20+ interactions)
- Gradually expand to lower thresholds as confidence grows
- Implement stake requirements (agents must lock funds as collateral)
- Use escrow for all payments (no direct transfers)

---

### 6.2 Malicious Behavior Detection

**Potential Attacks:**

- Sybil attacks (fake agents boost each other's reputation)
- Rug pulls (accept payment, deliver nothing)
- Data poisoning (provide false information)

**Defenses:**

- Check on-chain transaction history (real stake, real interactions)
- Cross-reference ratings from multiple sources
- Implement "test tasks" with known correct answers
- Maintain blacklist of problematic agents

---

### 6.3 Privacy

**Data Sharing with External Agents:**

- Never share SOUL.md or internal persona details
- Task specifications should be minimal (input/output only)
- Don't expose Chimera's internal architecture
- Use secure channels (encrypted communication)

---

## 7. Economic Model

### 7.1 Budget Allocation

```python
# Monthly budget per agent
TOTAL_MONTHLY_BUDGET_USD = 50.00

# Allocation
CORE_OPERATIONS = 0.70  # 70% - LLM inference, image/video gen
OPENCLAW_DELEGATION = 0.20  # 20% - hiring other agents
SERVICE_PROVISION = 0.10  # 10% - infrastructure for serving others
```

---

### 7.2 ROI Calculation

**For Service Consumer (Chimera hiring others):**

```
ROI = (Value_Gained - Cost_Paid) / Cost_Paid

Example:
- Hire trend analysis agent for $10
- Analysis leads to viral content
- Viral content generates $100 in sponsorship revenue
- ROI = ($100 - $10) / $10 = 900% = 9x return
```

**For Service Provider (Chimera being hired):**

```
Revenue per task = $5 (content generation)
Cost per task = $2 (LLM inference + image gen)
Profit margin = ($5 - $2) / $5 = 60%

If 100 tasks/month:
Monthly profit = 100 * $3 = $300
```

---

## 8. Testing Strategy

### 8.1 Phase 1 (Read-Only) Tests

```python
async def test_agent_discovery():
    """Test searching for agents by capability"""
    results = await openclaw.search_agents(
        capability="content_creation",
        min_reputation=4.0
    )
    assert len(results.agents) > 0
    assert all(a.reputation.overall_score >= 4.0 for a in results.agents)

async def test_profile_retrieval():
    """Test fetching detailed agent profile"""
    profile = await openclaw.get_agent_profile(
        did="did:openclaw:base:0xtest123"
    )
    assert profile.capabilities is not None
    assert profile.reputation is not None
```

---

### 8.2 Phase 2 (Delegation) Tests

```python
async def test_service_request_flow():
    """Test full service request with escrow"""
    # 1. Request service
    request = await openclaw.request_service(
        agent_did="did:openclaw:base:0xtest123",
        task={"skill": "trend_analysis", "topic": "AI"},
        max_price=10.00
    )
    assert request.status == "pending"

    # 2. Check escrow created
    assert request.escrow_tx_hash is not None

    # 3. Wait for completion (mock)
    await wait_for_completion(request.request_id)

    # 4. Verify payment released
    payment = await check_payment_status(request.request_id)
    assert payment.status == "completed"
```

---

### 8.3 Phase 4 (Service Provider) Tests

```python
async def test_receive_external_request():
    """Test handling service request from external agent"""
    # 1. External agent sends request
    request = mock_external_request(
        to_agent="did:openclaw:base:0xchimera001",
        skill="generate_influencer_content",
        input_data={"topic": "Ethiopian coffee culture"}
    )

    # 2. Chimera receives and validates
    task = await openclaw.handle_incoming_request(request)
    assert task.task_type == "generate_post"

    # 3. Worker executes
    result = await worker.execute_task(task)

    # 4. Judge validates
    decision = await judge.validate_result(result)
    assert decision == Decision.APPROVE

    # 5. Response sent to requester
    response = await openclaw.send_response(request.request_id, result)
    assert response.status == "delivered"
```

---

## 9. Metrics & KPIs

### 9.1 Phase 1 (Discovery) Metrics

- Unique agents discovered
- Network coverage by domain
- Data freshness (last_updated timestamps)

### 9.2 Phase 2-3 (Delegation) Metrics

- Service requests sent
- Success rate (completed / total)
- Average cost per delegation
- ROI (value gained / cost paid)
- Time to completion (request → delivery)

### 9.3 Phase 4 (Service Provider) Metrics

- Service requests received
- Fulfillment rate
- Average rating received
- Revenue generated
- Profit margin
- Repeat customer rate

---

## 10. Rollback Plan

**If OpenClaw integration fails or underperforms:**

1. **Immediate:** Disable mcp-server-openclaw (feature flag)
2. **Short-term:** Revert to isolated agent operations
3. **Analysis:** Determine root cause (technical, economic, or market fit)
4. **Decision:** Fix and retry, or defer integration to later phase

**No Disruption to Core Functionality:** OpenClaw is an enhancement, not a dependency. Chimera must function perfectly without it.

---

## 11. Future Enhancements

### 11.1 Agent Organizations

- Multiple Chimera agents could form a "virtual agency"
- Collective reputation and shared resources
- Coordinated campaigns leveraging network

### 11.2 Specialized Marketplaces

- Niche markets (e.g., "Ethiopian content specialists")
- Industry-specific collaborations (fashion, tech, finance)

### 11.3 Cross-Chain Interoperability

- Support multiple blockchains (Ethereum, Solana, Base)
- Bridge assets between chains for payments

---

**Approval Checklist:**

- [ ] Technical feasibility validated
- [ ] Security review completed
- [ ] Economic model stress-tested
- [ ] Phased rollout plan approved
- [ ] Rollback procedures documented

---

_"In a network of intelligent agents, trust is the currency and reputation is the ledger."_
