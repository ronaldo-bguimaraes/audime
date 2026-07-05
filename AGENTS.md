# Audime — Squad Agent System

Entry point for the squad-based incremental development agent system.

## Structure

```
.agents/
  agents/           ← Team member definitions (scrum_master, product_owner, developer, etc.)
  policies/         ← Security policies
  workspace/        ← Sprint artifacts (specification, validation, plan)
  state/            ← Persistent state (lessons.md, lessons_technical.md) and records/
AGENTS.md           ← Entry point for the agent system
```

## Usage

The scrum_master agent coordinates TDD sprints:
1. **Refinement** — defines criteria in `.agents/workspace/specification.md` (product_owner)
2. **Discovery** — researches and challenges with product_manager + tech_lead
3. **Test Specification** — writes failing tests that define expected behavior (developer)
4. **Development** — implements to satisfy the tests (developer)
5. **Validation** — verifies criteria and confirms ALL tests pass (qa_engineer, devops_engineer)
6. **Review & Archive** — records in `.agents/state/records/`

For quick queries without altering files, use **Discovery Mode**.

## Core Rules

- [CORE] Spec-first: no sprint without criteria
- [CORE] TDD-first: no implementation without a failing test that defines it
- [CORE] Audit mandatory: no sprint ends without validation
- [CORE] Maker-checker split: product_owner ≠ implementer ≠ qa_engineer
- [CORE] No-downgrade: every iteration improves the project
- [CONSTRAINT] Passing tests > existing implementation: implementation must adapt to tests, never vice versa
- [CONSTRAINT] Regression mandatory: any change to a rule or module must re-run all related tests and confirm no existing behavior is broken
- [CONSTRAINT] **Security first**: before every `git commit` or `git push`, execute `@devops_engineer` to scan for leaked credentials. If devops_engineer flags issues, resolve before proceeding.
