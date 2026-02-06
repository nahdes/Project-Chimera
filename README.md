# Project Chimera

Autonomous Influencer Network — orchestration, planning, and worker services
for persona-driven content generation using MCP integrations, Python 3.12+,
FastAPI, and async/await.

This repository contains the reference implementation and developer tooling
for Project Chimera: an experiment in autonomous agents that plan,
generate, validate, and publish social content according to immutable
personas defined in `SOUL.md` files.

**Status:** Draft (specs and tests drive development via TDD)

--

**Quick links**

- Specs: [specs/functional.md](specs/functional.md)
- Technical API: [specs/technical.md](specs/technical.md)
- Skills: [skills/README.md](skills/README.md)
- Tests: [tests](tests)
- Dockerfile: [Dockerfile](Dockerfile)

--

## Highlights

- Modular architecture: `orchestrator`, `planner`, `worker`, `judge` services
- Skill-driven capabilities: each competency is a pluggable `Skill`
- MCP abstraction for all external integrations (no direct API calls)
- Async-first, non-blocking workers and optimistic concurrency control (OCC)
- Test-driven: unit/integration/e2e tests under `tests/`

--

## Prerequisites

- Python 3.12+
- Git
- Docker (optional, for containerized runs)

On Windows, use a supported terminal (PowerShell / WSL recommended).

--

## Local development (recommended)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
.venv\Scripts\Activate.ps1 # PowerShell on Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run tests:

```bash
pytest -q
```

Notes:
- The project follows a TDD approach — many tests in `tests/unit` are
	intentionally written to fail until implementations are added.
- See `specs/functional.md` and `specs/technical.md` for acceptance criteria
	and API contracts you must implement to satisfy tests.

--

## Running the Orchestrator (development)

The codebase uses FastAPI services for the orchestrator and other
components. A simple development command (after installing deps):

```bash
uvicorn chimera.services.orchestrator:app --reload --host 0.0.0.0 --port 8000
```

Replace the module path above with the service you want to run (e.g.,
`chimera.services.worker:app`) when applicable.

--

## Docker

Build (uses the repository `Dockerfile`):

```bash
docker build -t chimera:dev .
```

Run (example):

```bash
docker run --rm -p 8000:8000 chimera:dev
```

Notes and caveats:
- The provided `Dockerfile` targets Python 3.12 and copies a virtual
	environment from a builder stage. The build assumes a reproducible
	dependency lockfile is available (see `pyproject.toml` / lockfile).
- The healthcheck in the current `Dockerfile` is a placeholder; consider
	replacing it with a real readiness probe (e.g., `curl http://localhost:8000/health`).

--

## Project layout

- `specs/` — functional and technical specifications (source of truth)
- `src/chimera/` — application source code (services, core, skills)
- `services/` — service entrypoints and service-specific code
	(`orchestrator`, `planner`, `worker`, `judge`, etc.)
- `skills/` — skill modules and README-guides for each skill
- `tests/` — unit, integration, and e2e tests (TDD-first)

--

## Development principles

- No direct third-party API calls — use MCP abstraction to integrate
	external providers.
- All I/O in workers must be async (no blocking calls).
- Use optimistic concurrency control (OCC) for all state changes.
- Persona validation against `SOUL.md` is mandatory at agent creation.
- Budget checks must run before any transaction operations.
- Use structured logging with `trace_id` in all services.

--

## How to contribute

1. Fork the repository and create a feature branch.
2. Implement tests for your change first (TDD). Tests live under `tests/`.
3. Run and iterate until tests pass.
4. Open a PR with a clear description and link to the relevant spec
	 acceptance criteria in `specs/functional.md` or `specs/technical.md`.

--

## Where to look next

- Start with `tests/unit` to see current TDD expectations.
- Read `specs/functional.md` (US-001..US-...) for user stories.
- Review `skills/README.md` for skill design and examples.

--

If you'd like, I can:
- Improve the `Dockerfile` to ensure deterministic builds (copy lockfile,
	pin tool names), and add a real `HEALTHCHECK`.
- Run the test suite in this environment and report failing tests.
- Expand developer setup instructions to include `pyproject.toml`/`uv` workflow.

--

License: UNLICENSED (check project maintainers for licensing details)

