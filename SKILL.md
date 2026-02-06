---
name: ralph-orchestrator
description: Autonomous E2E development with automatic multi-model workflow - Codex GPT 5.3 High (architecture + review) + Ralph/Claude Opus 4.5 (implementation). When invoked, automatically executes full cycle - planning, implementation, review. If fixes fail, escalates to Exa MCP (code examples) + Ref MCP (docs). Use when user requests "run ralph", "implement this autonomously", or wants complete feature development with quality analysis.
allowed-tools: Bash(ralph*), Bash(python*), Bash(codex*), Read, Write, Edit, Glob, grepai_search, grepai_trace_callers, grepai_trace_callees, grepai_trace_graph, mcp__exa__get_code_context_exa, mcp__exa__web_search_exa, mcp__Ref__ref_search_documentation, mcp__Ref__ref_read_url
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

```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --run
```

Or combined:
```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --plan "description" --run
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --generate --title "..." --tasks "..." --run
```

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
1. **Codex Planning** - GPT 5.3 High generates thorough architecture
2. **PROMPT Generation** - Extract tasks from architecture
3. **Ralph Implementation** - Claude Opus 4.5 executes via orchestrate.py
4. **Codex Review** - GPT 5.3 High analyzes implementation for edge cases
5. **Issue Resolution** (if fixes fail) - Exa MCP (code examples) + Ref MCP (docs)
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
Run: codex -q "REFINED_PROMPT" -c 'reasoningEffort="high"' > .ralph/codex-architecture.md 2>&1 & wait $!
Read: .ralph/codex-architecture.md
  → Contains architecture with sliding window implementation, Redis schema, middleware design

# Phase 2: PROMPT Generation
Generate PROMPT.md from Codex architecture

# Phase 3: Ralph Implementation
Run: python orchestrate.py --run --max-iterations 100
  → Claude implements based on architecture

# Phase 4: Codex Review (background execution)
Run: codex review --base HEAD~N -c 'reasoningEffort="high"' > .ralph/codex-review.md 2>&1 & wait $!
Read: .ralph/codex-review.md
  → Finds edge case: rate limit doesn't reset on server restart
  → Suggests: Redis persistence config + startup validation

# Phase 5: Apply fixes or escalate if needed

# Phase 6: Report
Complete implementation with review findings

# Result: User's nuanced request preserved (sliding window, Redis, per-API-key)
# Optimized prompt structure improved Codex planning quality
# Uses: 2 Codex requests (planning + review), abundant Claude for implementation
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
   - Calls Codex for architectural planning with refined prompt
   - Generates PROMPT.md from architecture
   - Runs ralph implementation (Claude Opus 4.5)
   - Calls Codex for code review
   - **If fixes fail:** Escalates to Exa (code examples) + Ref (docs)
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

**Architecture:** GPT 5.3 High for planning and code review + Claude Opus 4.5 for fast implementation.

**Rationale:** Developer consensus shows GPT 5.3 excels at "much more thorough" planning and finding "subtle edge cases" in review, while Claude Opus 4.5 excels at fast execution (7-8 min vs 20-26 min) and shipping working code.

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
reasoning_effort = determine_complexity(user_request)  # medium/high/xhigh

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
codex -q "$(cat /tmp/codex-prompt.txt)" -c 'reasoningEffort="high"' > .ralph/codex-architecture.md 2>&1 &
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

# Generate PROMPT.md
Write tool:
  file_path: "PROMPT.md"
  content: f"""# {title}

## Objective
{objective}

## Architecture (from Codex GPT 5.3 High)

{architecture}

## Implementation Tasks
{tasks}

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

```bash
python ~/.claude/skills/ralph-orchestrator/scripts/orchestrate.py --run --max-iterations 100
```

**Phase 4: Codex Code Review**

After LOOP_COMPLETE (exit code 0):

```bash
# Get base commit for review scope (adjust N based on implementation commits)
base_commit=$(git rev-parse HEAD~10)

# Run Codex review in background to avoid token waste
codex review --base "$base_commit" -c 'reasoningEffort="high"' > .ralph/codex-review.md 2>&1 &
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

### Codex CLI Reference

**ALWAYS use Codex CLI directly** (no MCP). This avoids timeout issues and provides more control.

**If unsure about available options, run `codex --help` or `codex review --help` first.**

**CRITICAL: Background Execution for Token Efficiency**

Always run Codex in background with output to file, then read the file. This avoids wasting tokens by streaming large outputs into the main context.

```bash
# ✓ CORRECT - Background with file output
codex -q "prompt" -c 'reasoningEffort="high"' > .ralph/codex-output.md 2>&1 &
wait $!
# Then use Read tool on .ralph/codex-output.md

# ❌ WRONG - Output streams into context, wastes tokens
codex -q "prompt" -c 'reasoningEffort="high"'
```

**CLI Syntax:**
```bash
# Planning/prompts - use -q for queries
codex -q "Your prompt here" -c 'reasoningEffort="high"' > .ralph/codex-plan.md 2>&1 & wait $!

# Code review - use review subcommand
codex review --base HEAD~10 -c 'reasoningEffort="high"' > .ralph/codex-review.md 2>&1 & wait $!

# ❌ WRONG - -m flag doesn't exist
codex review --base HEAD~10 -m gpt-5.3
```

**Available CLI Options:**

| Command | Option | Description |
|---------|--------|-------------|
| `codex` | `-q "prompt"` | Run a query/prompt |
| `codex` | `-c 'key=value'` | Config override (model, reasoningEffort, etc.) |
| `codex review` | `--base <ref>` | Review changes against base branch/commit |
| `codex review` | `--commit <sha>` | Review specific commit |
| `codex review` | `--uncommitted` | Review staged/unstaged changes |
| `codex review` | `--title <text>` | Title for review summary |

**Multi-line prompts:**
```bash
# Write prompt to temp file for complex prompts
cat > /tmp/codex-prompt.txt << 'EOF'
Your multi-line
prompt here
EOF

codex -q "$(cat /tmp/codex-prompt.txt)" -c 'reasoningEffort="high"' > .ralph/codex-output.md 2>&1 & wait $!
```

**Phase 5: Issue Resolution (if fixes fail)**

If applying Codex-suggested fixes still results in issues (tests fail, errors persist, integration problems):

**STRONGLY RECOMMENDED: Escalate to targeted external research**

```python
# For code implementation issues - use Exa MCP for working examples
code_examples = mcp__exa__get_code_context_exa(
    query=f"working example {library} {specific_issue} {language}",
    num_results=5
)

# For API/framework questions - use Ref MCP for official docs
documentation = mcp__Ref__ref_search_documentation(
    query=f"{framework} {api_method} documentation"
)

# Apply learned patterns from examples + docs
# Re-run ralph with corrected approach
```

**Why this escalation:**
- Codex review finds WHAT is wrong
- Exa finds HOW others solved it (battle-tested code)
- Ref finds OFFICIAL way to do it (canonical docs)
- Combination provides multiple solution vectors

**Example escalation:**

```
1. Codex review: "HIGH - Redis connection error handling inadequate"
2. Apply fix, still fails with "ECONNREFUSED" in tests
3. Escalate:
   - Exa: "redis node.js connection retry pattern working example"
   - Ref: "ioredis reconnection strategy documentation"
4. Find: Missing reconnectOnError callback + exponential backoff
5. Apply learned pattern, tests pass
```

### Rate Limit Strategy

**Assumptions:**
- Claude Max $100/month → High Opus 4.5 limits (abundant)
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
- Claude Opus 4.5 executes via orchestrate.py
- Fast iteration (7-8 min typical)
- Ships working code consistently
- Commits after each task

**Codex Review Phase (always executed):**
- Analyzes implementation for edge cases
- Checks security vulnerabilities
- Validates error handling
- Reviews test coverage
- Assesses maintainability
- Provides severity-rated findings

**Issue Resolution Phase (executed if fixes fail):**
- **Exa MCP**: Searches for working code examples from real implementations
- **Ref MCP**: Retrieves official documentation for canonical solutions
- Applies learned patterns from examples + docs
- Re-runs implementation with corrected approach
- Escalates from "what's wrong" (Codex) to "how to fix it" (Exa + Ref)

### Example: Full Multi-Model Cycle

```bash
# 1. User describes feature
User: "Add rate limiting to our API endpoints"

# 2. Claude calls Codex CLI for architecture (background, file output)
mkdir -p .ralph
codex -q "ARCH_PROMPT" -c 'reasoningEffort="high"' > .ralph/codex-architecture.md 2>&1 & wait $!
# Read .ralph/codex-architecture.md
# Contains: Token bucket algorithm, Redis backing store, middleware pattern,
# rate limit configs, error responses, monitoring

# 3. Claude generates PROMPT.md with architecture + tasks
Write PROMPT.md with Codex architecture and extracted tasks

# 4. Claude executes Ralph
python orchestrate.py --run --max-iterations 100
# Ralph implements over ~30-50 iterations, commits along the way

# 5. Ralph completes (LOOP_COMPLETE)
Exit code 0, all tasks done

# 6. Claude calls Codex CLI for review (background, file output)
codex review --base HEAD~10 -c 'reasoningEffort="high"' > .ralph/codex-review.md 2>&1 & wait $!
# Read .ralph/codex-review.md
# Contains: Found edge case - rate limit doesn't reset on server restart,
# Missing test for concurrent requests, Redis connection error handling needed

# 7. Claude reports review findings
"Implementation complete. Codex review found 3 issues:
- HIGH: Rate limit state lost on restart (use Redis persistence)
- MEDIUM: Missing concurrency tests
- LOW: Redis error handling could be more robust"

# 8. User decides whether to fix now or create follow-up issues
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
nohup ralph run --continue --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
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
nohup ralph run --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
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
nohup ralph run --continue --max-iterations 1 --verbose > .ralph/debug.log 2>&1 & disown
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
nohup ralph run --continue --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
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
nohup ralph run --verbose > .ralph/debug.log 2>&1 & disown
```

### Resuming After Failure

```bash
# Continue from where it left off (preserves scratchpad, tasks, memories)
nohup ralph run --continue --max-iterations 100 > .ralph/ralph.log 2>&1 & disown
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
| "consecutive_failures" | API rate limiting | Use loop script with 60s+ delays |
| Intermittent failures even with delays | Accumulated rate limit state | Script auto-doubles delay after failures |
| Can't see errors | Output truncated | Don't use `| head`, capture to file |
| Loop stuck | Iteration taking too long | Check `tail -f .ralph/ralph.log` |
| Tasks not progressing | Previous iteration incomplete | `ralph run --continue` |
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
    ralph run --continue --max-iterations 1 > "$LOG_FILE" 2>&1
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
