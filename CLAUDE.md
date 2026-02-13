# CLAUDE.md — Repository Rules & Workflow

> This file defines the development standards, Git workflows, and conventions for the **claude-mcp-server** project. All contributors — human and AI — must follow these rules.

---

## Project Overview

**claude-mcp-server** is an MCP (Model Context Protocol) server for managing Claude repositories. This document establishes the engineering culture and guardrails for the project from day one.

---

## Branching Strategy

We follow **GitHub Flow** — a simple, trunk-based model.

| Branch | Purpose | Lifetime |
|--------|---------|----------|
| `main` | Production-ready code. Always deployable. | Permanent |
| `dev` | Integration/staging. Version bumps happen here. | Permanent |
| `feature/*` | New features | Short-lived |
| `fix/*` | Bug fixes | Short-lived |
| `chore/*` | Maintenance, deps, config | Short-lived |
| `docs/*` | Documentation changes | Short-lived |
| `claude/*` | AI-assisted development branches | Short-lived |

### Rules

- **Never push directly to `main` or `dev`.** All changes go through Pull Requests.
- Feature branches are created from `dev` and merged back via PR.
- `dev` is promoted to `main` for production releases.
- Delete branches after merge — keep the repo clean.
- Rebase feature branches on `dev` before opening a PR to keep history linear.

---

## Commit Conventions

We use **Conventional Commits** (`<type>(<scope>): <description>`).

### Types

| Type | When to use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring, no behavior change |
| `test` | Adding or updating tests |
| `chore` | Build config, tooling, dependencies |
| `perf` | Performance improvements |
| `ci` | CI/CD pipeline changes |
| `revert` | Reverting a previous commit |

### Format

```
<type>(<scope>): <short summary>

<optional body — explain WHY, not WHAT>

<optional footer — breaking changes, issue refs>
```

### Examples

```
feat(server): add health check endpoint
fix(auth): resolve token expiration race condition
chore(deps): bump cryptography to 43.x
docs(readme): add setup instructions for local development
```

### Rules

- Subject line: imperative mood, lowercase, no period, max 72 characters.
- Body: wrap at 100 characters. Explain motivation and contrast with previous behavior.
- Reference issues: `Closes #123`, `Fixes #456`, `Refs #789`.
- **One logical change per commit.** Don't mix a feature and a refactor.

---

## Pull Request Workflow

### Opening a PR

Every PR must include:

1. **Title** — follows commit convention format (`feat(scope): summary`)
2. **Summary** — 1-3 bullet points of what changed and why
3. **Test Plan** — how the changes were verified
4. **Issue Reference** — link the related issue (`Closes #N`)

### PR Template

```markdown
## Summary
- <what changed and why>

## Changes
- <list of specific changes>

## Test Plan
- [ ] Unit tests pass
- [ ] Manual testing done
- [ ] No regressions introduced

## Related Issues
Closes #<issue-number>
```

### Review Rules

- **Minimum 1 approval** required before merge.
- All CI checks must pass (lint, test, build).
- Address all review comments — resolve or discuss, never ignore.
- Use **squash merge** for feature branches to keep `main` history clean.
- PR author merges after approval (not the reviewer).

### PR Size Guidelines

| Size | Lines Changed | Expectation |
|------|---------------|-------------|
| XS | < 50 | Quick review |
| S | 50–200 | Standard review |
| M | 200–500 | Detailed review, consider splitting |
| L | 500+ | Must justify why it can't be split |

Keep PRs small and focused. Large PRs slow down reviews and increase risk.

---

## Issue Management

### Labels

| Label | Color | Purpose |
|-------|-------|---------|
| `bug` | Red | Something is broken |
| `feature` | Green | New functionality |
| `enhancement` | Blue | Improvement to existing feature |
| `docs` | Purple | Documentation work |
| `good first issue` | Teal | Beginner-friendly |
| `priority:high` | Orange | Needs immediate attention |
| `priority:low` | Gray | Nice to have |
| `wontfix` | White | Decided against |
| `duplicate` | Yellow | Already tracked |

### Issue Lifecycle

1. **Open** — issue is created with clear description and reproduction steps (for bugs)
2. **Triaged** — labeled and assigned to a milestone
3. **In Progress** — someone is actively working on it (linked PR exists)
4. **In Review** — PR is open and under review
5. **Closed** — merged and deployed, or resolved as won't fix

---

## Code Standards

### General Principles

- **Readability over cleverness.** Code is read far more than it is written.
- **Keep it simple.** Don't over-engineer. Solve the problem at hand.
- **DRY, but not at the cost of clarity.** Three similar lines are better than a premature abstraction.
- **Fail fast.** Validate inputs at boundaries. Let errors surface early.
- **No dead code.** If it's unused, delete it. Git remembers.

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | `snake_case` | `token_service.py` |
| Classes | `PascalCase` | `SetTokenInput` |
| Functions | `snake_case` | `handle_set_github_token()` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_TOKEN_DIR` |
| Variables | `snake_case` | `token_path` |
| Types/Models | `PascalCase` | `CreateRepoInput` |
| Env variables | `UPPER_SNAKE_CASE` | `MCP_ENCRYPTION_KEY` |

### File Organization

```
.
├── src/                  # Application source code
│   ├── main.py           # Entry point
│   ├── server.py         # FastMCP server + tool definitions
│   ├── handlers/         # Request handlers
│   │   └── repo_handler.py
│   ├── services/         # Business logic
│   │   ├── github_service.py
│   │   └── token_service.py
│   ├── utils/            # Shared utilities
│   │   └── crypto.py
│   └── types/            # Pydantic models
│       └── models.py
├── tests/                # Test files (mirrors src/ structure)
├── docs/                 # Additional documentation
├── .github/              # GitHub config (workflows, templates)
│   └── workflows/        # CI/CD pipelines
├── pyproject.toml        # Project configuration
├── requirements.txt      # Runtime dependencies
├── Dockerfile            # Multi-stage Docker build
├── CLAUDE.md             # This file
├── CONTRIBUTING.md        # Contributing guide
└── README.md
```

---

## Testing Standards

### Rules

- Every new feature or bug fix **must** include tests.
- Tests live in `tests/` mirroring the `src/` structure.
- Test file naming: `test_<module>.py` (e.g., `test_crypto.py`).
- Aim for meaningful coverage, not 100% line coverage.

### Test Pyramid

| Level | What | Speed | Quantity |
|-------|------|-------|----------|
| Unit | Individual functions/classes | Fast | Many |
| Integration | Module interactions | Medium | Some |
| E2E | Full workflows | Slow | Few |

### Conventions

- Use descriptive test names: `should return 404 when resource not found`
- Arrange-Act-Assert (AAA) pattern in every test
- No test interdependence — each test runs in isolation
- Mock external dependencies, not internal logic

---

## CI/CD Expectations

Every PR triggers the following pipeline:

### Gates (must all pass to merge)

1. **Unit Tests** — all tests green (`pytest tests/ -v`)

### Additional (when configured)

- **Lint** — code style and static analysis
- **Type Check** — static type checking
- **Integration Tests** — on merge to `main`
- **Security Scan** — dependency vulnerability check
- **Coverage Report** — posted as PR comment

### Pipeline Principles

- **Fast feedback** — pipeline should complete in under 5 minutes.
- **No flaky tests** — fix or remove them immediately.
- **Pipeline as code** — all CI config lives in `.github/workflows/`.

---

## Security Practices

### Secrets

- **Never commit secrets** — no API keys, tokens, passwords, or credentials in code.
- Use environment variables for all sensitive configuration.
- Use `.env` files locally (already in `.gitignore`).
- Use GitHub Secrets for CI/CD.

### Dependencies

- Review dependency changes carefully in PRs.
- Keep dependencies up to date — schedule regular updates.
- Prefer well-maintained packages with active communities.
- Run `pip audit` (or equivalent) regularly.

### Code Review Security Checklist

- [ ] No hardcoded secrets or credentials
- [ ] Input validation at all external boundaries
- [ ] No SQL injection, XSS, or command injection vectors
- [ ] Authentication/authorization checks in place
- [ ] Sensitive data not logged or exposed in errors
- [ ] Dependencies are from trusted sources

---

## AI Assistant Guidelines

When an AI assistant (Claude, Copilot, etc.) works in this repository:

### Do

- Read existing code before making changes — understand context first.
- Follow all conventions in this file — commit messages, naming, structure.
- Write tests for any new code.
- Keep changes minimal and focused on the task.
- Use existing patterns and utilities — don't reinvent.
- Explain reasoning in PR descriptions and commit bodies.

### Don't

- Push directly to `main` or `dev`.
- Create files that aren't necessary for the task.
- Add comments, docstrings, or type annotations to code you didn't change.
- Over-engineer solutions or add speculative features.
- Ignore failing tests or lint errors.
- Make assumptions — ask when requirements are unclear.
- Introduce new dependencies without justification.

### Workflow for AI

1. **Understand** — read relevant files, explore the codebase.
2. **Plan** — think through the approach before writing code.
3. **Implement** — make focused, minimal changes.
4. **Verify** — run tests, lint, and build.
5. **Commit** — use conventional commit format.
6. **PR** — open with clear summary and test plan.

---

## Quick Reference

```bash
# Branch off dev
git checkout dev && git pull origin dev
git checkout -b feature/my-feature

# Make changes, then commit
git add <files>
git commit -m "feat(scope): add new feature"

# Push and open PR to dev
git push -u origin feature/my-feature
# Open PR via GitHub UI or: gh pr create --fill --base dev

# After approval, squash merge via GitHub
```

---

*Last updated: 2026-02-13*
