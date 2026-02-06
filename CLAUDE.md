# Project Chimera - AI Assistant Context

**For: GitHub Copilot, Claude Code, or any AI coding assistant**

---

## PROJECT IDENTITY

**Name:** Project Chimera  
**Type:** Autonomous Influencer Network  
**Status:** Active Development (Task 2-3 Complete, Implementation Pending)

This is a **production-grade distributed system** for managing AI-powered virtual influencers with:
- Hierarchical swarm architecture (Planner-Worker-Judge)
- Model Context Protocol (MCP) for all external integrations
- On-chain economic agency via Coinbase AgentKit
- Full autonomy: perception, reasoning, content creation, and financial transactions

---

## PRIME DIRECTIVE

### ⚠️ NEVER GENERATE CODE WITHOUT CHECKING SPECS FIRST

**Why:** Specifications prevent AI hallucination. Code without specs creates technical debt.

**Process (MANDATORY):**

1. **Read the spec** in `specs/` directory
2. **Quote acceptance criteria** from `specs/functional.md`
3. **Check API contract** in `specs/technical.md`
4. **Verify constraints** in `specs/_meta.md`
5. **THEN** write code that satisfies all criteria

**Example:**
```
Developer: "Implement agent creation"

❌ WRONG APPROACH:
- Jump straight to coding
- Make assumptions about data structure
- Skip validation and error handling

✅ CORRECT APPROACH:
Step 1: Read specs/functional.md → Find US-001 (Agent Persona Instantiation)
Step 2: Read specs/technical.md → Get Agent Profile JSON schema
Step 3: Note acceptance criteria:
   - "Agent persona defined via SOUL.md file"
   - "Unique agent_id generated"
   - "Wallet address created"
Step 4: Write code that satisfies ALL criteria
Step 5: Write tests that validate acceptance criteria
```

---

## TRACEABILITY REQUIREMENT

**Before writing ANY code, you MUST:**

1. **Explain your plan:**
   ```
   I will implement US-001 (Agent Persona Instantiation).
   
   Approach:
   - Create Agent class in src/chimera/core/agent.py
   - Load SOUL.md file and parse with pydantic
   - Generate UUID for agent_id
   - Call Coinbase AgentKit to create wallet
   - Store in PostgreSQL
   
   Acceptance criteria to satisfy:
   - [ ] Persona defined via SOUL.md (will use pydantic parser)
   - [ ] Unique agent_id (will use uuid4())
   - [ ] Wallet created (will call coinbase_agentkit.create_wallet())
   ```

2. **Write the code**

3. **Verify compliance:**
   ```
   ✅ Implemented US-001
   ✅ All acceptance criteria satisfied
   ✅ Tests pass (see tests/unit/test_agent.py)
   ```

---

## CRITICAL ARCHITECTURAL RULES

### Rule 1: No Direct API Calls (Use MCP)

**❌ NEVER:**
```python
import tweepy
client = tweepy.Client(bearer_token=TOKEN)
client.create_tweet(text="Hello")
```

**✅ ALWAYS:**
```python
from chimera.mcp_servers import MCPClient
result = await mcp_client.call_tool(
    server="mcp-server-twitter",
    tool="post_tweet",
    params={"text": "Hello"}
)
```

**Why:** MCP decouples our logic from external APIs. Direct calls create tight coupling.

---

### Rule 2: No Blocking Operations in Workers

**❌ NEVER:**
```python
def worker_execute(task):
    time.sleep(60)  # BLOCKS entire worker
    return process(task)
```

**✅ ALWAYS:**
```python
async def worker_execute(task):
    result = await asyncio.wait_for(
        process(task),
        timeout=task.timeout_seconds
    )
    return result
```

**Why:** Workers must remain async/non-blocking for parallel execution.

---

### Rule 3: All State Changes Use OCC

**❌ NEVER:**
```python
def update_state(data):
    global_state.update(data)  # RACE CONDITION
```

**✅ ALWAYS:**
```python
async def update_state(data, expected_version):
    current = await get_state_version()
    if current != expected_version:
        raise ConcurrencyConflictError()
    await commit_state(data, new_version)
```

**Why:** Distributed systems need Optimistic Concurrency Control to prevent races.

---

### Rule 4: Persona Validation is Mandatory

**❌ NEVER:**
```python
def generate_post(topic):
    return llm.generate(f"Write about {topic}")
```

**✅ ALWAYS:**
```python
async def generate_post(agent, topic):
    soul = await load_soul_md(agent.id)
    prompt = f"""
    Persona: {soul.voice_tone}, {soul.values}
    Topic: {topic}
    """
    content = await llm.generate(prompt)
    
    # Judge validates
    if not await judge.check_persona(content, soul):
        raise PersonaViolationError()
    return content
```

**Why:** Persona drift destroys brand consistency.

---

### Rule 5: Budget Checks Before Transactions

**❌ NEVER:**
```python
async def pay(amount, to):
    await wallet.send(amount, to)  # NO BUDGET CHECK
```

**✅ ALWAYS:**
```python
async def pay(agent_id, amount, to, reason):
    # CFO Judge approval
    approval = await cfo_judge.review({
        "agent_id": agent_id,
        "amount": amount,
        "reason": reason
    })
    if not approval.approved:
        raise BudgetExceededError()
    
    tx_hash = await wallet.send(amount, to)
    await log_transaction(agent_id, tx_hash, amount)
    return tx_hash
```

**Why:** Prevent runaway costs from bugs or hallucinations.

---

## CODE STYLE GUIDELINES

### Python Standards

```python
# ✅ GOOD: Type hints, async, proper error handling
async def create_agent(
    name: str,
    soul_path: str,
    character_ref: str
) -> Agent:
    """Create new agent with persona and wallet.
    
    Args:
        name: Agent display name
        soul_path: Path to SOUL.md file
        character_ref: LoRA identifier for images
        
    Returns:
        Initialized Agent instance
        
    Raises:
        FileNotFoundError: If SOUL.md doesn't exist
        ValidationError: If persona data invalid
    """
    if not Path(soul_path).exists():
        raise FileNotFoundError(f"SOUL.md not found: {soul_path}")
    
    persona = await parse_soul_md(soul_path)
    wallet = await create_wallet()
    
    agent = Agent(
        agent_id=uuid4(),
        name=name,
        persona=persona,
        wallet_address=wallet.address,
        character_reference_id=character_ref
    )
    
    await db.agents.insert(agent)
    logger.info(f"Agent created: {agent.agent_id}")
    return agent

# ❌ BAD: No types, blocking, no error handling
def create_agent(name, soul_path):
    persona = open(soul_path).read()
    agent = Agent(name=name, persona=persona)
    return agent
```

### Required Patterns

- **Type hints:** Always (`def func(x: int) -> str:`)
- **Async/await:** For all I/O operations
- **Pydantic:** For data validation
- **Structured logging:** Include trace_id
- **Error handling:** Specific exceptions with context

### Formatting

- **Black:** Line length 100
- **Import order:** stdlib, third-party, local
- **Docstrings:** Google style

---

## FILE ORGANIZATION

```
chimera-project/
├── specs/               # SPECIFICATIONS (read these first!)
│   ├── _meta.md        # Vision, constraints
│   ├── functional.md   # User stories (US-001, US-002...)
│   ├── technical.md    # API contracts, DB schemas
│   └── openclaw_integration.md
│
├── src/chimera/        # Source code
│   ├── core/          # Agent, Task, Result models
│   ├── services/      # Orchestrator, Planner, Worker, Judge
│   ├── mcp_servers/   # MCP integrations
│   ├── skills/        # Agent capabilities
│   └── utils/         # Utilities
│
├── tests/             # Tests (write BEFORE implementation)
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── skills/            # Skill documentation (I/O contracts)
└── research/          # Strategy documents
```

---

## TEST-DRIVEN DEVELOPMENT

### Process (Mandatory)

1. **Read acceptance criteria** from specs
2. **Write failing test** that validates criteria
3. **Run test** (should fail - this is success!)
4. **Implement** feature
5. **Run test** (should pass)
6. **Refactor** while keeping tests green

### Example

```python
# Step 1: Read specs/functional.md US-001
# Acceptance: "Agent persona defined via SOUL.md file"

# Step 2: Write failing test
def test_agent_loads_soul_md():
    """US-001: Agent persona instantiation from SOUL.md"""
    agent = Agent(
        agent_id="test-001",
        soul_path="fixtures/test_soul.md"
    )
    
    assert agent.persona is not None
    assert "voice_tone" in agent.persona
    assert "core_values" in agent.persona
    # This WILL fail initially - that's the point!

# Step 3: Run test → FAILS (expected)

# Step 4: Implement Agent.__init__ to load SOUL.md

# Step 5: Run test → PASSES
```

---

## COMMON PATTERNS

### Agent Creation
```python
# See: specs/functional.md US-001
# See: specs/technical.md Agent Profile schema
agent = Agent(
    agent_id=uuid4(),
    name=name,
    persona=await parse_soul_md(soul_path),
    wallet_address=await create_wallet(),
    character_reference_id=character_ref
)
```

### Task Execution
```python
# See: specs/functional.md US-014
# Workers execute tasks in isolation
async def execute_task(task: Task) -> Result:
    try:
        output = await skill.execute(task.input_data)
        return Result(
            task_id=task.task_id,
            status="success",
            output_data=output
        )
    except Exception as e:
        logger.error(f"Task failed: {e}", exc_info=True)
        return Result(
            task_id=task.task_id,
            status="failure",
            error_details=str(e)
        )
```

### MCP Tool Call
```python
# See: specs/technical.md MCP Tool Definitions
result = await mcp_client.call_tool(
    server="mcp-server-ideogram",
    tool="generate_image",
    params={
        "prompt": prompt,
        "character_reference_id": agent.character_reference_id
    }
)
```

---

## ANTI-PATTERNS TO AVOID

### ❌ Global State
```python
current_agent = None  # DON'T DO THIS
```

### ❌ Hardcoded Secrets
```python
API_KEY = "sk-1234567890"  # NEVER
```

### ❌ Tight Coupling
```python
class Planner:
    def __init__(self):
        self.twitter = TwitterAPI()  # BAD
```

### ❌ No Error Handling
```python
def process(task):
    return llm.generate(task.prompt)  # What if it fails?
```

---

## DEPENDENCY MANAGEMENT

**Using UV (fast Python package manager):**

```bash
# Add dependency
uv add package-name

# Install all deps
uv sync --all-extras

# Run command in venv
uv run pytest
```

**Important dependencies:**
- `fastapi` - Web framework
- `pydantic` - Data validation
- `sqlalchemy` + `asyncpg` - PostgreSQL
- `redis` - Caching/queuing
- `weaviate-client` - Vector DB
- `anthropic`, `google-generativeai` - LLMs
- `web3` - Blockchain

---

## MAKEFILE COMMANDS

```bash
make setup      # One-time setup
make test       # Run tests
make lint       # Check code quality
make format     # Auto-format code
make clean      # Remove artifacts

make run-orchestrator  # Start orchestrator
make run-worker        # Start worker

make docker-up    # Start services
make docker-down  # Stop services
```

---

## COMMIT MESSAGE FORMAT

```
<type>(<scope>): <subject>

<body>

Refs: #<issue-number>

Examples:
feat(agent): implement persona instantiation

- Add Agent class with SOUL.md parsing
- Create wallet via Coinbase AgentKit
- Satisfies US-001 acceptance criteria

Refs: #1

fix(worker): prevent blocking in task execution

- Replace time.sleep with asyncio.sleep
- Add timeout handling
- Fixes race condition in parallel tasks

Refs: #23
```

**Types:** feat, fix, docs, style, refactor, test, chore

---

## DEBUGGING TIPS

### Check Specs First
```bash
# Always start here
cat specs/functional.md | grep "US-XXX"
cat specs/technical.md | grep "API Contract"
```

### Use Trace IDs
```python
logger.info(
    "Task started",
    extra={"trace_id": task.trace_id, "task_id": task.task_id}
)
```

### Check Queue Depths
```python
# If system slow, check:
depth = redis.llen("taskqueue:agent_001")
```

---

## RESOURCES

- **Specifications:** `specs/` directory (START HERE)
- **Skills:** `skills/README.md`
- **Tooling:** `research/tooling_strategy.md`
- **IDE Rules:** `.cursor/rules` (comprehensive version)

---

## FINAL CHECKLIST

Before writing ANY code:

- [ ] Have you read the relevant spec?
- [ ] Can you quote the acceptance criteria?
- [ ] Do you know the API contract?
- [ ] Have you explained your plan?
- [ ] Will you write tests first (TDD)?
- [ ] Does your code follow the architectural rules?
- [ ] Are you using proper async/await patterns?
- [ ] Did you include error handling?
- [ ] Will it work with 1000+ concurrent agents?

---

**Remember:** Specifications are prophecy. Code is testimony. Tests are proof.

Good luck building autonomous AI influencers! 🚀
