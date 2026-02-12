# CI/CD Pipeline

## Git Workflow

```mermaid
---
title: claude-mcp-server — Git & Release Flow
---
gitGraph
    commit id: "init"
    branch dev
    checkout dev
    commit id: "setup project"

    branch feature/auth
    checkout feature/auth
    commit id: "add token service"
    commit id: "add crypto utils"
    checkout dev
    merge feature/auth id: "merge feat" tag: "v0.1.0" type: HIGHLIGHT

    branch fix/validation
    checkout fix/validation
    commit id: "fix input check"
    checkout dev
    merge fix/validation id: "merge fix" tag: "v0.1.1" type: HIGHLIGHT

    checkout main
    merge dev id: "promote v0.1.1" tag: "latest" type: HIGHLIGHT

    checkout dev
    branch feature/repos
    checkout feature/repos
    commit id: "add repo handler"
    commit id: "add github service"
    checkout dev
    merge feature/repos id: "merge repos" tag: "v0.2.0" type: HIGHLIGHT

    checkout main
    merge dev id: "promote v0.2.0" tag: "latest " type: HIGHLIGHT
```

## Pipeline Stages

### 1. CI — Pull Request Validation (`ci.yml`)

Runs on every PR targeting **`dev`** or **`main`**.

```mermaid
flowchart LR
    A[PR opened] --> B[Checkout]
    B --> C[Setup Python 3.11]
    C --> D[Install dependencies]
    D --> E[Run pytest]
    E -->|pass| F[PR mergeable]
    E -->|fail| G[PR blocked]
```

### 2. Dev Release (`release-dev.yml`)

Triggers when a PR is **merged into `dev`**.

```mermaid
flowchart TD
    A[PR merged → dev] --> B[Read PR labels]
    B --> C{Which label?}
    C -->|breaking| D["MAJOR bump (1.0.0 → 2.0.0)"]
    C -->|feature| E["MINOR bump (0.1.0 → 0.2.0)"]
    C -->|fix| F["PATCH bump (0.1.0 → 0.1.1)"]
    C -->|none| G[Pipeline fails]
    D & E & F --> H[Build Docker image]
    H --> I["Push to GHCR\nghcr.io/…:dev-X.Y.Z"]
    I --> J["Create git tag\nvX.Y.Z"]
```

### 3. Production Release (`release-prd.yml`)

Triggers when a PR is **merged into `main`**.

```mermaid
flowchart TD
    A[PR merged → main] --> B[Read latest git tag]
    B --> C{Tag exists?}
    C -->|no| D[Pipeline fails]
    C -->|yes| E[Build Docker image]
    E --> F["Push to GHCR\nghcr.io/…:X.Y.Z\nghcr.io/…:latest"]
```

## End-to-End Example

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant FB as feature/auth
    participant DV as dev branch
    participant MN as main branch
    participant CI as CI Pipeline
    participant RD as Release Dev
    participant RP as Release Prd
    participant GH as GHCR

    Dev->>FB: push commits
    FB->>DV: open PR
    DV->>CI: trigger tests
    CI-->>DV: tests pass

    Dev->>DV: merge PR (label: feature)
    DV->>RD: trigger release-dev
    RD->>RD: bump version (0.1.0 → 0.2.0)
    RD->>GH: push ghcr.io/…:dev-0.2.0
    RD->>DV: create tag v0.2.0

    DV->>MN: open PR (dev → main)
    MN->>CI: trigger tests
    CI-->>MN: tests pass

    Dev->>MN: merge PR
    MN->>RP: trigger release-prd
    RP->>RP: read tag v0.2.0
    RP->>GH: push ghcr.io/…:0.2.0
    RP->>GH: push ghcr.io/…:latest
```

## Docker Tag Summary

| Event | Docker Tag | Example |
|-------|-----------|---------|
| Merge to `dev` | `dev-<version>` | `ghcr.io/pedrovmota/claude-mcp-server:dev-0.2.0` |
| Merge to `main` | `<version>` | `ghcr.io/pedrovmota/claude-mcp-server:0.2.0` |
| Merge to `main` | `latest` | `ghcr.io/pedrovmota/claude-mcp-server:latest` |

## Version Bump Rules

Applied via **PR labels** on merges to `dev`:

| Label | Bump | Example |
|-------|------|---------|
| `fix` | patch | `0.1.0` → `0.1.1` |
| `feature` | minor | `0.1.0` → `0.2.0` |
| `breaking` | major | `0.1.0` → `1.0.0` |
| *(none)* | **error** | Pipeline fails — label is required |
