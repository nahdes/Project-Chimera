# Project Chimera - Frontend Specification
**Version:** 1.0.0  
**Status:** DRAFT  
**Last Updated:** 2026-02-06  
**Addresses:** Feedback Gap - Missing Explicit Frontend Specifications

---

## 1. Frontend Architecture Overview

### 1.1 Technology Stack

**Framework:** React 18+ with TypeScript  
**State Management:** Redux Toolkit + RTK Query  
**UI Library:** shadcn/ui (Tailwind CSS-based components)  
**Routing:** React Router v6  
**Build Tool:** Vite  
**Testing:** Vitest + React Testing Library  
**API Client:** RTK Query (auto-generated from OpenAPI spec)

**Rationale:**
- React + TypeScript: Industry standard, strong typing prevents errors
- Redux Toolkit: Predictable state management for complex agent orchestration
- shadcn/ui: Production-ready components, customizable, accessible
- Vite: Fast development, optimized builds

---

## 2. Application Structure

### 2.1 Route Architecture

```typescript
// Frontend Routes
/                           # Dashboard (overview of all agents)
/agents                     # Agent list view
/agents/:id                 # Single agent detail view
/agents/create              # Create new agent wizard
/campaigns                  # Campaign management
/campaigns/:id              # Campaign detail & analytics
/tasks                      # Task queue monitoring
/tasks/:id                  # Task detail view
/hitl                       # Human-in-the-Loop review queue
/hitl/:id                   # HITL decision interface
/analytics                  # System-wide analytics
/settings                   # Configuration
/settings/mcp               # MCP server management
/settings/budgets           # Budget governance settings
/login                      # Authentication (future)
```

---

## 3. Core User Interfaces

### 3.1 Dashboard (Homepage)

**Purpose:** Real-time overview of autonomous influencer network

**Components:**

**Header:**
```typescript
interface DashboardHeader {
  totalAgents: number;
  activeAgents: number;
  tasksInQueue: number;
  monthlySpend: number;
  systemStatus: 'healthy' | 'degraded' | 'offline';
}
```

**Agent Grid:**
```typescript
interface AgentCard {
  agentId: string;
  name: string;
  avatarUrl: string;
  status: 'active' | 'paused' | 'error';
  recentPosts: number;
  engagement: number;
  earnings: number;
  lastActiveAt: string;
}
```

**Activity Feed:**
```typescript
interface ActivityFeedItem {
  id: string;
  type: 'post_published' | 'task_completed' | 'hitl_escalated' | 'budget_alert';
  agentId: string;
  timestamp: string;
  message: string;
  metadata: Record<string, any>;
}
```

**Wireframe (ASCII):**
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] Chimera Dashboard        [Notifications] [@User ▼]  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│ │ Agents  │ │ Active  │ │ Tasks   │ │ Spend   │           │
│ │   142   │ │   138   │ │   234   │ │ $1,234  │           │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────┤
│ Agent Grid                          │ Activity Feed         │
│ ┌────────┐ ┌────────┐ ┌────────┐  │ • Agent X posted...   │
│ │ Agent1 │ │ Agent2 │ │ Agent3 │  │ • Task completed...   │
│ │ [img]  │ │ [img]  │ │ [img]  │  │ • HITL escalation...  │
│ │ Active │ │ Active │ │ Paused │  │ • Budget alert...     │
│ └────────┘ └────────┘ └────────┘  │                       │
└─────────────────────────────────────────────────────────────┘
```

**API Endpoints:**
- `GET /api/v1/dashboard/summary` - Header metrics
- `GET /api/v1/agents?limit=20` - Agent grid
- `GET /api/v1/activity?since=1h` - Activity feed (SSE stream)

---

### 3.2 Agent Detail View

**Purpose:** Deep dive into single agent's performance and controls

**Components:**

**Agent Header:**
```typescript
interface AgentHeader {
  agentId: string;
  name: string;
  bio: string;
  avatarUrl: string;
  status: 'active' | 'paused' | 'archived';
  createdAt: string;
  walletAddress: string;
  characterReferenceId: string;
}
```

**Persona Editor:**
```typescript
interface PersonaEditor {
  soulMdPath: string;
  voiceTone: string[];
  coreValues: string[];
  directives: string[];
  readonly: boolean; // SOUL.md is immutable baseline
  mutableMemories: Memory[]; // Can be updated
}
```

**Performance Metrics:**
```typescript
interface AgentMetrics {
  timeRange: '24h' | '7d' | '30d';
  postsPublished: number;
  totalEngagement: number;
  avgEngagementRate: number;
  earnings: number;
  costs: number;
  roi: number;
  topPosts: Post[];
}
```

**Task Queue Viewer:**
```typescript
interface TaskQueueViewer {
  pendingTasks: Task[];
  inProgressTasks: Task[];
  completedTasks: Task[];
  failedTasks: Task[];
}
```

**Controls:**
- Pause/Resume agent
- Edit mutable memories
- Adjust budget limits
- View SOUL.md (read-only)
- Manual task injection
- Export analytics

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Agents                                    [Pause] │
├─────────────────────────────────────────────────────────────┤
│ ┌────────┐ Agent Name                                       │
│ │ Avatar │ @handle • Active • Created 2 days ago           │
│ │  [img] │ Wallet: 0x1234...5678                           │
│ └────────┘ Character: lora_ref_001                          │
├─────────────────────────────────────────────────────────────┤
│ [Persona] [Performance] [Tasks] [Content] [Settings]       │
├─────────────────────────────────────────────────────────────┤
│ Performance (Last 7 Days)                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Posts: 42  Engagement: 12.3K  ROI: +234%  Cost: $12.50 │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [Engagement Chart]                                          │
│ Top Posts:                                                  │
│ 1. "AI trends analysis..." - 2.3K likes                    │
│ 2. "Coffee culture deep dive..." - 1.8K likes              │
└─────────────────────────────────────────────────────────────┘
```

**API Endpoints:**
- `GET /api/v1/agents/:id` - Agent profile
- `GET /api/v1/agents/:id/metrics?range=7d` - Performance data
- `GET /api/v1/agents/:id/tasks` - Task history
- `PATCH /api/v1/agents/:id` - Update agent settings
- `POST /api/v1/agents/:id/pause` - Pause agent
- `POST /api/v1/agents/:id/resume` - Resume agent

---

### 3.3 Agent Creation Wizard

**Purpose:** Guide user through creating new autonomous agent

**Steps:**

**Step 1: Basic Info**
```typescript
interface BasicInfo {
  name: string;
  handle: string;
  bio: string;
  avatarFile: File | null;
}
```

**Step 2: Persona Definition**
```typescript
interface PersonaDefinition {
  voiceTone: string[]; // e.g., ["humorous", "educational", "authentic"]
  coreValues: string[]; // e.g., ["sustainability", "innovation"]
  directives: string[]; // e.g., ["Never discuss politics"]
  backstory: string; // Rich text editor
  soulMdTemplate: 'tech-influencer' | 'lifestyle' | 'education' | 'custom';
}
```

**Step 3: Character Reference**
```typescript
interface CharacterSetup {
  uploadImages: File[]; // For LoRA training
  stylePreference: 'realistic' | 'anime' | 'artistic';
  generatePreview: boolean;
}
```

**Step 4: Platform Configuration**
```typescript
interface PlatformSetup {
  platforms: ('twitter' | 'instagram' | 'tiktok')[];
  twitterConfig?: {
    apiKey: string;
    apiSecret: string;
    accessToken: string;
    accessSecret: string;
  };
  // Similar for other platforms
}
```

**Step 5: Budget & Limits**
```typescript
interface BudgetSetup {
  dailySpendLimit: number;
  monthlySpendLimit: number;
  perTaskLimits: {
    imageGeneration: number;
    videoGeneration: number;
    llmInference: number;
  };
  approvalThreshold: number; // Auto-approve below this amount
}
```

**Step 6: Review & Launch**
- Summary of all settings
- Estimated monthly cost
- Preview of generated SOUL.md
- Confirmation button

**Wireframe (Step 2 - Persona):**
```
┌─────────────────────────────────────────────────────────────┐
│ Create New Agent - Step 2 of 6                              │
├─────────────────────────────────────────────────────────────┤
│ [1✓] [2●] [3] [4] [5] [6]                                   │
│ Basic  Persona  Character  Platforms  Budget  Review        │
├─────────────────────────────────────────────────────────────┤
│ Define Agent Personality                                    │
│                                                              │
│ Voice & Tone (Select up to 3)                               │
│ [x] Humorous  [ ] Professional  [x] Authentic               │
│ [ ] Casual    [x] Educational   [ ] Inspirational           │
│                                                              │
│ Core Values (Add values)                                    │
│ [Sustainability] [Innovation] [Transparency] [+ Add]        │
│                                                              │
│ Directives (What should the agent NEVER do?)                │
│ • Never discuss politics                                    │
│ • Never promote competitors                                 │
│ • Never use offensive language                              │
│ [+ Add directive]                                           │
│                                                              │
│ Backstory                                                   │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ [Rich text editor for agent backstory...]             │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                              │
│                              [← Back]  [Next: Character →]  │
└─────────────────────────────────────────────────────────────┘
```

**API Endpoints:**
- `POST /api/v1/agents` - Create agent (final step)
- `POST /api/v1/agents/validate` - Validate config before creation
- `POST /api/v1/characters/lora` - Upload images for LoRA training
- `GET /api/v1/templates/soul` - Get SOUL.md templates

---

### 3.4 Human-in-the-Loop (HITL) Interface

**Purpose:** Review and approve/reject escalated decisions

**Components:**

**HITL Queue:**
```typescript
interface HITLQueueItem {
  hitlId: string;
  escalationReason: string;
  priority: 1 | 2 | 3 | 4 | 5;
  agentId: string;
  agentName: string;
  taskId: string;
  contextData: {
    generatedContent?: string;
    transactionDetails?: {
      amount: number;
      recipient: string;
      reason: string;
    };
    riskFactors: string[];
  };
  createdAt: string;
}
```

**Review Interface:**
```typescript
interface HITLReviewInterface {
  item: HITLQueueItem;
  originalTask: Task;
  proposedResult: Result;
  agentPersona: Persona; // For reference
  similarPastDecisions: HITLDecision[]; // Learning from history
  recommendedAction: 'approve' | 'reject' | 'modify' | null;
  confidenceScore: number;
}
```

**Decision Form:**
```typescript
interface HITLDecision {
  action: 'approve' | 'reject' | 'modify';
  feedback: string; // Explain reasoning for AI learning
  modifications?: {
    modifiedContent?: string;
    adjustedAmount?: number;
    // etc.
  };
  createRuleForFuture: boolean; // Add to guidelines?
}
```

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ HITL Review Queue                      [Filter ▼] [Sort ▼] │
├─────────────────────────────────────────────────────────────┤
│ Pending: 3   In Review: 1   Completed Today: 12            │
├─────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────────┐   │
│ │ [!] HIGH PRIORITY • Agent: TechInfluencer              │   │
│ │ Reason: High-cost transaction ($150)                   │   │
│ │ Created: 2 minutes ago                                 │   │
│ │                                          [Review →]    │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ [i] MEDIUM • Agent: FashionExpert                      │   │
│ │ Reason: Low persona consistency (0.65)                 │   │
│ │ Created: 5 minutes ago                                 │   │
│ │                                          [Review →]    │   │
│ └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

─── Review Detail ───────────────────────────────────────────
┌─────────────────────────────────────────────────────────────┐
│ Transaction Approval Request                                │
├─────────────────────────────────────────────────────────────┤
│ Agent: TechInfluencer wants to hire external service        │
│                                                              │
│ Transaction Details:                                        │
│ • Amount: $150.00 USD                                       │
│ • Recipient: did:openclaw:base:0x7a8f...                   │
│ • Service: "AI trend analysis report"                       │
│ • Agent Reasoning: "Need deep analysis for content series"  │
│                                                              │
│ Risk Assessment:                                            │
│ • Exceeds daily limit ($100)                                │
│ • New vendor (no history)                                   │
│ • High value transaction                                    │
│                                                              │
│ Recommendation: REVIEW REQUIRED                             │
│ Confidence: Medium (vendor reputation: unknown)             │
│                                                              │
│ Similar Past Decisions:                                     │
│ • Approved $120 to similar vendor (3 weeks ago)             │
│ • Rejected $200 to unknown vendor (1 month ago)             │
│                                                              │
│ Decision:                                                   │
│ ( ) Approve  ( ) Reject  (•) Approve with modifications    │
│                                                              │
│ Modifications:                                              │
│ New Amount: [$100.00]                                       │
│                                                              │
│ Feedback (for AI learning):                                 │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Approving at reduced amount. Agent should build track  │   │
│ │ record with vendor before larger transactions.         │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                              │
│ [ ] Add rule: "Max $100 for new vendors"                    │
│                                                              │
│                                 [Cancel]  [Submit Decision] │
└─────────────────────────────────────────────────────────────┘
```

**API Endpoints:**
- `GET /api/v1/hitl` - Get HITL queue
- `GET /api/v1/hitl/:id` - Get detailed item
- `POST /api/v1/hitl/:id/decision` - Submit decision
- `GET /api/v1/hitl/history?agentId=X` - Past decisions for context

---

### 3.5 Campaign Management

**Purpose:** Create and monitor multi-agent campaigns

**Campaign Creation:**
```typescript
interface Campaign {
  campaignId: string;
  name: string;
  description: string;
  agentIds: string[]; // Multiple agents can participate
  startDate: string;
  endDate: string;
  goals: CampaignGoal[];
  budget: number;
  spent: number;
  status: 'draft' | 'active' | 'paused' | 'completed';
}

interface CampaignGoal {
  type: 'posts' | 'engagement' | 'revenue' | 'custom';
  target: number;
  current: number;
  metric: string;
}
```

**Campaign Dashboard:**
- Progress bars for each goal
- Real-time spend tracking
- Agent performance comparison
- Content calendar
- Analytics charts

**API Endpoints:**
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns/:id` - Get campaign details
- `GET /api/v1/campaigns/:id/analytics` - Campaign analytics
- `PATCH /api/v1/campaigns/:id` - Update campaign

---

### 3.6 Task Queue Monitoring

**Purpose:** Real-time view of distributed task execution

**Components:**

**Queue Visualization:**
```typescript
interface QueueStats {
  taskQueue: {
    depth: number;
    processing: number;
    completed: number;
    failed: number;
  };
  reviewQueue: {
    depth: number;
    pending: number;
    approved: number;
    rejected: number;
  };
  workers: {
    active: number;
    idle: number;
    busy: number;
  };
}
```

**Task Detail Modal:**
```typescript
interface TaskDetailModal {
  task: Task;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedWorker: string | null;
  logs: LogEntry[];
  retryHistory: RetryAttempt[];
  duration: number | null;
}
```

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ Task Queue Monitor                          [Auto-refresh] │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│ │ Queue    │ │ Workers  │ │ Success  │ │ Failed   │       │
│ │   234    │ │  12/20   │ │   98.2%  │ │    4     │       │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│ Task Flow Diagram:                                          │
│ [TaskQueue: 234] → [Workers: 12] → [ReviewQueue: 15]       │
│                         ↓                    ↓              │
│                    [Processing]         [Judges: 3]         │
│                                              ↓              │
│                                         [Approved]          │
├─────────────────────────────────────────────────────────────┤
│ Recent Tasks:                                               │
│ ID          Type              Status      Duration          │
│ task_001    generate_post     ✓ Done     12.3s              │
│ task_002    generate_image    ⏳ Running 23.1s              │
│ task_003    analyze_trends    ✓ Done     45.2s              │
│ task_004    post_content      ❌ Failed  ERROR              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. State Management Architecture

### 4.1 Redux Store Structure

```typescript
interface RootState {
  auth: AuthState;
  agents: AgentsState;
  campaigns: CampaignsState;
  tasks: TasksState;
  hitl: HITLState;
  analytics: AnalyticsState;
  ui: UIState;
}

interface AgentsState {
  entities: Record<string, Agent>;
  ids: string[];
  selectedAgentId: string | null;
  loading: boolean;
  error: string | null;
  filters: AgentFilters;
}

interface TasksState {
  queueDepth: number;
  recentTasks: Task[];
  selectedTask: Task | null;
  workers: WorkerStats[];
}
```

### 4.2 RTK Query API Slices

```typescript
// Auto-generated from OpenAPI spec
export const chimera API = createApi({
  reducerPath: 'chimeraApi',
  baseQuery: fetchBaseQuery({ 
    baseUrl: process.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  }),
  tagTypes: ['Agent', 'Campaign', 'Task', 'HITL'],
  endpoints: (builder) => ({
    // Agents
    getAgents: builder.query<Agent[], void>(),
    getAgent: builder.query<Agent, string>(),
    createAgent: builder.mutation<Agent, CreateAgentRequest>(),
    updateAgent: builder.mutation<Agent, UpdateAgentRequest>(),
    pauseAgent: builder.mutation<void, string>(),
    
    // Tasks
    getTasks: builder.query<Task[], TaskFilters>(),
    getTask: builder.query<Task, string>(),
    
    // HITL
    getHITLQueue: builder.query<HITLQueueItem[], void>(),
    submitHITLDecision: builder.mutation<void, HITLDecision>(),
    
    // Real-time subscriptions (WebSocket)
    subscribeToActivityFeed: builder.query<ActivityFeedItem[], void>({
      queryFn: () => ({ data: [] }),
      async onCacheEntryAdded(arg, { cacheDataLoaded, cacheEntryRemoved, updateCachedData }) {
        const ws = new WebSocket('ws://localhost:8000/ws/activity');
        try {
          await cacheDataLoaded;
          ws.onmessage = (event) => {
            updateCachedData((draft) => {
              draft.unshift(JSON.parse(event.data));
            });
          };
        } catch {}
        await cacheEntryRemoved;
        ws.close();
      },
    }),
  }),
});
```

---

## 5. Component Library (shadcn/ui)

### 5.1 Custom Components

**AgentCard.tsx:**
```typescript
interface AgentCardProps {
  agent: Agent;
  onClick?: () => void;
  actions?: React.ReactNode;
}

export function AgentCard({ agent, onClick, actions }: AgentCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={onClick}>
      <CardHeader className="flex flex-row items-center gap-4">
        <Avatar className="h-16 w-16">
          <AvatarImage src={agent.avatarUrl} />
          <AvatarFallback>{agent.name[0]}</AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <CardTitle>{agent.name}</CardTitle>
          <CardDescription>@{agent.handle}</CardDescription>
        </div>
        <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
          {agent.status}
        </Badge>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Posts (7d)</p>
            <p className="text-2xl font-bold">{agent.metrics.postsLast7Days}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Engagement</p>
            <p className="text-2xl font-bold">{agent.metrics.engagement}</p>
          </div>
        </div>
      </CardContent>
      {actions && <CardFooter>{actions}</CardFooter>}
    </Card>
  );
}
```

**TaskStatusBadge.tsx:**
```typescript
interface TaskStatusBadgeProps {
  status: Task['status'];
}

export function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  const variants = {
    pending: 'secondary',
    in_progress: 'default',
    completed: 'success',
    failed: 'destructive',
  } as const;
  
  return <Badge variant={variants[status]}>{status}</Badge>;
}
```

---

## 6. Real-Time Features

### 6.1 WebSocket Connections

**Activity Feed (Server-Sent Events):**
```typescript
function useActivityFeed() {
  const [activities, setActivities] = useState<ActivityFeedItem[]>([]);
  
  useEffect(() => {
    const eventSource = new EventSource('/api/v1/activity/stream');
    
    eventSource.onmessage = (event) => {
      const item = JSON.parse(event.data);
      setActivities(prev => [item, ...prev].slice(0, 50));
    };
    
    return () => eventSource.close();
  }, []);
  
  return activities;
}
```

**Task Queue Updates:**
```typescript
function useTaskQueueStats() {
  const { data } = useSubscribeToTaskQueueQuery();
  return data;
}
```

---

## 7. Security & Permissions

### 7.1 Role-Based Access Control (RBAC)

```typescript
enum UserRole {
  Admin = 'admin',        // Full access
  Operator = 'operator',  // Manage agents, review HITL
  Viewer = 'viewer',      // Read-only
}

interface Permission {
  resource: 'agents' | 'campaigns' | 'tasks' | 'hitl' | 'settings';
  action: 'create' | 'read' | 'update' | 'delete';
}

const rolePermissions: Record<UserRole, Permission[]> = {
  [UserRole.Admin]: [
    { resource: '*', action: '*' }, // All permissions
  ],
  [UserRole.Operator]: [
    { resource: 'agents', action: 'read' },
    { resource: 'agents', action: 'update' },
    { resource: 'campaigns', action: '*' },
    { resource: 'hitl', action: '*' },
    { resource: 'tasks', action: 'read' },
  ],
  [UserRole.Viewer]: [
    { resource: '*', action: 'read' }, // Read-only everywhere
  ],
};
```

### 7.2 Protected Routes

```typescript
function ProtectedRoute({ children, requiredPermission }: ProtectedRouteProps) {
  const { user } = useAuth();
  const hasPermission = checkPermission(user.role, requiredPermission);
  
  if (!hasPermission) {
    return <Navigate to="/unauthorized" />;
  }
  
  return <>{children}</>;
}

// Usage
<Route path="/agents/create" element={
  <ProtectedRoute requiredPermission={{ resource: 'agents', action: 'create' }}>
    <CreateAgentPage />
  </ProtectedRoute>
} />
```

---

## 8. Performance Optimization

### 8.1 Code Splitting

```typescript
// Lazy load heavy components
const AgentDetailPage = lazy(() => import('./pages/AgentDetailPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const HITLReviewPage = lazy(() => import('./pages/HITLReviewPage'));

// Route with Suspense
<Route path="/agents/:id" element={
  <Suspense fallback={<PageLoader />}>
    <AgentDetailPage />
  </Suspense>
} />
```

### 8.2 Virtualization for Large Lists

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function AgentList({ agents }: { agents: Agent[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: agents.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100, // Agent card height
  });
  
  return (
    <div ref={parentRef} className="h-screen overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <AgentCard agent={agents[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 9. Testing Strategy

### 9.1 Component Tests

```typescript
// AgentCard.test.tsx
import { render, screen } from '@testing-library/react';
import { AgentCard } from './AgentCard';

describe('AgentCard', () => {
  it('displays agent name and status', () => {
    const mockAgent = {
      agentId: '123',
      name: 'TechInfluencer',
      status: 'active',
      // ...
    };
    
    render(<AgentCard agent={mockAgent} />);
    
    expect(screen.getByText('TechInfluencer')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<AgentCard agent={mockAgent} onClick={handleClick} />);
    
    screen.getByRole('article').click();
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### 9.2 Integration Tests

```typescript
// CreateAgent.integration.test.tsx
describe('Agent Creation Flow', () => {
  it('creates agent through full wizard', async () => {
    const { user } = renderWithProviders(<CreateAgentWizard />);
    
    // Step 1: Basic Info
    await user.type(screen.getByLabelText('Name'), 'TechInfluencer');
    await user.click(screen.getByText('Next'));
    
    // Step 2: Persona
    await user.click(screen.getByLabelText('Humorous'));
    await user.type(screen.getByLabelText('Backstory'), 'A tech expert...');
    await user.click(screen.getByText('Next'));
    
    // ... continue through steps
    
    // Final step
    await user.click(screen.getByText('Create Agent'));
    
    await waitFor(() => {
      expect(screen.getByText('Agent created successfully')).toBeInTheDocument();
    });
  });
});
```

---

## 10. Deployment & Build

### 10.1 Environment Configuration

```typescript
// .env.production
VITE_API_URL=https://api.chimera.aiqem.tech
VITE_WS_URL=wss://api.chimera.aiqem.tech
VITE_SENTRY_DSN=https://...
VITE_ANALYTICS_ID=G-...
```

### 10.2 Build Optimization

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
          'charts': ['recharts'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});
```

---

## 11. Accessibility (WCAG 2.1 AA)

### 11.1 Requirements

- ✅ Keyboard navigation for all interactive elements
- ✅ ARIA labels and roles
- ✅ Color contrast ratios ≥ 4.5:1
- ✅ Focus indicators visible
- ✅ Screen reader compatible
- ✅ Skip navigation links
- ✅ Semantic HTML

### 11.2 Implementation Example

```typescript
function AgentCard({ agent }: AgentCardProps) {
  return (
    <article
      role="article"
      aria-labelledby={`agent-${agent.agentId}-name`}
      tabIndex={0}
      onKeyPress={(e) => e.key === 'Enter' && handleClick()}
    >
      <h3 id={`agent-${agent.agentId}-name`}>{agent.name}</h3>
      <span role="status" aria-live="polite">
        {agent.status}
      </span>
    </article>
  );
}
```

---

## 12. Mobile Responsiveness

### 12.1 Breakpoints (Tailwind)

```typescript
// sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px

// Mobile-first approach
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {agents.map(agent => <AgentCard key={agent.agentId} agent={agent} />)}
</div>
```

### 12.2 Mobile Navigation

```typescript
function MobileNav() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <MenuIcon />
        </Button>
      </SheetTrigger>
      <SheetContent side="left">
        <nav className="flex flex-col gap-4">
          <Link to="/">Dashboard</Link>
          <Link to="/agents">Agents</Link>
          <Link to="/campaigns">Campaigns</Link>
          <Link to="/hitl">HITL Queue</Link>
        </nav>
      </SheetContent>
    </Sheet>
  );
}
```

---

## 13. Error Handling & User Feedback

### 13.1 Error Boundaries

```typescript
class ErrorBoundary extends React.Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to Sentry
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-screen">
          <Card>
            <CardHeader>
              <CardTitle>Something went wrong</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{this.state.error?.message}</p>
              <Button onClick={() => window.location.reload()}>
                Reload Page
              </Button>
            </CardContent>
          </Card>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### 13.2 Toast Notifications

```typescript
import { useToast } from '@/components/ui/use-toast';

function CreateAgentForm() {
  const { toast } = useToast();
  const [createAgent] = useCreateAgentMutation();
  
  const handleSubmit = async (data: CreateAgentRequest) => {
    try {
      await createAgent(data).unwrap();
      toast({
        title: 'Success',
        description: 'Agent created successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    }
  };
}
```

---

## 14. API Contract (OpenAPI Integration)

### 14.1 Auto-Generated TypeScript Types

```bash
# Generate TypeScript types from OpenAPI spec
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

```typescript
// src/types/api.ts (auto-generated)
export interface components {
  schemas: {
    Agent: {
      agent_id: string;
      name: string;
      status: 'active' | 'paused' | 'archived';
      // ... matches backend exactly
    };
  };
}

// Use in RTK Query
type Agent = components['schemas']['Agent'];
```

---

## 15. Acceptance Criteria

### 15.1 Functional Requirements

**Dashboard Page:**
- [ ] Displays accurate agent count, active agents, tasks in queue, monthly spend
- [ ] Agent grid shows max 20 agents per page with pagination
- [ ] Activity feed updates in real-time via SSE
- [ ] System status indicator reflects actual backend health
- [ ] Clicking agent card navigates to detail view

**Agent Creation:**
- [ ] All 6 wizard steps can be completed
- [ ] Form validation prevents invalid submissions
- [ ] Character images upload successfully
- [ ] SOUL.md preview matches input data
- [ ] Agent appears in dashboard within 5 seconds of creation

**HITL Interface:**
- [ ] Queue shows all pending items ordered by priority
- [ ] Review interface loads full context (task, result, persona)
- [ ] Approve/Reject/Modify actions execute correctly
- [ ] Feedback saves for AI learning
- [ ] Similar past decisions display for reference

### 15.2 Performance Requirements

- [ ] Initial page load < 2 seconds
- [ ] API response time < 500ms (p95)
- [ ] Real-time updates latency < 1 second
- [ ] Agent list renders 1000+ agents without lag (virtualized)
- [ ] Lighthouse score > 90 (Performance, Accessibility, Best Practices)

### 15.3 Accessibility Requirements

- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels present on all form inputs
- [ ] Color contrast ratios meet WCAG AA
- [ ] Screen reader announces dynamic content changes
- [ ] Focus indicators visible on all focusable elements

---

## 16. Future Enhancements

**Phase 2:**
- Dark mode support
- Advanced analytics dashboard with custom date ranges
- Bulk agent operations (pause/resume multiple)
- Export data (CSV, JSON)
- Agent templates/presets

**Phase 3:**
- Mobile app (React Native)
- Collaborative features (team comments, mentions)
- Audit log viewer
- Custom dashboard widgets (drag-and-drop)
- A/B testing framework for content

---

## Appendix A: File Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── AgentCard.tsx
│   │   ├── TaskStatusBadge.tsx
│   │   └── ...
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── AgentDetailPage.tsx
│   │   ├── CreateAgentPage.tsx
│   │   ├── HITLReviewPage.tsx
│   │   └── ...
│   ├── features/
│   │   ├── agents/
│   │   │   ├── agentsSlice.ts
│   │   │   └── agentsApi.ts
│   │   ├── campaigns/
│   │   ├── tasks/
│   │   └── hitl/
│   ├── hooks/
│   │   ├── useActivityFeed.ts
│   │   └── useAuth.ts
│   ├── types/
│   │   ├── api.ts        # Auto-generated from OpenAPI
│   │   └── index.ts
│   ├── utils/
│   ├── App.tsx
│   ├── main.tsx
│   └── store.ts
├── tests/
│   ├── unit/
│   └── integration/
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.ts
```

---

## Appendix B: Component Hierarchy

```
App
├── Router
│   ├── DashboardPage
│   │   ├── DashboardHeader (metrics)
│   │   ├── AgentGrid
│   │   │   └── AgentCard (×20)
│   │   └── ActivityFeed
│   │       └── ActivityFeedItem (×50)
│   ├── AgentDetailPage
│   │   ├── AgentHeader
│   │   ├── PersonaTab
│   │   ├── PerformanceTab
│   │   │   └── MetricsChart
│   │   ├── TasksTab
│   │   │   └── TaskList
│   │   └── SettingsTab
│   ├── CreateAgentPage
│   │   └── AgentCreationWizard
│   │       ├── BasicInfoStep
│   │       ├── PersonaStep
│   │       ├── CharacterStep
│   │       ├── PlatformStep
│   │       ├── BudgetStep
│   │       └── ReviewStep
│   ├── HITLReviewPage
│   │   ├── HITLQueue
│   │   │   └── HITLQueueItem (×N)
│   │   └── HITLReviewInterface
│   │       ├── ContextDisplay
│   │       ├── DecisionForm
│   │       └── SimilarDecisions
│   └── ...
└── Toast (notifications)
```

---

**Status:** Ready for frontend implementation  
**Dependencies:** Backend API must implement OpenAPI spec  
**Estimated Development:** 4-6 weeks (1 developer)

