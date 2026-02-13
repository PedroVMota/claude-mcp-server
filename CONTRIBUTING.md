# Contributing to claude-mcp-server

Thank you for your interest in contributing. This guide covers the development workflow, conventions, and standards for this project.

## Getting Started

```bash
# Fork and clone the repository
git clone https://github.com/<your-username>/claude-mcp-server.git
cd claude-mcp-server

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests to verify your setup
pytest tests/ -v
```

**Requirements:** Python 3.11+

## Development Workflow

We use a modified GitHub Flow with `dev` as the integration branch and `main` as the production branch. See [Branching Strategy](docs/branching-strategy.md) for full details.

```bash
# 1. Create a feature branch from dev
git checkout dev && git pull origin dev
git checkout -b feature/my-feature

# 2. Make changes and commit
git add <files>
git commit -m "feat(scope): add new feature"

# 3. Push and open a PR to dev
git push -u origin feature/my-feature
gh pr create --fill --base dev
```

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

### Rules

- Subject line: imperative mood, lowercase, no period, max 72 characters.
- Body: explain motivation and contrast with previous behavior.
- Reference issues: `Closes #123`, `Fixes #456`.
- **One logical change per commit.**

### Examples

```
feat(server): add health check endpoint
fix(auth): resolve token expiration race condition
chore(deps): bump cryptography to 43.x
docs(readme): add setup instructions for local development
```

## Pull Request Process

### Every PR must include

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
- All CI checks must pass.
- Use **squash merge** for feature branches.
- PR author merges after approval.

### Size Guidelines

| Size | Lines Changed | Expectation |
|------|---------------|-------------|
| XS | < 50 | Quick review |
| S | 50-200 | Standard review |
| M | 200-500 | Detailed review, consider splitting |
| L | 500+ | Must justify why it can't be split |

## Code Style

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

### Principles

- **Readability over cleverness.**
- **Keep it simple.** Don't over-engineer.
- **DRY, but not at the cost of clarity.** Three similar lines are better than a premature abstraction.
- **Fail fast.** Validate inputs at boundaries.
- **No dead code.** If it's unused, delete it.

## Testing

- Every new feature or bug fix **must** include tests.
- Tests live in `tests/` mirroring the `src/` structure.
- Test file naming: `test_<module>.py` (e.g., `test_crypto.py`).
- Use the **Arrange-Act-Assert** (AAA) pattern.
- Use descriptive test names: `test_should_return_error_when_no_token_stored`.
- No test interdependence — each test runs in isolation.
- Mock external dependencies, not internal logic.

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_crypto.py -v
```

## Issue Labels

| Label | Purpose |
|-------|---------|
| `bug` | Something is broken |
| `feature` | New functionality |
| `enhancement` | Improvement to existing feature |
| `docs` | Documentation work |
| `good first issue` | Beginner-friendly |
| `priority:high` | Needs immediate attention |
| `priority:low` | Nice to have |

## Security

- **Never commit secrets** — no API keys, tokens, or credentials in code.
- Use environment variables for sensitive configuration.
- See [Security Documentation](docs/security.md) for the token encryption model.
