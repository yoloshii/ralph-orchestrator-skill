---
name: ralph-orchestrator
description: Autonomous E2E development with automatic multi-model workflow - Codex GPT 5.3 High (architecture + review) + Ralph/Claude Opus 4.6 (implementation). When invoked, automatically executes full cycle - planning, parallel implementation via worktree subagents, review, parallel fix resolution. Exa MCP (code examples) + Ref MCP (docs) used only when Codex review fix suggestions are unclear. Use when user requests "run ralph", "implement this autonomously", or wants complete feature development with quality analysis.
allowed-tools: Bash(ralph*), Bash(python*), Bash(codex*), Bash(git*), Read, Write, Edit, Glob, Task, grepai_search, grepai_trace_callers, grepai_trace_callees, grepai_trace_graph, mcp__exa__get_code_context_exa, mcp__exa__web_search_exa, mcp__Ref__ref_search_documentation, mcp__Ref__ref_read_url
---

# Ralph Orchestrator

Wraps ralph-orchestrator for E2E autonomous development loops from Claude Code.

## Quick Start

**Prerequisites:** Ensure `ralph.yml` in your project (or default at `~/Projects/ralph.yml`) contains:

```yaml
cli:
  backend: "claude"
  args: ["--dangerously-skip-permissions"]
```

**Usage:**

```bash
# Validate environment
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --check

# Standard workflow: plan + run
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --plan "Add user authentication" --run

# Multi-model workflow: Codex architecture + Ralph implementation + Codex review
# (See "Multi-Model Integration" section below)
```

## Workflow

### Phase 0: Prompt Refinement & Optimization

**Purpose:** Transform user's feature request into optimal Codex GPT 5.3 High planning prompt while preserving all nuance and intent.

**Guiding Principles (January 2026 Research):**
- Systems-first architecture (not prompt-first)
- Remove planning preambles
- Use appropriate reasoning effort (medium/high/xhigh)
- Structured output formatting
- Chain-of-thought decomposition

#### Step 1: Information Gathering

**Ask clarifying questions ONLY if:**
- Feature scope is ambiguous
- Technical constraints are unspecified
- Domain context is missing
- Performance/security requirements unclear
- Integration points undefined

**Example clarifying questions:**
```
AskUserQuestion:
  questions:
    - question: "What is the primary domain/tech stack for this feature?"
      header: "Domain"
      options:
        - label: "Web API (REST/GraphQL)"
          description: "Backend API service"
        - label: "Frontend (React/Vue/etc)"
          description: "User interface components"
        - label: "Data Pipeline"
          description: "ETL, streaming, batch processing"
        - label: "Infrastructure/DevOps"
          description: "CI/CD, deployment, monitoring"
      multiSelect: false

    - question: "What are the critical constraints?"
      header: "Constraints"
      options:
        - label: "Performance (low latency, high throughput)"
          description: "Speed and scale are paramount"
        - label: "Security/Compliance (GDPR, SOC2, etc)"
          description: "Regulatory requirements must be met"
        - label: "Cost optimization"
          description: "Minimize infrastructure/operational costs"
        - label: "Developer experience"
          description: "Easy to maintain and extend"
      multiSelect: true
```

**CRITICAL:** Only ask questions for genuinely unclear aspects. If user provides sufficient detail, proceed directly to refactoring.

#### Step 2: Prompt Refactoring

**Transform user request using this structure:**

```python
refactored_prompt = f"""Role: Lead Software Architect specializing in {domain}

Context:
- Project: {project_name}
- Tech Stack: {tech_stack}
- Constraints: {constraints_from_user_or_questions}
- Existing Architecture: {codebase_summary}

User Intent (verbatim):
{original_user_request}

Task: Design the system architecture for: {feature_summary}

Output Requirements (Ralph TDD-Style Planning):

## Architecture Overview
1. System Design Summary
   - High-level architecture (Mermaid component diagram)
   - Data flow patterns
   - Integration points with existing systems
   - Technology choices with rationale

2. Component Breakdown
   - Core components with clear responsibilities
   - Component interactions and dependencies
   - API contracts (JSON schema or TypeScript types)
   - Data models with relationships and constraints

3. Risk Analysis & Edge Cases
   - Failure scenarios (network, data, auth, rate limits)
   - Security considerations (auth, encryption, attack surface)
   - Performance implications
   - Migration strategy if modifying existing schemas

## Implementation Plan (TDD Format)

For each implementation step, provide:

### Step N: [Clear Objective]

**Objective:** What we're building and why (one sentence)

**Implementation:**
- Specific files to create/modify
- Concrete code changes (functions, classes, interfaces)
- Configuration or schema updates
- Dependencies or libraries needed

**Test Requirements (DEFINE BEFORE IMPLEMENTING):**
- Unit tests: What specific behavior to test
- Integration tests: What interactions to verify
- Test fixtures or mocks needed
- Acceptance criteria (how to know it works)

**Integration:**
- How this step connects to other components
- What interfaces or contracts it depends on
- What it exposes for future steps

**Demo/Verification:**
- Command to run after implementing
- Expected output or behavior
- How to manually verify correctness

---

4. Implementation Checklist
   - [ ] Step 1: [Description]
   - [ ] Step 2: [Description]
   - [ ] Step 3: [Description]
   - ...

5. Step Dependencies
   - Mermaid flowchart showing which steps must complete before others
   - Identify parallel vs sequential work

6. Estimated Scope
   - Table with: Step | Files Modified | Complexity (Low/Medium/High)

## Ralph Guardrails (CRITICAL)

Your architecture must align with these principles:
- **Fresh context each iteration** - Each build step can be executed independently
- **Verification is mandatory** - Tests/typecheck/lint must pass before moving forward
- **Search before assuming** - Don't assume functionality is missing, verify first
- **Backpressure over prescription** - Design gates that reject bad work (tests fail = stop)
- **Disk is state** - Use files, git, and explicit artifacts for handoff between steps

Format: Structured markdown with Mermaid diagrams and JSON schemas where applicable.

Constraints:
- Follow existing codebase patterns: {existing_patterns}
- Maintain compatibility with: {dependencies}
- Optimize for: {performance_goals}
- {user_specific_constraints}

DO NOT include preambles, status updates, or meta-commentary. Proceed directly to architectural design.
"""
```

#### Step 3: Reasoning Effort Selection

**ALWAYS use `high` reasoning effort:**

```python
# Always use high for quality results
reasoning_effort = "high"
```

High reasoning effort ensures thorough analysis for both planning and review phases. The marginal cost increase is justified by significantly better architectural decisions and more comprehensive code review findings.

#### Step 4: Nuance Preservation Rules

**MUST preserve:**
- All specific technical requirements mentioned by user
- Performance targets, SLAs, metrics
- Security/compliance requirements
- User preferences for libraries, frameworks, patterns
- Timeline constraints
- Budget constraints

**Example preservation:**
```
User: "Add authentication with JWT, must support refresh tokens, Redis for session store"

Refactored (preserves all specifics):
- Authentication: JWT-based (access + refresh tokens)
- Session Store: Redis (as specified)
- Adds architectural context: token rotation, expiry policies, security best practices

NOT:
- Authentication: Consider OAuth2, SAML, or JWT  ❌ (changes user's choice)
- Session Store: Evaluate Redis, Memcached, or in-memory  ❌ (introduces alternatives)
```

**ONLY change if user explicitly revises during follow-up:**
```
User: "Add rate limiting"
You ask: "Which rate limiting strategy - token bucket, sliding window, or fixed window?"
User: "Actually, let's use sliding window with Redis"
Refactored: Rate limiting using sliding window algorithm with Redis backing store ✓
```

#### Step 5: Anti-Patterns to Avoid

**❌ DO NOT:**
- Ask questions already answered in user's request
- Add verbose preambles ("I will now analyze...")
- Over-constrain output format with micro-management
- Change user's technical choices without explicit approval
- Ask questions for the sake of thoroughness when context is clear

**✓ DO:**
- Ask targeted questions only for genuine ambiguity
- Preserve all user-specified technologies, patterns, constraints
- Structure the prompt for optimal Codex reasoning
- Use appropriate reasoning effort based on complexity
- Let Codex reason without forcing meta-commentary

#### Example Refactoring

**User Request:**
> "Add user authentication to the app"

**Clarifying Questions:**
```
1. What authentication method? (OAuth2, JWT, Session-based, Magic links)
2. What are the security requirements? (MFA, password policies, session timeout)
3. Integration points? (Existing user DB, third-party providers)
```

**User Answers:**
> "JWT with refresh tokens, must support Google OAuth, want MFA optional, Redis for sessions"

**Refactored Prompt:**
```
Role: Lead Software Architect specializing in Web Application Security

Context:
- Project: [app_name]
- Tech Stack: [detected from codebase]
- Constraints: Must integrate with existing user database, production Redis available
- Existing Architecture: [codebase summary]

User Intent (verbatim):
"Add user authentication to the app using JWT with refresh tokens, must support Google OAuth, want MFA optional, Redis for sessions"

Task: Design the authentication system architecture

Output Requirements:
1. System Design Overview
   - Authentication flow diagram (Mermaid)
   - Token lifecycle (access + refresh)
   - OAuth2 integration with Google
   - MFA workflow (optional enrollment)
   - Session management via Redis

2. Component Breakdown
   - Auth service (JWT generation, validation, refresh)
   - OAuth2 client (Google integration)
   - MFA service (TOTP, backup codes)
   - Session manager (Redis-backed)
   - Middleware (route protection)

3. API Contracts
   - POST /auth/login (email/password → JWT)
   - POST /auth/oauth/google (OAuth flow)
   - POST /auth/refresh (refresh token → new access token)
   - POST /auth/mfa/enroll (optional MFA setup)
   - POST /auth/mfa/verify (TOTP verification)

4. Data Models
   - User schema (id, email, password_hash, mfa_enabled, mfa_secret)
   - RefreshToken schema (token_id, user_id, expires_at, revoked)
   - Session schema in Redis (session_id, user_id, metadata, ttl)

5. Edge Cases & Error Handling
   - Expired tokens, revoked sessions, concurrent logins
   - OAuth failures (Google API down, user cancels)
   - MFA lockout scenarios, backup codes
   - Rate limiting for login attempts

6. Security Architecture
   - Password hashing (bcrypt/argon2)
   - Token signing algorithm (RS256)
   - HTTPS-only cookies for refresh tokens
   - CSRF protection for OAuth callbacks
   - Rate limiting and brute-force protection

7. Testing Strategy
   - Unit: Token generation/validation, password hashing
   - Integration: OAuth flow, MFA enrollment
   - E2E: Full login/logout cycles, session persistence

8. Implementation Sequence
   1. Core JWT service (generation, validation)
   2. User model + password hashing
   3. Login/logout endpoints
   4. Refresh token mechanism
   5. Google OAuth integration
   6. Optional MFA (last, can be skipped for MVP)

Format: Structured markdown with Mermaid diagrams for flows

Constraints:
- Use existing Redis instance (connection details in .env)
- Follow existing API route structure (/api/v1/*)
- Maintain compatibility with current User model
- JWT secret must be environment variable
- Optimize for: Security first, then developer experience

DO NOT include preambles or status updates. Proceed directly to architectural design.
```

**Reasoning Effort:** `high` (authentication is complex, security-critical)

---

### Phase 1: Validation

```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --check
ralph preflight
```

Verifies:
- `ralph` CLI installed and in PATH
- Current directory is a git repository
- At least one commit exists
- `ralph preflight` validates configuration, backend availability, and project structure

### Phase 2: Planning (PDD)

**Option A: Interactive planning session**
```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --plan "Add JWT authentication"
```

Creates:
- `specs/` directory with requirements.md, design.md, implementation-plan.md
- `PROMPT.md` referencing the specs

**Option B: Generate from tasks (skip planning)**
```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --generate \
  --title "Add Authentication" \
  --tasks "Add NextAuth.js" "Create login page" "Add session provider"
```

### Phase 3: Execution

**Standard (sequential):**
```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --run
```

Or combined:
```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --plan "description" --run
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --generate --title "..." --tasks "..." --run
```

**Parallel execution (when PROMPT.md contains task waves):**

If PROMPT.md uses the wave format (see "Parallel Task Execution" section below), independent tasks within each wave run in parallel via git worktrees + Task subagents.

### Phase 4: Report

Script automatically reports:
- Exit code interpretation
- Task completion summary
- Any errors or partial progress

## CLI Options

| Option | Description |
|--------|-------------|
| `--check` | Validate environment (ralph, git, etc.) |
| `--plan TEXT` | Run PDD planning session with description |
| `--generate` | Generate PROMPT.md from --title and --tasks |
| `--title TEXT` | Title for generated PROMPT.md |
| `--tasks TEXT...` | Task list for generated PROMPT.md |
| `--context TEXT` | Additional context for PROMPT.md |
| `--run` | Execute ralph run after plan/generate |
| `--max-iterations N` | Iteration limit (default: 50) |
| `--backend NAME` | Override backend (default: claude) |
| `--dry-run` | Preview without executing |

## Default Workflow: Multi-Model (Codex + Ralph + Exa/Ref)

When ralph-orchestrator skill is invoked, it executes the full multi-model cycle:

0. **Prompt Refinement** - Clarify user intent, refactor for optimal Codex ingestion
1. **Codex Planning** - GPT 5.3 High generates thorough architecture (single sequential call)
2. **PROMPT Generation** - Extract tasks from architecture (with wave annotations for parallelism)
3. **Ralph Implementation** - Claude Opus 4.6 executes via orchestrate.py; independent task waves run in parallel via worktree + Task subagents
4. **Codex Review** - GPT 5.3 High analyzes implementation for edge cases (single sequential call)
5. **Issue Resolution** - Parse review findings, fix independent issues in parallel via Task subagents; Exa/Ref research only if fix isn't obvious from review
6. **Report** - Deliver results with review findings

No decision tree - this is the complete workflow every time.

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | LOOP_COMPLETE | Success - all tasks done |
| 1 | Failure | Check .ralph/ logs for details |
| 2 | Limit exceeded | Partial progress, may resume |
| 130 | Interrupted | User cancelled |

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| `ralph not found` | CLI not installed | `npm install -g @ralph-orchestrator/ralph-cli` |
| `Not a git repository` | No .git directory | `git init && git add . && git commit -m "init"` |
| `No commits` | Empty git history | `git add . && git commit -m "Initial commit"` |
| `PROMPT.md exists` | Previous run | Use `--run` to resume or delete PROMPT.md |

## PROMPT.md Format

Generated PROMPT.md follows this structure:

```markdown
# {title}

## Objective
{description from --plan or context}

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Context
{additional context if provided}

## Constraints
- Follow existing code patterns
- Run tests after changes
- Commit after each task

## Acceptance Criteria
- All tasks completed
- Tests passing
- No linting errors
```

### PROMPT.md Wave Format (Parallel Execution)

When Codex architecture identifies independent implementation steps, generate PROMPT.md with wave annotations. Tasks within the same wave have no dependencies on each other and run in parallel via worktrees.

```markdown
# {title}

## Objective
{description}

## Tasks

### Wave 1 (parallel - no dependencies)
- [ ] Add authentication module (src/auth/)
- [ ] Add logging system (src/logging/)
- [ ] Add configuration loader (src/config/)

### Wave 2 (depends on Wave 1)
- [ ] Add authorization middleware (depends: authentication)
- [ ] Add audit logging (depends: logging)

### Wave 3 (depends on all above)
- [ ] Add integration tests

## Constraints
- Each module must have test coverage
- All tests must pass before merging waves
```

**Wave detection:** If PROMPT.md contains `### Wave N` headings, Phase 3 uses parallel execution. Otherwise, standard sequential ralph execution.

**When to use waves:**
- ≥2 tasks touch entirely different directories/modules
- Tasks have no shared file dependencies
- Each task is substantial enough to justify worktree overhead (≥5 ralph iterations expected)

**When NOT to use waves (keep sequential):**
- Tasks edit overlapping files
- Tasks have tight sequential dependencies
- Small tasks (<5 iterations each, overhead > benefit)
- Single-task PROMPT.md

## Examples

### Example 1: Full PDD workflow

```bash
# Interactive planning + execution
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py \
  --plan "Add user authentication with OAuth2 (Google, GitHub)" \
  --run
```

### Example 2: Quick task execution

```bash
# Skip planning, provide tasks directly
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py \
  --generate \
  --title "Add Input Validation" \
  --tasks "Add zod schema" "Validate /users endpoint" "Add error messages" \
  --run
```

### Example 3: Dry run preview

```bash
# See what would be generated without executing
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py \
  --generate \
  --title "Refactor Auth" \
  --tasks "Extract auth logic" "Add tests" \
  --dry-run
```

### Example 4: Custom iteration limit

```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py \
  --plan "Complex feature" \
  --run \
  --max-iterations 100
```

### Example 5: Multi-model workflow with prompt refinement

```
User: "Add rate limiting to API endpoints"

# Phase 0: Prompt Refinement
Claude asks clarifying questions:
  1. Which rate limiting strategy? (token bucket, sliding window, fixed window)
  2. What backing store? (Redis, in-memory, database)
  3. Rate limit scope? (per-user, per-IP, per-API-key)

User answers:
  - Sliding window algorithm
  - Redis backing store
  - Per-API-key with fallback to per-IP

Claude refactors into optimal Codex prompt:
  Role: Lead Software Architect specializing in API Infrastructure
  Context: Express.js API, Redis available, ~10k requests/sec
  User Intent: "Add rate limiting with sliding window, Redis, per-API-key + per-IP fallback"
  [... full structured prompt with 8 output requirements ...]
  Reasoning effort: high (complex multi-tier rate limiting)

# Phase 1: Codex Planning (background execution)
Run: codex exec -o .ralph/codex-architecture.md -- "REFINED_PROMPT" 2>/dev/null & wait $!
Read: .ralph/codex-architecture.md
  → Contains architecture with sliding window implementation, Redis schema, middleware design

# Phase 2: PROMPT Generation
Generate PROMPT.md from Codex architecture with wave annotations:
  Wave 1 (parallel): sliding-window module, Redis store adapter, config loader
  Wave 2 (sequential): middleware integration, tests

# Phase 3: Ralph Implementation (parallel waves)
Wave 1: 3 Task subagents in worktrees (sliding-window, Redis adapter, config)
  → All 3 complete in ~40 min (vs ~90 min sequential)
Wave 2: sequential ralph run for middleware + tests
  → Merges wave 1 results first, then implements integration

# Phase 4: Codex Review (single sequential call, background)
Run: codex exec review --base HEAD~N > .ralph/codex-review.md 2>&1 & wait $!
Read: .ralph/codex-review.md
  → Finds: rate limit doesn't reset on restart, missing concurrency tests
  → Suggests: Redis persistence config, add concurrent request test

# Phase 5: Fix review issues (parallel - different files)
  2 issues in 2 files → 2 parallel Task subagents
  Subagent 1: Apply Redis persistence fix (clear suggestion, no Exa/Ref needed)
  Subagent 2: Add concurrency tests (clear suggestion, no Exa/Ref needed)
  Both complete in ~5 min

# Phase 6: Report
Complete implementation with review findings, all fixes applied

# Result: User's nuanced request preserved (sliding window, Redis, per-API-key)
# Parallel execution: ~65 min total (vs ~120 min sequential)
# Uses: 2 Codex requests (planning + review), parallel Claude for implementation + fixes
```

### Example 6: Prompt refinement with preservation

```
User: "Add authentication with JWT, must support refresh tokens, Redis for session store"

# Phase 0: Prompt Refinement
Claude analyzes: All technical choices specified, no ambiguity
  ✓ Auth method: JWT (specified)
  ✓ Features: Refresh tokens (specified)
  ✓ Session store: Redis (specified)

No clarifying questions needed - user was explicit.

Claude refactors preserving ALL specifics:
  Role: Lead Software Architect specializing in Web Application Security
  User Intent (verbatim): "Add authentication with JWT, must support refresh tokens, Redis for session store"

  Output Requirements:
  1. System Design Overview
     - JWT-based authentication (access + refresh tokens as specified)
     - Redis session management (as specified)
     [...]

  Constraints:
  - MUST use JWT for authentication (user requirement)
  - MUST implement refresh token mechanism (user requirement)
  - MUST use Redis for session storage (user requirement)

  Reasoning effort: high (authentication is security-critical)

# Continues to Phase 1 (Codex Planning) with refined prompt
# User's technical choices (JWT, refresh tokens, Redis) are preserved and emphasized
```

## Integration with Claude Code

**Automatic multi-model workflow:**

1. User discusses requirements with Claude Code
2. User: "Run ralph to implement this" or "Use ralph-orchestrator"
3. Claude invokes ralph-orchestrator skill
4. **Skill executes automatically:**
   - **Refines user request** into optimal Codex prompt (asks clarifying questions if needed)
   - Calls Codex for architectural planning with refined prompt (single sequential call)
   - Generates PROMPT.md from architecture (with wave annotations for parallelism if applicable)
   - Runs ralph implementation — independent task waves run in parallel via worktrees + Task subagents
   - Calls Codex for code review (single sequential call)
   - Fixes review issues — independent issues fixed in parallel via Task subagents, each driven by Codex review findings; Exa/Ref only if suggested fix is unclear
   - Reports results with review findings
5. User receives complete implementation + quality analysis + working solutions

**When to use ralph-orchestrator:**
- Well-defined feature implementation
- Multiple related tasks
- Want thorough architecture + fast implementation + comprehensive review
- Can run unattended

**When NOT to use:**
- Task requires clarification
- Exploratory/research work
- Single trivial change (< 5 lines)

## Core Workflow: Multi-Model (Codex + Ralph)

**Automatic execution:** When ralph-orchestrator is invoked, this full workflow executes automatically.

**Architecture:** GPT 5.3 High for planning and code review + Claude Opus 4.6 for fast implementation.

**Rationale:** Developer consensus shows GPT 5.3 excels at "much more thorough" planning and finding "subtle edge cases" in review, while Claude Opus 4.6 excels at fast execution (7-8 min vs 20-26 min) and shipping working code.

### Full Cycle: Refine → Codex Plan → Ralph Implement → Codex Review

**Phase 0: Prompt Refinement**

```python
# Gather user's feature request
user_request = "Add user authentication with JWT and Google OAuth"

# Ask clarifying questions ONLY if unclear
if requires_clarification(user_request):
    answers = AskUserQuestion(questions=[...])
    user_request = incorporate_answers(user_request, answers)

# Detect domain and complexity
domain = detect_domain(user_request, codebase_summary)
constraints = extract_constraints(user_request, codebase_summary)
reasoning_effort = "high"  # Always high - set in ~/.codex/config.toml

# Refactor into optimal Codex prompt (preserving all user nuance)
refined_prompt = f"""Role: Lead Software Architect specializing in {domain}

Context:
- Project: {project_name}
- Tech Stack: {tech_stack}
- Constraints: {constraints}
- Existing Architecture: {codebase_summary}

User Intent (verbatim):
{user_request}

Task: Design the system architecture for: {extract_feature_summary(user_request)}

Output Requirements (Ralph TDD-Style Planning):

## Architecture Overview
1. System Design Summary
   - High-level architecture (Mermaid component diagram)
   - Data flow patterns
   - Integration points with existing systems
   - Technology choices with rationale

2. Component Breakdown
   - Core components with clear responsibilities
   - Component interactions and dependencies
   - API contracts (JSON schema or TypeScript types)
   - Data models with relationships and constraints

3. Risk Analysis & Edge Cases
   - Failure scenarios (network, data, auth, rate limits)
   - Security considerations (auth, encryption, attack surface)
   - Performance implications
   - Migration strategy if modifying existing schemas

## Implementation Plan (TDD Format)

For each implementation step, provide:

### Step N: [Clear Objective]

**Objective:** What we're building and why (one sentence)

**Implementation:**
- Specific files to create/modify
- Concrete code changes (functions, classes, interfaces)
- Configuration or schema updates
- Dependencies or libraries needed

**Test Requirements (DEFINE BEFORE IMPLEMENTING):**
- Unit tests: What specific behavior to test
- Integration tests: What interactions to verify
- Test fixtures or mocks needed
- Acceptance criteria (how to know it works)

**Integration:**
- How this step connects to other components
- What interfaces or contracts it depends on
- What it exposes for future steps

**Demo/Verification:**
- Command to run after implementing
- Expected output or behavior
- How to manually verify correctness

---

4. Implementation Checklist
   - [ ] Step 1: [Description]
   - [ ] Step 2: [Description]
   - [ ] Step 3: [Description]
   - ...

5. Step Dependencies
   - Mermaid flowchart showing which steps must complete before others
   - Identify parallel vs sequential work

6. Estimated Scope
   - Table with: Step | Files Modified | Complexity (Low/Medium/High)

## Ralph Guardrails (CRITICAL)

Your architecture must align with these principles:
- **Fresh context each iteration** - Each build step can be executed independently
- **Verification is mandatory** - Tests/typecheck/lint must pass before moving forward
- **Search before assuming** - Don't assume functionality is missing, verify first
- **Backpressure over prescription** - Design gates that reject bad work (tests fail = stop)
- **Disk is state** - Use files, git, and explicit artifacts for handoff between steps

Format: Structured markdown with Mermaid diagrams and JSON schemas where applicable.

Constraints:
- Follow existing codebase patterns: {existing_patterns}
- Maintain compatibility with: {dependencies}
- Optimize for: {performance_goals}
- {user_specific_constraints}

DO NOT include preambles, status updates, or meta-commentary. Proceed directly to architectural design.
"""
```

**Phase 1: Codex Architectural Planning**

```bash
# Call Codex CLI with refined prompt
# ALWAYS use reasoningEffort="high" for thorough architecture
# Write prompt to temp file to handle multi-line content
cat > /tmp/codex-prompt.txt << 'PROMPT_EOF'
{refined_prompt}
PROMPT_EOF

# Run codex in background to avoid token waste in main context
codex exec -o .ralph/codex-architecture.md -- "$(cat /tmp/codex-prompt.txt)" 2>/dev/null &
CODEX_PID=$!

# Wait for completion (or poll periodically)
wait $CODEX_PID

# Read architecture from file
# Use Read tool on .ralph/codex-architecture.md
```

**Phase 2: Generate PROMPT.md from Codex Architecture**

```python
# Extract tasks from Codex architecture
tasks = extract_implementation_tasks(architecture)

# Analyze task dependencies from Codex architecture
# Group into waves: tasks touching different directories/modules with no shared files = same wave
# Tasks with explicit dependencies or shared files = later wave
waves = group_tasks_into_waves(tasks, architecture)

# Generate PROMPT.md with wave annotations if ≥2 independent tasks exist
Write tool:
  file_path: "PROMPT.md"
  content: f"""# {title}

## Objective
{objective}

## Architecture (from Codex GPT 5.3 High)

{architecture}

## Implementation Tasks
{format_tasks_with_waves(waves)}  # Uses ### Wave N format if parallel, flat list if sequential

## Constraints
- Follow the architectural design above
- Run tests after each component
- Commit after completing each task
- Use meaningful commit messages

## Acceptance Criteria
- All tasks completed per architecture
- Tests passing (unit + integration)
- No linting errors
- Security review passed
- Performance benchmarks met
"""
```

**Phase 3: Execute Ralph Implementation**

**Sequential (no waves in PROMPT.md):**
```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --run --max-iterations 100
```

**Parallel (waves detected in PROMPT.md):**

When PROMPT.md contains `### Wave N` headings, execute independent tasks in parallel using git worktrees + Task subagents:

```python
# Parse waves from PROMPT.md
waves = parse_waves_from_prompt_md("PROMPT.md")

for wave_idx, wave_tasks in enumerate(waves):
    print(f"Wave {wave_idx + 1}/{len(waves)}: {len(wave_tasks)} tasks")

    if len(wave_tasks) == 1:
        # Single task - run in main workspace (standard ralph)
        nohup ralph run -a --continue --max-iterations 30 > .ralph/ralph.log 2>&1 & disown
        # Monitor until completion
    else:
        # Multiple independent tasks - parallel worktrees + subagents
        for task in wave_tasks:
            # 1. Create isolated git worktree
            worktree_path = f".worktrees/wave{wave_idx + 1}-{task.id}"
            git worktree add {worktree_path} HEAD

            # 2. Write single-task PROMPT.md in worktree
            Write(file_path=f"{worktree_path}/PROMPT.md", content=single_task_prompt)

            # 3. Spawn Task subagent to run ralph in worktree
            Task(
                subagent_type="general-purpose",
                description=f"Ralph: {task.title}",
                prompt=f"""Execute ralph in isolated worktree for this task:

**Task:** {task.title}
**Description:** {task.description}
**Workspace:** {worktree_path}

1. Navigate: cd {worktree_path}
2. Verify PROMPT.md contains this single task
3. Run ralph detached:
   nohup ralph run -a --continue --max-iterations 30 > .ralph/ralph.log 2>&1 & disown
4. Monitor: tail -20 .ralph/ralph.log every 2-3 minutes
5. Wait for LOOP_COMPLETE or 60 minute timeout
6. Run tests: {test_command}

Output format:
STATUS: complete | partial | failed
ITERATIONS: [count]
COMMITS: [git log --oneline]
FILES: [modified files list]
TESTS: passing | failing
""",
                run_in_background=False
            )

        # After all wave tasks complete, merge worktrees back
        for task in completed_tasks:
            git merge {worktree_path}  # merge worktree branch into main
            git worktree remove {worktree_path}

    # Run full test suite after wave merge
    run_tests()
```

**Worktree cleanup:** Always remove worktrees after merge (`git worktree remove`), even on failure.

**Merge conflicts:** If merge fails, report conflicting files and fall back to sequential re-implementation of the conflicting task.

**Phase 4: Codex Code Review**

After LOOP_COMPLETE (exit code 0):

```bash
# Get base commit for review scope (adjust N based on implementation commits)
base_commit=$(git rev-parse HEAD~10)

# Run Codex review in background to avoid token waste
codex exec review --base "$base_commit" > .ralph/codex-review.md 2>&1 &
CODEX_PID=$!

# Wait for completion
wait $CODEX_PID

# Read review from file
# Use Read tool on .ralph/codex-review.md
```

**Review output includes:**
1. **Subtle edge cases or bugs** - Does the code handle all scenarios?
2. **Error handling gaps** - Missing try/catch, unhandled errors?
3. **Security vulnerabilities** - Injection, XSS, auth bypass, data leaks?
4. **Performance issues** - N+1 queries, memory leaks, blocking operations?
5. **Maintainability concerns** - Code smells, tight coupling, poor naming?
6. **Test coverage gaps** - Missing test cases, untested paths?
7. **Documentation needs** - Unclear APIs, missing comments for complex logic?
8. **Architectural deviations** - Did implementation follow the plan?

### Codex CLI Reference (v0.98.0)

**ALWAYS use Codex CLI directly** (no MCP). This avoids timeout issues and provides more control.

**If unsure about available options, run `codex exec --help` or `codex exec review --help` first.**

**CRITICAL: Required config.toml settings**

Codex config at `~/.codex/config.toml` MUST have:
```toml
model = "gpt-5.3-codex"
model_reasoning_effort = "high"
```

These are inherited by all `codex exec` and `codex exec review` calls. No need to pass on every invocation.

**CRITICAL: Non-Interactive Execution**

Always use `codex exec` (not bare `codex`) for non-interactive use. Use `-o FILE` to capture the final response to a file instead of stdout.

```bash
# ✓ CORRECT - Non-interactive with file output, background execution
codex exec -o .ralph/codex-output.md -- "prompt" 2>/dev/null &
wait $!
# Then use Read tool on .ralph/codex-output.md

# ❌ WRONG - bare `codex` opens interactive TUI
codex "prompt"

# ❌ WRONG - `-q` flag does not exist
codex -q "prompt"

# ❌ WRONG - `reasoningEffort` is not a valid config key
codex exec -c 'reasoningEffort="high"' -- "prompt"
# ✓ CORRECT config key (if you need to override config.toml)
codex exec -c model_reasoning_effort="high" -- "prompt"
```

**CLI Syntax:**
```bash
# Planning/prompts - use `codex exec` for non-interactive
codex exec -o .ralph/codex-plan.md -- "Your prompt here" 2>/dev/null & wait $!

# Code review - use `codex exec review` for non-interactive (no -o, use redirect)
codex exec review --base HEAD~10 > .ralph/codex-review.md 2>&1 & wait $!

# Review uncommitted changes
codex exec review --uncommitted > .ralph/codex-review.md 2>&1 & wait $!

# Review specific commit
codex exec review --commit abc123 > .ralph/codex-review.md 2>&1 & wait $!
```

**Available CLI Options:**

| Command | Option | Description |
|---------|--------|-------------|
| `codex exec` | `"prompt"` | Non-interactive prompt (positional arg) |
| `codex exec` | `-o FILE` | Write final response to file |
| `codex exec` | `-m MODEL` | Override model (default from config.toml) |
| `codex exec` | `-c key=value` | Config override (e.g., `model_reasoning_effort="high"`) |
| `codex exec` | `-s SANDBOX` | Sandbox mode: `read-only`, `workspace-write`, `danger-full-access` |
| `codex exec` | `--full-auto` | Convenience: `-a on-request --sandbox workspace-write` |
| `codex exec` | `-C DIR` | Working directory |
| `codex exec review` | `--base <ref>` | Review changes against base branch/commit |
| `codex exec review` | `--commit <sha>` | Review specific commit |
| `codex exec review` | `--uncommitted` | Review staged/unstaged changes |
| `codex exec review` | `--title <text>` | Title for review summary |
| `codex exec review` | `-m MODEL` | Override model |

**NOTE:** `codex exec review` does NOT have `-o`. Use shell redirect: `> file 2>&1`

**Multi-line prompts (use temp file or stdin):**
```bash
# Option A: Temp file with command substitution
cat > /tmp/codex-prompt.txt << 'EOF'
Your multi-line
prompt here
EOF
codex exec -o .ralph/codex-output.md -- "$(cat /tmp/codex-prompt.txt)" 2>/dev/null & wait $!

# Option B: Stdin (use - as prompt arg)
codex exec -o .ralph/codex-output.md -- - < /tmp/codex-prompt.txt 2>/dev/null & wait $!
```

**Common errors:**
| Error | Cause | Fix |
|-------|-------|-----|
| `unexpected argument '-q'` | `-q` flag doesn't exist | Use `codex exec "prompt"` |
| `unknown config key 'reasoningEffort'` | Wrong key name | Use `model_reasoning_effort` |
| TUI opens instead of running | Used bare `codex` | Use `codex exec` |
| Empty output file | Model config missing | Check `~/.codex/config.toml` has model + reasoning |

**Phase 5: Issue Resolution (parallel fixes from Codex review)**

After Codex review completes, parse findings and fix issues. Independent issues (different files) run in parallel via Task subagents. Each subagent receives the **full Codex review finding** for its issue.

**Step 1: Parse and categorize review findings**

```python
# Read Codex review output
review = Read(file_path=".ralph/codex-review.md")

# Parse findings into structured issues
# Each finding has: file, line, severity, category, description, suggested_fix
findings = parse_codex_review(review)

# Categorize by file independence
by_file = {}
for finding in findings:
    by_file.setdefault(finding.file, []).append(finding)

# Independent: files with single issue (can parallelize)
independent = [issues[0] for f, issues in by_file.items() if len(issues) == 1]
# Dependent: files with multiple issues (must serialize)
dependent = [issue for f, issues in by_file.items() if len(issues) > 1 for issue in issues]
```

**Step 2: Spawn parallel fix subagents (≥2 independent issues)**

```python
if len(independent) >= 2:
    # Spawn parallel Task subagents
    for finding in independent:
        Task(
            subagent_type="general-purpose",
            description=f"Fix {finding.severity} in {finding.file}",
            prompt=f"""Fix this issue identified by Codex GPT 5.3 High code review.

## Codex Review Finding (AUTHORITATIVE - this is what needs fixing)

**File:** {finding.file}:{finding.line}
**Severity:** {finding.severity}
**Category:** {finding.category}
**Description:** {finding.description}
**Suggested Fix:** {finding.suggested_fix}

## Instructions

1. **Read the file:**
   Read(file_path="{finding.file}")

2. **Understand the issue:**
   - Locate line {finding.line} and surrounding context
   - Understand why the Codex review flagged this
   - Understand the suggested fix

3. **Apply the fix:**
   - Follow the Codex review's suggested fix as the primary approach
   - Use Edit tool to apply changes
   - Maintain existing code style and conventions

4. **If the suggested fix is unclear or insufficient:**
   - Search for working examples: mcp__exa__get_code_context_exa(query="{finding.category} {language} fix example")
   - Check official docs: mcp__Ref__ref_search_documentation(query="{finding.category} best practices")
   - Apply the pattern learned from examples/docs
   NOTE: Only use Exa/Ref if the Codex review's suggested fix is ambiguous or doesn't resolve the issue.

5. **Run tests:**
   Bash(command="{test_command}")

6. **Report result:**

If fixed:
```
STATUS: fixed
FILE: {finding.file}
CHANGES: [1-2 sentence description]
TESTS: [passing count]
RESEARCH_USED: none | exa | ref | both
```

If failed:
```
STATUS: failed
FILE: {finding.file}
ERROR: [what went wrong]
BLOCKER: [why couldn't fix]
```
""",
            run_in_background=False
        )
else:
    # <2 independent issues - fix all sequentially in main thread
    fix_sequentially(findings)
```

**Step 3: Fix dependent issues sequentially**

```python
# Issues in same file must be fixed sequentially to avoid conflicts
for finding in dependent:
    # Same fix logic as subagent prompt, but in main thread
    # Read file → apply Codex suggested fix → test
    # Escalate to Exa/Ref only if fix fails
```

**Step 4: Run full test suite after all fixes**

```bash
# Verify all fixes work together
{test_command}
```

**Exa/Ref escalation (conditional):**
- Exa/Ref are NOT mandatory research steps
- Use them ONLY when the Codex review's suggested fix is:
  - Ambiguous (review says "consider using X" without specifics)
  - Insufficient (applied fix but tests still fail)
  - Missing (review identifies problem but doesn't suggest solution)
- When escalating:
  - **Exa**: `mcp__exa__get_code_context_exa(query="working example {pattern} {language}")` for battle-tested code
  - **Ref**: `mcp__Ref__ref_search_documentation(query="{framework} {api} documentation")` for canonical docs

**Example parallel fix execution:**

```
Codex review finds 4 issues:
  1. auth.ts:47 - SQL injection (CRITICAL) - "Use parameterized queries"
  2. api.ts:89 - Missing rate limit (HIGH) - "Add express-rate-limit middleware"
  3. db.ts:23 - N+1 query (HIGH) - "Use DataLoader or eager loading"
  4. utils.ts:12 - Logging leak (MEDIUM) - "Redact PII fields before logging"

All in different files → 4 parallel Task subagents

Subagent 1: Read auth.ts → apply parameterized queries (clear fix, no Exa/Ref needed) → test ✓
Subagent 2: Read api.ts → apply rate limit (unclear middleware setup) → Ref lookup → apply → test ✓
Subagent 3: Read db.ts → apply DataLoader (need example) → Exa lookup → apply → test ✓
Subagent 4: Read utils.ts → add PII redaction (clear fix) → test ✓

Duration: ~8 min parallel (vs ~25 min sequential)
Exa/Ref used: 2 of 4 subagents (only where needed)
```

### Rate Limit Strategy

**Assumptions:**
- Claude Max $100/month → High Opus 4.6 limits (abundant)
- Codex $20/month → Medium GPT 5.3 High limits (~50 requests/day)

**Usage per feature:**
- Planning: 1 Codex request
- Review: 1 Codex request
- Implementation: Unlimited Claude (ralph run)

**Result:** ~25 plan+implement+review cycles per day

### What Happens Automatically

**Prompt Refinement Phase (always executed):**
- Analyzes user's feature request for clarity
- Asks clarifying questions only if genuinely unclear
- Refactors user request into optimal Codex planning prompt
- Preserves all user intent, nuance, and technical choices
- Selects appropriate reasoning effort (medium/high/xhigh)

**Codex Planning Phase (always executed):**
- Receives refined, optimized prompt
- Analyzes feature requirements with appropriate reasoning depth
- Designs system architecture using systems-first approach
- Identifies components and interactions
- Plans implementation sequence
- Considers edge cases and security

**Ralph Implementation Phase (always executed):**
- Claude Opus 4.6 executes via orchestrate.py
- Fast iteration (7-8 min typical)
- Ships working code consistently
- Commits after each task
- **If PROMPT.md has wave format:** Independent task waves run in parallel via git worktrees + Task subagents (30-50% speedup on implementation phase)

**Codex Review Phase (always executed, single sequential call):**
- Analyzes implementation for edge cases
- Checks security vulnerabilities
- Validates error handling
- Reviews test coverage
- Assesses maintainability
- Provides severity-rated findings

**Issue Resolution Phase (always executed after review):**
- Parses Codex review findings into structured issues
- Categorizes by file independence (same file = sequential, different files = parallel)
- **≥2 independent issues:** Spawns parallel Task subagents, each receiving full Codex review finding
- Each subagent applies the Codex-suggested fix directly
- **Exa/Ref research is conditional** - only used when Codex suggested fix is ambiguous, insufficient, or missing
- Runs full test suite after all fixes applied

### Example: Full Multi-Model Cycle

```bash
# 1. User describes feature
User: "Add rate limiting to our API endpoints"

# 2. Claude calls Codex CLI for architecture (background, file output)
mkdir -p .ralph
codex exec -o .ralph/codex-architecture.md -- "ARCH_PROMPT" 2>/dev/null & wait $!
# Read .ralph/codex-architecture.md
# Contains: Token bucket algorithm, Redis backing store, middleware pattern,
# rate limit configs, error responses, monitoring

# 3. Claude generates PROMPT.md with architecture + tasks (wave format if applicable)
# If Codex architecture shows independent modules:
#   Wave 1: Rate limit middleware, Redis store, Config loader (parallel)
#   Wave 2: Integration + monitoring (depends on Wave 1)
# Otherwise: flat task list (sequential)

# 4. Claude executes Ralph
# Sequential: python orchestrate.py --run --max-iterations 100
# Parallel waves: spawn Task subagents per wave with worktrees
# Wave 1: 3 parallel worktrees (middleware, store, config)
# Wave 2: sequential (depends on wave 1 merge)

# 5. Ralph completes (LOOP_COMPLETE)
Exit code 0, all tasks done

# 6. Claude calls Codex CLI for review (single sequential call, background)
codex exec review --base HEAD~10 > .ralph/codex-review.md 2>&1 & wait $!
# Read .ralph/codex-review.md
# Contains: Found edge case - rate limit doesn't reset on server restart,
# Missing test for concurrent requests, Redis connection error handling needed

# 7. Fix issues from review (parallel if in different files)
# Parse review: 3 issues in 3 different files → spawn 3 parallel fix subagents
# Subagent 1: Fix rate limit persistence (Codex suggested Redis SAVE config) → apply directly
# Subagent 2: Add concurrency tests (Codex suggested test patterns) → apply directly
# Subagent 3: Fix Redis error handling (ambiguous suggestion) → Ref lookup → apply
# All 3 complete in ~8 min vs ~20 min sequential

# 8. Run full test suite → all passing
# Report: "Fixed 3 review issues (2 direct, 1 with Ref docs). All tests passing."
```

## Execution from Claude Code

### CRITICAL: Timeout Behavior

**Claude Code's Bash tool has timeouts that WILL kill long-running processes:**

| Method | Timeout | Use Case |
|--------|---------|----------|
| `Bash` tool (default) | 5 min | Quick commands |
| `Bash` tool with `timeout: 600000` | 10 min | Medium tasks |
| `run_in_background: true` | Still has timeout | NOT suitable for ralph loops |
| `nohup ... & disown` | NO timeout | **Required for ralph loops** |

### Running Ralph Loops (Correct Way)

**ALWAYS use `nohup` + `disown` for ralph loops:**

```bash
# Start ralph detached (survives timeouts and disconnects)
nohup ralph run -a --continue --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
echo "PID: $!"

# Monitor progress
tail -f .ralph/ralph.log
```

**❌ WRONG - Will get killed:**
```bash
# These will timeout after 5-10 minutes
ralph run --max-iterations 100
python orchestrate.py --run --max-iterations 100
```

**✓ CORRECT - Detached execution:**
```bash
nohup ralph run -a --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
```

### Monitoring Detached Processes

```bash
# Watch live output
tail -f .ralph/ralph.log

# Check if still running
ps aux | grep ralph | grep -v grep

# Check latest output
tail -50 .ralph/ralph.log

# Check git progress (what's been committed)
git log --oneline -10
```

### Stopping a Detached Process

```bash
# Find and kill
kill $(pgrep -f "ralph run")

# Or by PID if you saved it
kill <PID>
```

## Troubleshooting

### "Too many consecutive failures"

**Symptom:** Ralph terminates with "consecutive_failures" after several rapid iterations (~1 second each).

**Cause:** Claude API rate limiting between consecutive requests. Each iteration completes in ~1 second without actually invoking the Claude agent.

**Root cause confirmed:** When ralph runs multiple iterations back-to-back, the Claude API may reject rapid consecutive requests. Adding a 60-second delay between iterations resolves this.

**Solution:** Use the loop runner script with delays (see below).

**Debug steps:**

1. **Run single iteration with verbose output:**
```bash
nohup ralph run -a --continue --max-iterations 1 --verbose > .ralph/debug.log 2>&1 & disown
tail -f .ralph/debug.log
```

2. **Check what was happening:**
```bash
# Ralph's scratchpad shows current state
cat .ralph/agent/scratchpad.md

# Event history
ralph events

# Task list
ralph tools task ready
```

3. **If debug iteration succeeds:** The original failure was transient. Resume normally:
```bash
nohup ralph run -a --continue --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
```

### Output Truncation

**❌ NEVER use `| head -N` when capturing ralph output:**
```bash
# BAD - truncates output, can't see actual errors
ralph run --verbose 2>&1 | head -100
```

**✓ ALWAYS capture full output to file:**
```bash
# GOOD - full output preserved
nohup ralph run -a --verbose > .ralph/debug.log 2>&1 & disown
```

### Resuming After Failure

```bash
# Continue from where it left off (preserves scratchpad, tasks, memories)
nohup ralph run -a --continue --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
```

### Checking Progress

```bash
# Completed tasks
ralph tools task list | grep -v "^ID"

# Git commits made
git log --oneline -10

# Current iteration state
cat .ralph/agent/scratchpad.md

# Ralph's learned patterns
cat .ralph/agent/memories.md
```

### Environment Diagnostics

When troubleshooting, run `ralph doctor` first for a full environment health check:

```bash
ralph doctor
```

Reports backend availability, config validity, tool versions, and common misconfigurations.

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Process killed mid-iteration | Claude Code timeout | Use `nohup ... & disown` |
| TUI errors in background | No terminal for TUI | Add `-a` (autonomous/headless mode) |
| "consecutive_failures" | API rate limiting | Use loop script with 60s+ delays |
| Intermittent failures even with delays | Accumulated rate limit state | Script auto-doubles delay after failures |
| Can't see errors | Output truncated | Don't use `| head`, capture to file |
| Loop stuck | Iteration taking too long | Check `tail -f .ralph/ralph.log` |
| Tasks not progressing | Previous iteration incomplete | `ralph run -a --continue` |
| Unknown environment issue | Misconfiguration | Run `ralph doctor` for diagnostics |

### Verifying Claude is Being Invoked

If iterations complete in <10 seconds without output, Claude may not be starting:

```bash
# Check process tree while ralph is running
pstree -p $(pgrep -f "ralph run") | head -20

# Should show: ralph → claude → (MCP servers, docker, etc.)
# If no claude subprocess, the API call is failing silently
```

## Loop Runner Script (Recommended)

For reliable multi-iteration runs, use a loop script with delays between iterations:

```bash
#!/bin/bash
# scripts/ralph-loop.sh - Ralph loop with rate limit protection
# Usage: ./scripts/ralph-loop.sh [max_iterations] [delay_seconds]

MAX_ITERATIONS=${1:-20}
DELAY=${2:-60}  # 60 second delay to avoid API rate limits
LOG_DIR=".ralph/loop-logs"
CONSECUTIVE_FAILURES=0
MAX_CONSECUTIVE_FAILURES=3

mkdir -p "$LOG_DIR"

echo "=== Ralph Loop Runner ==="
echo "Max iterations: $MAX_ITERATIONS | Delay: ${DELAY}s"

for i in $(seq 1 $MAX_ITERATIONS); do
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    LOG_FILE="$LOG_DIR/iteration-$i-$TIMESTAMP.log"

    echo "[$TIMESTAMP] Starting iteration $i/$MAX_ITERATIONS..."
    rm -f .ralph/loop.lock

    START=$(date +%s)
    ralph run -a --continue --max-iterations 1 > "$LOG_FILE" 2>&1
    DURATION=$(($(date +%s) - START))

    if [ $DURATION -lt 10 ]; then
        echo "  ⚠ Iteration completed too quickly (${DURATION}s) - likely failed"
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))

        if [ $CONSECUTIVE_FAILURES -ge $MAX_CONSECUTIVE_FAILURES ]; then
            echo "  ✗ $MAX_CONSECUTIVE_FAILURES consecutive failures - doubling delay"
            DELAY=$((DELAY * 2))
            CONSECUTIVE_FAILURES=0
        fi
    else
        echo "  ✓ Iteration completed in ${DURATION}s"
        CONSECUTIVE_FAILURES=0
        git log --oneline -1
    fi

    # Check for completion
    grep -q "LOOP_COMPLETE" "$LOG_FILE" 2>/dev/null && echo "=== LOOP_COMPLETE ===" && break

    [ $i -lt $MAX_ITERATIONS ] && echo "  Waiting ${DELAY}s..." && sleep $DELAY
done

echo -e "\n=== Summary ===" && git log --oneline -10
```

**Usage:**
```bash
chmod +x scripts/ralph-loop.sh
nohup ./scripts/ralph-loop.sh 20 60 > .ralph/loop-runner.log 2>&1 & disown
tail -f .ralph/loop-runner.log  # Monitor progress
```

**Why 60 seconds?** The Claude API rate limits consecutive requests. Testing shows 60s is sufficient cooldown, but the script auto-doubles delay after 3 consecutive failures.

**Observed iteration times:**
- Failed iterations: 0-1 seconds (API rejected)
- Successful iterations: 3-8 minutes (actual work)

## Dependencies

- `ralph-orchestrator` CLI: `npm install -g @ralph-orchestrator/ralph-cli`
- `codex` CLI: Required for multi-model workflow (planning + review)
- Python 3.8+
- Git repository with commits
