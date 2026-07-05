# Cycle 004 — Skills vs Agents in the Loopback Ecosystem

**Date:** 2026-06-30
**Status:** ✅ Architectural analysis complete (4/4 criteria approved)

## Summary
Architectural analysis comparing Skills vs Agents for each of the 5 subagents in the Loopback ecosystem, based on external research (RAIL Framework, Loop Engineering, Anthropic, breaking.build) and current project configuration verification.

## What was analyzed
- Complete mapping of the 5 subagents (especulador, questionador, explicador, validador, seguranca) + 2 existing skills (agents, prd)
- Individual analysis of each subagent across 7 aspects (tools, isolation, permissions, model, autonomous loop, multiple invocation, classification)
- Comparison with the OpenCode Skill format (SKILL.md with frontmatter, no isolated context, no own permissions)
- Verification of opencode.json and permission configuration
- Research of external references (RAIL, breaking.build, skills 2.0 issue #17791)

## Mapping

| Subagent | Classification | Recommendation |
|----------|---------------|---------------|
| **questionador** | Skill | Pure research instruction — does not validate, does not judge. Loses parallelism but gains simplicity. |
| **explicador** | Skill | Same case as questionador. Can be combined into a `pesquisador` skill. |
| **especulador** | Hybrid | Spec Mode → skill; Validation Mode → agent (maker-checker). In practice, keep as agent. |
| **validador** | Agent (keep) | **Critical**: needs context isolation and restricted permissions (bash only). |
| **seguranca** | Agent (keep) | Needs restricted permissions (bash without write/edit). Mechanized scanning but limited tools. |

## Final Recommendation

**KEEP the current subagent architecture.** Justifications:

1. **Maker-checker split** is the most important principle — skills do not offer context isolation
2. **Loss of parallelism** — questionador + explicador run in parallel today; skills are sequential
3. **Reuse is not a problem** — only loopback invokes these subagents
4. **Skills 2.0** (context: fork, allowed_tools) is under discussion — worth waiting to mature
5. **Actual cost not measured** — agent overhead may be a benefit (isolation)
6. **Migration complexity** does not justify the gain for 2 out of 5 subagents

## Decisions Made
- Do not migrate any subagent to skill at this time
- Monitor Skills 2.0 (issue #17791) for future reassessment
- If migration is insisted upon: create a `pesquisador` skill unifying questionador + explicador

## Lessons
- The decisive criterion between skill and agent is not scope, but **need for context isolation** [CORE]
- Skills are suitable for additive tasks (research, questioning) that do not require independence [ROUTING]
- Agents are required for critical validation/verification tasks that demand independence from the implementer [CORE]
- Parallelism is a concrete advantage of subagents that skills do not replicate [CONSTRAINT]
