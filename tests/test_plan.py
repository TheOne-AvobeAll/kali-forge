# kali-forge

A modular, local-first security testing workflow toolkit for authorized assessments and isolated labs.

## Overview

`kali-forge` is a security-first Python CLI foundation designed for deterministic, locally controlled automation. The project now includes a secure execution layer, configuration defaults, reusable workflow models, a local lab configuration system, and persistent execution plans for repeatable automation.

## Goals

- Deterministic execution with explicit policy boundaries
- Security-first subprocess handling
- Local-first operation without AI runtime dependencies
- Modular architecture that isolates workflow logic from system controls

## Current structure

- `src/kali_forge/cli.py` — CLI entry points
- `src/kali_forge/config.py` — configuration defaults and validation
- `src/kali_forge/security.py` — path and executable validation helpers
- `src/kali_forge/executor.py` — safe subprocess execution
- `src/kali_forge/workflow.py` — built-in workflow templates and quoted-step parsing
- `src/kali_forge/lab.py` — local lab configuration model and file helpers
- `src/kali_forge/plan.py` — persisted execution plans for deterministic multi-step runs
- `tests/` — regression tests for security-sensitive behavior

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Commands

Show help:

```bash
kali-forge --help
```

Print version:

```bash
kali-forge version
```

Run a safe command (allowlisted executables only):

```bash
kali-forge run echo hello
```

Show the effective configuration:

```bash
kali-forge config --show
```

List built-in workflows:

```bash
kali-forge workflow list
```

Show a workflow definition:

```bash
kali-forge workflow show hello-world
```

Run a built-in workflow:

```bash
kali-forge workflow run hello-world
```

Create a default lab config file:

```bash
kali-forge lab init kali-forge.lab.json
```

Inspect a saved lab config:

```bash
kali-forge lab show kali-forge.lab.json
```

Create a default execution plan:

```bash
kali-forge plan init kali-forge.plan.json
```

Run a saved execution plan:

```bash
kali-forge plan run kali-forge.plan.json
```

## Security model

- No shell is used for execution; subprocess calls run with `shell=False`.
- Executables must be explicitly allowlisted.
- Paths must resolve within a configured working directory.
- Command output is capped to prevent excessive memory use.
- Default timeouts are enforced to avoid hanging operations.
- Lab configs and execution plans are explicit and auditable before deployment.

## Roadmap

The project is intentionally a minimal but extensible foundation. The next layer should add richer lab orchestration, policy enforcement, and persistence for multi-step assessment flows while preserving the security controls built into the runtime.
