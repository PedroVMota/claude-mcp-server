# Branching Strategy

This project follows a modified **GitHub Flow** model with two permanent branches (`main` and `dev`) and short-lived feature branches.

## Branch Types

| Branch | Purpose | Lifetime |
|--------|---------|----------|
| `main` | Production-ready code. Always deployable. Triggers production Docker release. | Permanent |
| `dev` | Integration/staging branch. Version bumps and dev Docker releases happen here. | Permanent |
| `feature/*` | New features | Short-lived |
| `fix/*` | Bug fixes | Short-lived |
| `chore/*` | Maintenance, deps, config | Short-lived |
| `docs/*` | Documentation changes | Short-lived |
| `claude/*` | AI-assisted development branches | Short-lived |

## Git Flow

```mermaid
---
title: claude-mcp-server — Git & Release Flow
---
gitGraph
    commit id: "init"
    branch dev order: 1
    checkout dev
    commit id: "setup project"

    branch feature/auth order: 2
    checkout feature/auth
    commit id: "add token service"
    commit id: "add crypto utils"
    checkout dev
    merge feature/auth id: "merge feat" tag: "v0.1.0" type: HIGHLIGHT

    branch fix/validation order: 3
    checkout fix/validation
    commit id: "fix input check"
    checkout dev
    merge fix/validation id: "merge fix" tag: "v0.1.1" type: HIGHLIGHT

    checkout main
    merge dev id: "promote v0.1.1" tag: "latest" type: HIGHLIGHT

    checkout dev
    branch feature/repos order: 4
    checkout feature/repos
    commit id: "add repo handler"
    commit id: "add github service"
    checkout dev
    merge feature/repos id: "merge repos" tag: "v0.2.0" type: HIGHLIGHT

    checkout main
    merge dev id: "promote v0.2.0" tag: "latest " type: HIGHLIGHT
```

## Branch Lifecycle

The full lifecycle of a feature branch, from creation to production release:

```mermaid
flowchart LR
    A["Create branch\nfrom dev"] --> B["Develop &\ncommit"]
    B --> C["Open PR\nto dev"]
    C --> D["CI passes +\ncode review"]
    D --> E["Squash merge\nto dev"]
    E --> F["Dev release\n(Docker + tag)"]
    F --> G["Open PR\ndev → main"]
    G --> H["CI passes +\nreview"]
    H --> I["Merge to main"]
    I --> J["Prd release\n(Docker + latest)"]
    J --> K["Delete feature\nbranch"]
```

## Release Timeline

A typical release cycle from feature development to production:

```mermaid
timeline
    title Feature to Production Release
    section Development
        Create feature branch : Developer branches from dev
        Implement & commit : Write code, tests, docs
        Open PR to dev : Request review from team
    section Integration
        CI validation : Automated tests run
        Code review : Team reviews changes
        Squash merge to dev : Feature lands in dev
        Dev release : Docker image dev-X.Y.Z published
    section Production
        Open PR dev to main : Promote to production
        CI validation : Final automated checks
        Merge to main : Code reaches production
        Prd release : Docker image X.Y.Z + latest published
```

## Rules

1. **Never push directly to `main` or `dev`.** All changes go through Pull Requests.
2. Feature branches are created from `dev` and merged back to `dev` via PR.
3. `dev` is promoted to `main` for production releases via PR.
4. Use **squash merge** for feature branches to keep history clean.
5. Delete branches after merge — keep the repo clean.
6. Rebase feature branches on `dev` before opening a PR to keep history linear.
7. PRs to `dev` **must** have a version label: `feature`, `fix`, `breaking`, or `no-deploy`.

## Quick Reference

```bash
# Start a new feature
git checkout dev && git pull origin dev
git checkout -b feature/my-feature

# Work on the feature
git add <files>
git commit -m "feat(scope): add new feature"

# Push and open PR to dev
git push -u origin feature/my-feature
gh pr create --fill --base dev

# After approval, squash merge via GitHub UI
# Then promote dev to main when ready for production
```
