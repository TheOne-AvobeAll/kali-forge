# kali-forge

A modular, local-first security testing workflow toolkit for authorized assessments and isolated labs.

## Overview

`kali-forge` is a security-first Python CLI framework for local, deterministic automation in isolated lab environments. It is designed to run allowlisted commands and keep workflow execution explicit, auditable, and predictable.

## Goals

- Deterministic execution with explicit policy boundaries
- Security-first subprocess handling
- Local-first operation without AI or runtime model dependencies
- Modular architecture for lab config, workflow execution, and plan-based automation

## Current structure

- `src/kali_forge/cli.py` — CLI entry points and command routing
- `src/kali_forge/config.py` — runtime configuration defaults
- `src/kali_forge/security.py` — path validation and executable allowlisting
- `src/kali_forge/executor.py` — safe subprocess execution with output limits and timeouts
- `src/kali_forge/workflow.py` — workflow templates and quoted-step handling
- `src/kali_forge/lab.py` — lab configuration serialization and validation
- `src/kali_forge/plan.py` — execution plan definitions and persistence
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

Run a safe command:

```bash
kali-forge run echo hello
```

Show the active runtime configuration:

```bash
kali-forge config
```

List built-in workflows:

```bash
kali-forge workflow list
```

Run a workflow:

```bash
kali-forge workflow run hello-world
```

Create a lab config:

```bash
kali-forge lab init kali-forge.lab.json
```

Create a plan file:

```bash
kali-forge plan init kali-forge.plan.json
```

Run a saved plan:

```bash
kali-forge plan run kali-forge.plan.json
```

## Security model

- No shell is used for execution; subprocess calls run with `shell=False`.
- Executables must be explicitly allowlisted.
- Paths must remain within the configured working directory.
- Output is capped to prevent oversized memory consumption.
- Execution times are bounded using explicit timeouts.
- Lab configs and plans are explicit and reviewable before execution.

## Roadmap

The project is now a working foundation suitable for a local-first security automation platform. The next logical evolution is to add richer plan validation, persistence of lab profiles, and support for domain-specific workflows beyond the builtin template set.
