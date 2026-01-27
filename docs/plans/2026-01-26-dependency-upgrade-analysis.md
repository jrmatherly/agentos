# Dependency Upgrade Analysis

> **Purpose:** Document the analysis of outdated Python packages, their breaking changes, upgrade status, and constraints for future reference.

**Date:** 2026-01-26

**Commit:** `8907421`

---

## Executive Summary

Analyzed 8 outdated packages identified by `uv pip list --outdated`. Successfully upgraded 3 packages. The remaining 5 are constrained by upstream dependencies and cannot be upgraded until those dependencies release updates with looser version constraints.

---

## Packages Analyzed

| Package | Current | Latest | Status | Risk Level |
|---------|---------|--------|--------|------------|
| agno-infra | 1.0.4 | 1.0.7 | ✅ Upgraded | Low |
| huggingface-hub | 1.3.3 | 1.3.4 | ✅ Upgraded | Low |
| openinference-instrumentation | 0.1.42 | 0.1.43 | ✅ Upgraded | Low |
| curl-cffi | 0.13.0 | 0.14.0 | ⏸️ Blocked | Medium |
| pydocket | 0.16.6 | 0.17.2 | ⏸️ Blocked | Low |
| referencing | 0.36.2 | 0.37.0 | ⏸️ Blocked | Low |
| starlette | 0.50.0 | 0.52.1 | ⏸️ Blocked | Low |
| wrapt | 1.17.3 | 2.0.1 | ⏸️ Blocked | Low |

---

## Successfully Upgraded Packages

### agno-infra (1.0.4 → 1.0.7)

**Dependency Chain:**

```markdown
agno-infra → agentos-matherlynet (direct dependency)
```

**Action Taken:** Changed constraint in `pyproject.toml` from pinned (`==1.0.4`) to minimum (`>=1.0.4`) to allow future patch upgrades automatically.

**Breaking Changes:** None documented. Patch releases within same major version.

**Source:** [PyPI - agno-infra](https://pypi.org/project/agno-infra/)

---

### huggingface-hub (1.3.3 → 1.3.4)

**Dependency Chain:**

```markdown
huggingface-hub → tokenizers → litellm → agentos-matherlynet
```

**Breaking Changes:** None. Patch release.

**Source:** [PyPI - huggingface-hub](https://pypi.org/project/huggingface-hub/)

---

### openinference-instrumentation (0.1.42 → 0.1.43)

**Dependency Chain:**

```markdown
openinference-instrumentation → openinference-instrumentation-agno → agentos-matherlynet
```

**Breaking Changes:** None. Patch release.

**Source:** [PyPI - openinference-instrumentation](https://pypi.org/project/openinference-instrumentation/)

---

## Blocked Packages (Awaiting Upstream Updates)

### curl-cffi (0.13.0 → 0.14.0)

**Dependency Chain:**

```markdown
curl-cffi → yfinance → agentos-matherlynet
```

**Blocked By:** `yfinance` caps curl-cffi at `<0.14`

**Breaking Changes in 0.14.0:**

- macOS requirement now 15.0+ (due to bundled c-ares)
- Python requirement now 3.10+
- Async websocket API completely rewritten with performance improvements

**Environment Compatibility:** Our environment (macOS 15.0+, Python 3.12) is compatible with 0.14.0.

**Action Required:** Wait for `yfinance` to release with updated curl-cffi constraint, or pin yfinance and manually override curl-cffi if security-critical.

**Sources:**

- [curl-cffi Changelog](https://curl-cffi.readthedocs.io/en/latest/changelog.html)
- [curl-cffi GitHub Releases](https://github.com/yifeikong/curl_cffi/releases)

---

### pydocket (0.16.6 → 0.17.2)

**Dependency Chain:**

```markdown
pydocket → fastmcp → agentos-matherlynet
```

**Blocked By:** `fastmcp` caps pydocket at `<0.17`

**New Features in 0.17.x:**

- Redis Cluster support via `redis+cluster://` URLs
- Shared dependencies (worker-scoped resource management)
- Refactored worker architecture (retries, perpetuals, timeouts driven by dependencies)
- Fixed memory leak in fakeredis Lua script execution

**Breaking Changes:** None documented. Architecture refactoring maintains backward compatibility.

**Action Required:** Wait for `fastmcp` to release with updated pydocket constraint.

**Source:** [Docket GitHub Releases](https://github.com/chrisguidry/docket/releases)

---

### referencing (0.36.2 → 0.37.0)

**Dependency Chain:**

```markdown
referencing → jsonschema → litellm/mcp → agentos-matherlynet
referencing → jsonschema-path → fastmcp → agentos-matherlynet
referencing → jsonschema-specifications → jsonschema → ...
```

**Blocked By:** `jsonschema`, `jsonschema-path`, `jsonschema-specifications` cap referencing at `<0.37`

**Changes in 0.37.0:**

- Dropped Python 3.9 support
- Added Python 3.14 and 3.14t support

**Breaking Changes:** Only Python 3.9 removal (not applicable - we use Python 3.12).

**Action Required:** Wait for `jsonschema` ecosystem to release with updated referencing constraint.

**Source:** [referencing GitHub Releases](https://github.com/python-jsonschema/referencing/releases)

---

### starlette (0.50.0 → 0.52.1)

**Dependency Chain:**

```markdown
starlette → fastapi → agentos-matherlynet
starlette → mcp → agentos-matherlynet
starlette → sse-starlette → mcp → ...
```

**Blocked By:** `fastapi`, `mcp`, `sse-starlette` cap starlette at `<0.51`

**Changes in 0.51.0-0.52.1:**

- `allow_private_network` added to CORSMiddleware
- Increased warning stacklevel on DeprecationWarning for wsgi module
- Python 3.9 support dropped in 0.50.0

**Breaking Changes:** Only Python 3.9 removal (not applicable - we use Python 3.12).

**Action Required:** Wait for `fastapi` and `mcp` to release with updated starlette constraint.

**Sources:**

- [Starlette Release Notes](https://starlette.dev/release-notes/)
- [Starlette PyPI](https://pypi.org/project/starlette/)

---

### wrapt (1.17.3 → 2.0.1)

**Dependency Chain:**

```markdown
wrapt → openinference-instrumentation → openinference-instrumentation-agno → agentos-matherlynet
wrapt → opentelemetry-instrumentation → openinference-instrumentation-agno → ...
wrapt → opentelemetry-instrumentation → pydocket → fastmcp → agentos-matherlynet
```

**Blocked By:** `openinference-instrumentation`, `opentelemetry-instrumentation` cap wrapt at `<2.0`

**Changes in 2.0.0:**

- Removed all Python 2.7 and early Python 3.x compatibility code
- Removed setuptools runtime dependency (uses importlib.metadata instead)
- Added type hints support for Python 3.10+

**Breaking Changes:** None documented. Major version bump was precautionary due to internal refactoring, not API changes.

**Action Required:** Wait for `opentelemetry-instrumentation` to release with updated wrapt constraint.

**Sources:**

- [wrapt 2.0.0 Announcement](https://grahamdumpleton.me/posts/2025/10/wrapt-version-2-0-0/)
- [wrapt Release Notes](https://wrapt.readthedocs.io/en/master/changes.html)

---

## Recommendations

### Immediate Actions (Completed)

1. ✅ Upgraded agno-infra, huggingface-hub, openinference-instrumentation
2. ✅ Loosened agno-infra constraint to allow future patch upgrades
3. ✅ Regenerated requirements.txt and uv.lock
4. ✅ Validated with ruff and mypy

### Future Actions

1. **Monitor upstream releases** - Check monthly for updates to:
   - `fastapi` (unblocks starlette)
   - `yfinance` (unblocks curl-cffi)
   - `fastmcp` (unblocks pydocket)
   - `jsonschema` (unblocks referencing)
   - `opentelemetry-instrumentation` (unblocks wrapt)

2. **Re-run analysis** - After upstream updates, run:

   ```bash
   uv pip list --outdated
   uv lock --upgrade
   ./scripts/generate_requirements.sh
   mise run validate
   ```

3. **Security monitoring** - If any blocked package has a CVE:
   - Consider pinning parent dependency and manually overriding
   - Example: `pip install --force-reinstall curl-cffi==0.14.0`

---

## Commands Reference

```bash
# Check outdated packages
uv pip list --outdated

# Show dependency tree (what requires a package)
uv tree --invert --package <package-name>

# Upgrade specific packages
uv lock --upgrade-package <package-name>

# Upgrade all packages
uv lock --upgrade

# Regenerate requirements.txt
./scripts/generate_requirements.sh

# Sync installed packages with lock
uv sync --all-extras

# Validate
mise run validate
```

---

## Appendix: Full Dependency Trees

### starlette

```tree
starlette v0.50.0
├── fastapi v0.128.0
│   └── agentos-matherlynet[standard] v1.0.0
├── mcp v1.26.0
│   ├── agentos-matherlynet v1.0.0
│   └── fastmcp v2.14.4
│       └── agentos-matherlynet v1.0.0
└── sse-starlette v3.2.0
    └── mcp v1.26.0
```

### wrapt

```tree
wrapt v1.17.3
├── openinference-instrumentation v0.1.43
│   └── openinference-instrumentation-agno v0.1.26
│       └── agentos-matherlynet v1.0.0
├── openinference-instrumentation-agno v0.1.26
└── opentelemetry-instrumentation v0.60b1
    ├── openinference-instrumentation-agno v0.1.26
    └── pydocket v0.16.6
        └── fastmcp v2.14.4
            └── agentos-matherlynet v1.0.0
```

### curl-cffi

```tree
curl-cffi v0.13.0
└── yfinance v1.1.0
    └── agentos-matherlynet v1.0.0
```

### pydocket

```tree
pydocket v0.16.6
└── fastmcp v2.14.4
    └── agentos-matherlynet v1.0.0
```

### referencing

```tree
referencing v0.36.2
├── jsonschema v4.26.0
│   ├── litellm v1.81.3
│   │   └── agentos-matherlynet v1.0.0
│   └── mcp v1.26.0
│       ├── agentos-matherlynet v1.0.0
│       └── fastmcp v2.14.4
│           └── agentos-matherlynet v1.0.0
├── jsonschema-path v0.3.4
│   └── fastmcp v2.14.4
└── jsonschema-specifications v2025.9.1
    └── jsonschema v4.26.0
```
