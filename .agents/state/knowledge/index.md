# Knowledge

This directory stores learning records produced by the **aprendiz** agent.

## Purpose

Unlike `lessons.md` (which accumulates cross-cycle lessons) and `records/` (which archives summaries of completed cycles), this directory contains **thematic and autonomous knowledge**: research about technologies, patterns, tools, and concepts relevant to the Audime project.

Each file is an independent record about a specific topic, created when the `aprendiz` agent is invoked to learn something.

## Format

Each file follows this format:

```markdown
---
date: YYYY-MM-DD
topic: <topic>
tags: [tag1, tag2]
sources:
  - title: <source title>
    url: <url>
---

# <Topic> — <date>

## What is it
...

## How we would use it in Audime
...

## Why not to use it
...

## Alternatives
...

## Pros and cons
| Pros | Cons |
|------|------|
| ...  | ...  |

## Conclusion
...
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `date` | Yes | Learning date in YYYY-MM-DD format |
| `topic` | Yes | Topic name (e.g., "Docker", "Pydantic", "WebSockets") |
| `tags` | Yes | List of tags for search and correlation |
| `sources` | Yes | List of consulted sources with title and URL |

### Naming

Files should be named as `<topic>.md`, where `<topic>` is a simplified version of the topic name:
- Lowercase letters, numbers, and hyphens only
- No spaces or special characters
- Examples: `docker.md`, `pydantic-v2.md`, `python-asyncio.md`

## Usage

To invoke the aprendiz and register knowledge about a topic:

```
@aprendiz learn docker
```

The aprendiz will:
1. Research the topic on the internet
2. Question how to apply it in Audime
3. Explain it in a structured way
4. Explore the codebase for context
5. Register in `<topic>.md`

## Differences from Other Artifacts

| Artifact | Written by | What it contains |
|----------|-----------|-----------------|
| `lessons.md` | Loopback / everyone | Cross-cycle lessons (failures, decisions, general learnings) |
| `records/` | Speculator | Summary of completed cycles (what was done, criteria status) |
| `knowledge/` | **Aprendiz** | Newly researched knowledge (topics, technologies, patterns) |
