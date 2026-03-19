# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Splunk SOAR connector for the CrowdStrike OAuth2 API. It integrates with CrowdStrike Falcon to provide endpoint security data (detections, incidents, devices, IOCs, real-time response, sandbox detonation, etc.) within the SOAR platform.

## Linting and Code Quality

Pre-commit hooks handle all linting and formatting. Install and run them with:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Key hooks:
- **ruff** — linting and formatting (replaces flake8/black)
- **djLint** — HTML template linting/formatting
- **soar-app-linter** — validates the app JSON and connector structure
- **build-docs** — regenerates HTML documentation from the app JSON
- **conventional-pre-commit** — enforces Conventional Commits format for commit messages (e.g. `fix(TICKET-123): description`)

## Architecture

### Core Files

- **`crowdstrikeoauthapi_connector.py`** — Main connector class (`CrowdstrikeConnector`), subclasses Phantom's `BaseConnector`. All action handlers (`handle_action`) live here. This is the largest file in the repo.
- **`crowdstrikeoauthapi_consts.py`** — All constants: config keys, API endpoint paths, error/success message strings, status code lists.
- **`crowdstrikeoauthapi.json`** — App manifest: declares app metadata, asset configuration schema, and all supported actions with their parameter definitions. This is the source of truth for what actions exist and their input/output schemas.
- **`parse_cs_events.py`** — Parses raw CrowdStrike `DetectionSummaryEvent` and `EppDetectionSummaryEvent` stream data into SOAR containers/artifacts.
- **`parse_cs_incidents.py`** — Parses incident data into SOAR containers/artifacts.
- **`crowdstrike_view.py`** — Custom Phantom view renderers for action results.
- **`*.html`** — Django-template HTML files for rendering action results in the SOAR UI (one per action).

### Authentication Flow

The connector uses OAuth2 client credentials. Tokens are stored encrypted in SOAR's state file (per-asset). Multi-tenant (subtenant CIDs) is supported — tokens are stored as a dict keyed by tenant CID. Token refresh happens every ~29 minutes.

### Ingestion (On Poll)

Polling uses CrowdStrike's streaming API (`/sensors/entities/datafeed/v2`) to ingest `DetectionSummaryEvent` and `EppDetectionSummaryEvent` events as SOAR containers. The state file tracks the last feed offset to avoid duplicate ingestion.

### App JSON ↔ Connector Relationship

Every action defined in `crowdstrikeoauthapi.json` maps to a `_handle_<action_identifier>` method in the connector. When adding a new action, both files must be updated together.

## Commit Message Format

Commits must follow Conventional Commits: `type(scope): description`
- Types: `fix`, `feat`, `chore`, `docs`, `refactor`, `test`
- Scope is typically a JIRA ticket (e.g. `PAPP-12345`)

## Release Notes

Add entries for user-visible changes to `release_notes/unreleased.md`. The `release-notes` pre-commit hook validates this file exists and is non-empty for changes.
