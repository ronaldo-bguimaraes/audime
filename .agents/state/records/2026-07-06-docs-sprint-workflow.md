# Record — Documentation Sprint: Workflow Docs

**Date:** 2026-07-06
**Objective:** Document the complete sprint workflow so any new agent or human can understand the full process by reading only the documentation.

---

## What Was Created

### `docs/workflow-sprint.md`
Complete sprint lifecycle documentation covering all 6 steps:
- Step 1: Refinement (product_owner defines criteria)
- Step 2: Discovery & Plan (product_manager + tech_lead research)
- Step 3: Test Specification (developer writes failing tests)
- Step 4: Development (developer implements, pre-commit security)
- Step 5: Validation & Improvement (qa_engineer + devops_engineer)
- Step 6: Review & Archive (product_owner archives)
- Discovery Mode (lightweight query mode)
- Core rules reference

### `docs/github-cli-workflow.md`
GitHub CLI operations for the audime project:
- Project board #5 details (ID, status options, field IDs)
- Issue creation and management
- Adding items to project board
- Moving cards between statuses with real `gh project` commands
- Step-by-step examples with actual project IDs
- Shell script shortcut for creating + adding + moving issues
- Sprint step ↔ board status mapping

### `docs/commit-flow.md`
Full commit and push process:
- 6-step pre-commit checklist (test → security → add → commit → push)
- Commit format: `<type>(<scope>): <description>`
- Types and scopes tables
- Pre-commit security scan commands
- Branch naming convention
- Checklist for before every commit

### `docs/token-scopes.md`
GitHub token scopes documentation:
- Required scopes: `repo`, `project`, `read:org`, `gist`
- How to verify and configure
- Fine-grained token permissions table
- Why each scope is needed

---

## What Was Modified

### `AGENTS.md`
- Added `docs/` directory to the structure tree
- Added Quick Reference table linking to new docs
- Added "GitHub Workflow" section covering issues, project board, and commits
- Referenced `docs/github-cli-workflow.md` for detailed board management
- Referenced `docs/commit-flow.md` for commit process
- Referenced `docs/token-scopes.md` for token requirements

---

## What Was Verified

| Check | Result |
|-------|--------|
| GitHub project #5 exists and is accessible | ✅ `audime`, 20 items |
| Token scopes include `repo`, `project`, `read:org`, `gist` | ✅ Verified |
| All 4 new docs are valid markdown | ✅ |
| AGENTS.md still references all canonical agent definitions | ✅ |
| Existing `docs/` files remain unchanged | ✅ |
| All project board status IDs are correct | ✅ Backlog/In Progress/In Review/Done |

---

## Known Gaps (Not in Scope)

- `.cursor/rules/` directory is empty — no Cursor-specific rules yet
- `.agents/templates/` directory is empty — no templates yet
- `docs/` now has 13 files total, which could benefit from a table of contents in future
