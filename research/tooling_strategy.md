# Project Chimera - Tooling & Skills Strategy

**Version:** 1.0.0  
**Last Updated:** 2026-02-05

---

## Overview

This document distinguishes between two critical categories of tools in Project Chimera:

1. **Developer Tools (MCP Servers for Development)**: Tools that help YOU (the developer) build the system
2. **Agent Skills (Runtime Capabilities)**: Tools that Chimera agents use during autonomous operation

**Critical Distinction:**

- Developer tools are for **development time** (writing code, testing, debugging)
- Agent skills are for **runtime** (autonomous agent operation)

---

## Part A: Developer Tools (MCP for Development)

### Purpose

These MCP servers enhance the development workflow by providing standardized interfaces to common development operations.

### Selected Developer MCP Servers

---

#### 1. filesystem-mcp

**Purpose:** File system operations for code generation and management

**Capabilities:**

- Read/write files
- Create directories
- List directory contents
- Search for files by pattern

**Why We Need It:**
When AI assists with code generation, it needs to:

- Read existing code to understand context
- Create new files in the correct locations
- Navigate the project structure

**Example Usage:**

```typescript
// AI assistant reading a spec file
const spec = await mcp.call_tool("filesystem", "read_file", {
  path: "/home/claude/chimera-project/specs/functional.md",
});

// AI assistant creating a new service file
await mcp.call_tool("filesystem", "write_file", {
  path: "/home/claude/chimera-project/services/planner/planner_service.py",
  content: generated_code,
});
```

**Installation:**

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Configuration:**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["--allowed-directory", "/home/claude/chimera-project"]
    }
  }
}
```

---

#### 2. git-mcp

**Purpose:** Version control operations

**Capabilities:**

- Create commits
- Create branches
- View commit history
- Check git status
- Create pull requests (with GitHub integration)

**Why We Need It:**

- Automated commit messages based on changes
- Branch management for feature development
- Commit history analysis to understand code evolution

**Example Usage:**

```typescript
// AI assistant checking what files changed
const status = await mcp.call_tool("git", "status", {});

// AI assistant creating a commit
await mcp.call_tool("git", "commit", {
  message:
    "feat(planner): implement task decomposition\n\nSatisfies US-012 acceptance criteria",
  files: ["services/planner/planner_service.py"],
});
```

**Installation:**

```bash
npm install -g @modelcontextprotocol/server-git
```

---

#### 3. postgres-mcp

**Purpose:** Database schema management and queries during development

**Capabilities:**

- Execute SQL queries
- View table schemas
- Create migrations
- Inspect database state

**Why We Need It:**

- AI can help write SQL queries
- Automated migration generation
- Database debugging during development

**Example Usage:**

```typescript
// AI assistant checking database schema
const schema = await mcp.call_tool("postgres", "describe_table", {
  table: "agents",
});

// AI assistant generating a migration
await mcp.call_tool("postgres", "execute", {
  query: `
    ALTER TABLE agents 
    ADD COLUMN character_reference_id VARCHAR(255);
  `,
});
```

**Configuration:**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "mcp-server-postgres",
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/chimera_dev"
      }
    }
  }
}
```

---

#### 4. docker-mcp (Custom)

**Purpose:** Container management for local development

**Capabilities:**

- Start/stop containers
- View container logs
- Check container health
- Rebuild images

**Why We Need It:**

- AI can help debug container issues
- Automated container orchestration during dev
- Quick environment resets

**Example Usage:**

```typescript
// AI assistant checking if services are running
const containers = await mcp.call_tool("docker", "list_containers", {});

// AI assistant restarting a service
await mcp.call_tool("docker", "restart", {
  container_name: "chimera-worker-1",
});
```

**Implementation:** Custom MCP server (to be built)

---

#### 5. test-runner-mcp (Custom)

**Purpose:** Execute tests and analyze results

**Capabilities:**

- Run specific test files
- Run test suites
- Parse test results
- Generate coverage reports

**Why We Need It:**

- AI can run tests to verify code changes
- Automated test result analysis
- Test-driven development workflow

**Example Usage:**

```typescript
// AI assistant running tests for a specific module
const result = await mcp.call_tool("test-runner", "run_tests", {
  path: "tests/unit/test_planner_service.py",
});

if (!result.all_passed) {
  // AI can analyze failures and suggest fixes
  const failures = result.failures;
}
```

**Implementation:** Custom MCP server wrapping pytest

---

### Developer MCP Servers Priority Matrix

| Server          | Priority | Status    | Complexity |
| --------------- | -------- | --------- | ---------- |
| filesystem-mcp  | P0       | Available | Low        |
| git-mcp         | P0       | Available | Low        |
| postgres-mcp    | P1       | Available | Medium     |
| docker-mcp      | P1       | Custom    | Medium     |
| test-runner-mcp | P1       | Custom    | Low        |

---

### Development Workflow with MCP Tools

```
Developer asks AI: "Implement US-012 (Task Decomposition)"
                            ↓
AI uses filesystem-mcp to read specs/functional.md
                            ↓
AI uses postgres-mcp to check database schema
                            ↓
AI uses test-runner-mcp to run existing tests
                            ↓
AI generates code and tests
                            ↓
AI uses filesystem-mcp to write new files
                            ↓
AI uses test-runner-mcp to verify tests pass
                            ↓
AI uses git-mcp to create commit
```

---

## Part B: Agent Skills (Runtime Capabilities)

### Purpose

Skills are specific capability packages that Chimera agents use during autonomous operation. Each skill has a defined input/output contract.

### Skill Architecture

```
┌─────────────────────────────────────────────┐
│            Cognitive Core (LLM)             │
│  "I need to analyze trending topics"        │
└─────────────────────────────────────────────┘
                    ↓
            Invokes Skill
                    ↓
┌─────────────────────────────────────────────┐
│        skill_analyze_trends                 │
│  Input: {topic_category, timeframe}         │
│  Logic: Fetch data → Analyze → Summarize   │
│  Output: {trends, insights, recommendations}│
└─────────────────────────────────────────────┘
                    ↓
         Uses MCP Tools (if needed)
                    ↓
    mcp-server-news, mcp-server-twitter
```

**Key Principle:** Skills are business logic. MCP Tools are technical integrations.

---

### Critical Skills for MVP

#### Skill 1: skill_analyze_trends

#### Skill 2: skill_generate_social_post

#### Skill 3: skill_generate_character_image

Let me create the detailed specifications for each...

---

## Skill Development Guidelines

### 1. Input/Output Contracts

Every skill MUST define clear JSON schemas for input and output.

```python
from pydantic import BaseModel

class AnalyzeTrendsInput(BaseModel):
    topic_category: str
    timeframe_hours: int = 24
    min_relevance: float = 0.7

class AnalyzeTrendsOutput(BaseModel):
    trending_topics: List[TrendingTopic]
    insights: str
    recommended_actions: List[str]
```

---

### 2. Error Handling

Skills must handle all failure modes gracefully:

- API timeouts
- Rate limiting
- Invalid input
- Null responses

---

### 3. Observability

Every skill execution must log:

- Input parameters
- Execution time
- Cost (if applicable)
- Output summary
- Errors/warnings

---

### 4. Testing Strategy

Each skill requires:

- Unit tests (mock MCP tools)
- Integration tests (use real MCP tools in test mode)
- Performance benchmarks

---

## Skill Manifest Format

Each skill directory contains:

```
skills/skill_analyze_trends/
├── README.md           # Skill documentation
├── __init__.py        # Skill registration
├── skill.py           # Main skill logic
├── schema.py          # Input/Output models
├── tests/
│   ├── test_skill.py  # Unit tests
│   └── fixtures/      # Test data
└── examples/          # Usage examples
```

---

## Skill Discovery & Registration

Skills are registered at startup:

```python
# services/worker/worker_service.py
from skills import get_all_skills

class WorkerService:
    def __init__(self):
        self.skills = {}
        for skill in get_all_skills():
            self.skills[skill.name] = skill

    async def execute_task(self, task: Task):
        skill_name = task.type  # e.g., "analyze_trends"
        skill = self.skills.get(skill_name)
        if not skill:
            raise UnknownSkillError(skill_name)

        result = await skill.execute(task.input_data)
        return result
```

---

## MCP Tools vs Skills: Decision Matrix

| Question                                   | MCP Tool | Skill |
| ------------------------------------------ | -------- | ----- |
| Is this a technical integration (API, DB)? | ✅       | ❌    |
| Does this involve business logic?          | ❌       | ✅    |
| Could this be used by multiple agents?     | ✅       | ✅    |
| Does this require agent-specific context?  | ❌       | ✅    |
| Is this a reusable atomic operation?       | ✅       | ❌    |

**Examples:**

- "Post to Twitter" → MCP Tool (technical integration)
- "Decide what to post about" → Skill (business logic)
- "Generate image via Ideogram" → MCP Tool
- "Generate character-consistent image" → Skill (adds business logic on top of MCP Tool)

---

## Next Steps

### Phase 1: Development Setup (Week 1)

- [ ] Install filesystem-mcp, git-mcp, postgres-mcp
- [ ] Configure MCP servers in IDE
- [ ] Test MCP server connectivity
- [ ] Document MCP server usage patterns

### Phase 2: Custom Development Tools (Week 2)

- [ ] Build docker-mcp server
- [ ] Build test-runner-mcp server
- [ ] Integration test custom servers
- [ ] Document custom server APIs

### Phase 3: Core Skills Implementation (Week 3-4)

- [ ] Implement skill_analyze_trends
- [ ] Implement skill_generate_social_post
- [ ] Implement skill_generate_character_image
- [ ] Write comprehensive tests for each skill

### Phase 4: Skill Expansion (Week 5+)

- [ ] Implement skill_reply_to_comment
- [ ] Implement skill_schedule_campaign
- [ ] Implement skill_analyze_engagement
- [ ] Build skill discovery system

---

## Resources

**MCP Documentation:**

- Official Spec: https://spec.modelcontextprotocol.io/
- Example Servers: https://github.com/modelcontextprotocol/servers

**Skill Development:**

- Pydantic Docs: https://docs.pydantic.dev/
- FastAPI Patterns: https://fastapi.tiangolo.com/

**Testing:**

- Pytest Async: https://pytest-asyncio.readthedocs.io/
- Mock Strategies: https://docs.python.org/3/library/unittest.mock.html

---

_"Tools are the hands of the developer. Skills are the mind of the agent."_
