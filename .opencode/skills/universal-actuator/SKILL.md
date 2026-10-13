---
name: universal-actuator
description: Federated search, RAG ingest, fleet telemetry and milestones via the Universal Actuator hub.
---

# Universal Actuator

Federation gateway consolidating fleet MCP servers into one tool interface.

## Before starting work

1. Check hub status: `universal_status()` — federation graph, registered domains.
2. Search federated content: `search_federated(query="...")`.

## At end of work

- Record progress: `universal_milestone(title="...", description="...")`.
- Ingest new content if relevant: `ingest_fleet_to_rag()`.
