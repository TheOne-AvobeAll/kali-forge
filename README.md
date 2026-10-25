# kali-forge

A modular, local-first security testing workflow toolkit for authorized assessments and isolated labs.

## Overview

`kali-forge` is a security-first Python CLI foundation designed for deterministic, locally controlled automation. The initial implementation establishes the project skeleton, configuration model, and safe execution primitives needed for future workflow modules and lab tooling.

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

## Security model

- No shell is used for execution; subprocess calls run with `shell=False`.
- Executables must be explicitly allowlisted.
- Paths must resolve within a configured working directory.
- Command output is capped to prevent excessive memory use.
- Default timeouts are enforced to avoid hanging operations.

## Roadmap

This repository is intentionally a minimal foundation. The next layer should add actual workflow modules such as lab orchestration, policy enforcement, and command inventory management while preserving these core security controls.
