# CI/CD Pipeline

This project uses a three-stage GitHub Actions pipeline: PR validation, dev release, and production release. All workflow configuration lives in `.github/workflows/`.

## Pipeline Overview

```mermaid
flowchart TD
    PR["PR opened\nto dev or main"] -->|triggers| CI["CI: ci.yml\nCheckout → Python 3.11\nInstall deps → pytest"]
    CI -->|pass| Mergeable["PR mergeable ✓"]
    CI -->|fail| Blocked["PR blocked ✗"]

    MergeDev["PR merged\nto dev"] -->|triggers| RelDev["Release Dev:\nrelease-dev.yml"]
    RelDev --> CheckLabel{no-deploy\nlabel?}
    CheckLabel -->|yes| Skip1["Skip release"]
    CheckLabel -->|no| Bump["Version bump\nfrom PR labels"]
    Bump --> DockerDev["Build + push Docker\nghcr.io/…:dev-X.Y.Z"]
    DockerDev --> TagDev["Create git tag\nvX.Y.Z"]

    MergeMain["PR merged\nto main"] -->|triggers| RelPrd["Release Prd:\nrelease-prd.yml"]
    RelPrd --> CheckLabel2{no-deploy\nlabel?}
    CheckLabel2 -->|yes| Skip2["Skip release"]
    CheckLabel2 -->|no| ReadTag["Read latest\ngit tag"]
    ReadTag -->|exists| DockerPrd["Build + push Docker\nghcr.io/…:X.Y.Z\nghcr.io/…:latest"]
    ReadTag -->|missing| Fail["Pipeline fails"]
```

## Stage 1: CI — Pull Request Validation

**Workflow:** `ci.yml`
**Trigger:** Every PR targeting `dev` or `main`.

```mermaid
flowchart LR
    A["PR opened"] --> B["Checkout\n(actions/checkout@v4)"]
    B --> C["Setup Python 3.11\n(actions/setup-python@v5)"]
    C --> D["Install deps\npip install -e '.[dev]'"]
    D --> E["Run pytest\npytest tests/ -v"]
    E -->|pass| F["PR mergeable"]
    E -->|fail| G["PR blocked"]
```

All actions are pinned to commit SHAs for reproducibility and supply-chain security.

## Stage 2: Dev Release

**Workflow:** `release-dev.yml`
**Trigger:** PR merged into `dev` (skipped if `no-deploy` label is present).

```mermaid
flowchart TD
    A["PR merged → dev"] --> B{no-deploy label?}
    B -->|yes| X["Skip release"]
    B -->|no| C["Read PR labels"]
    C --> D{Which label?}
    D -->|breaking| E["MAJOR bump\n(1.0.0 → 2.0.0)"]
    D -->|feature| F["MINOR bump\n(0.1.0 → 0.2.0)"]
    D -->|fix| G["PATCH bump\n(0.1.0 → 0.1.1)"]
    D -->|none| H["Pipeline fails\n(label required)"]
    E & F & G --> I["Build Docker image\n(docker/build-push-action@v6)"]
    I --> J["Push to GHCR\nghcr.io/…:dev-X.Y.Z"]
    J --> K["Create git tag\nvX.Y.Z"]
```

**What happens under the hood:**

1. Checkout with full history (`fetch-depth: 0`, `fetch-tags: true`)
2. Read PR labels to determine bump type (major/minor/patch)
3. Find latest `v*` tag and calculate next version
4. Login to GHCR with `GITHUB_TOKEN`
5. Build Docker image with BuildKit layer caching (`type=gha`)
6. Push image tagged `dev-X.Y.Z`
7. Create and push annotated git tag `vX.Y.Z`

**Concurrency:** Uses `concurrency: release-dev` group — only one dev release runs at a time (no cancellation of in-progress runs).

## Stage 3: Production Release

**Workflow:** `release-prd.yml`
**Trigger:** PR merged into `main` (skipped if `no-deploy` label is present).

```mermaid
flowchart TD
    A["PR merged → main"] --> B{no-deploy label?}
    B -->|yes| X["Skip release"]
    B -->|no| C["Read latest git tag"]
    C --> D{Tag exists?}
    D -->|no| E["Pipeline fails\n(dev release required first)"]
    D -->|yes| F["Build Docker image\n(docker/build-push-action@v6)"]
    F --> G["Push to GHCR\nghcr.io/…:X.Y.Z\nghcr.io/…:latest"]
```

**Prerequisite:** A dev release must exist (a `v*` tag must be present). The production pipeline reads the latest tag — it does not bump versions itself.

**Concurrency:** Uses `concurrency: release-prd` group.

## End-to-End Example

A complete feature from development to production:

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
    FB->>DV: open PR (label: feature)
    DV->>CI: trigger tests
    CI-->>DV: tests pass

    Dev->>DV: merge PR
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

## Pipeline Stage Durations

Approximate timing for each pipeline stage:

```mermaid
gantt
    title CI/CD Pipeline Timing
    dateFormat ss
    axisFormat %S s

    section CI Pipeline
        Checkout code           :ci1, 00, 3s
        Setup Python 3.11       :ci2, after ci1, 5s
        Install dependencies    :ci3, after ci2, 15s
        Run pytest              :ci4, after ci3, 5s

    section Dev Release
        Checkout (full history) :dev1, 00, 5s
        Determine version bump  :dev2, after dev1, 2s
        Login to GHCR           :dev3, after dev2, 2s
        Build Docker image      :dev4, after dev3, 30s
        Push to GHCR            :dev5, after dev4, 10s
        Create git tag          :dev6, after dev5, 3s

    section Prd Release
        Checkout (full history) :prd1, 00, 5s
        Resolve version tag     :prd2, after prd1, 2s
        Login to GHCR           :prd3, after prd2, 2s
        Build Docker image      :prd4, after prd3, 30s
        Push to GHCR (2 tags)   :prd5, after prd4, 10s
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
| `no-deploy` | **skip** | Merge without triggering any release |
| *(none)* | **error** | Pipeline fails — label is required |

## Security Notes

- All GitHub Actions are **pinned to commit SHAs** (not mutable tags) to prevent supply-chain attacks.
- GHCR authentication uses the built-in `GITHUB_TOKEN` — no manual secrets required for Docker pushes.
- Docker layer caching uses GitHub Actions cache (`type=gha`) to speed up builds.
- The runtime Docker image runs as a **non-root user** (`mcp`, UID 1000).
