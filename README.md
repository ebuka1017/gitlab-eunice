# Eunice

Eunice is an AI agent system for technical debt intelligence in GitLab projects.

It is not a generic code review bot.

Eunice focuses on:
- debt detection and prioritization
- impact / ROI estimation using GitLab activity signals
- dependency-aware debt propagation ("root-node" risk)
- sprint-sized debt paydown planning
- actionable GitLab feedback (MR notes / issues)
- monthly debt balance sheet reporting

## What this repository is

This repository is the AI Catalog package for Eunice (agents + flows) published to GitLab AI Catalog.

It intentionally contains only:
- `agents/`
- `flows/`
- `README.md`
- `LICENSE`

Runtime integrations (for example Nia MCP, project-specific CI variables, custom config files) are configured in the project where Eunice runs.

## Architecture (new Eunice)

### Agents

- `eunice` — general-purpose debt triage and remediation planning agent (chat-friendly)
- `eunice-collector` — gathers measurable GitLab signals and produces evidence packets
- `eunice-graph` — builds dependency-weighted debt maps and propagated risk estimates
- `eunice-planner` — turns the debt graph into a paydown sprint and backlog recommendations
- `eunice-actioner` — writes MR comments/issues and manages follow-up actions

### Flows

- `eunice` — flagship debt triage flow (collector -> graph -> planner -> actioner)
- `eunice-mr-review` — MR-oriented fast path (collector -> graph -> actioner)
- `eunice-weekly-triage` — backlog/sprint planning flow (full pipeline)
- `eunice-monthly-balance-sheet` — debt paydown and trend reporting flow

## Trust model (how Eunice avoids hallucinated metrics)

Every metric should be labeled as one of:
- `measured` (from GitLab APIs / repository data)
- `estimated` (derived from assumptions)

Eunice should also emit:
- `analysis_mode`: `nia_enhanced` or `gitlab_only`
- `confidence`: `high`, `medium`, or `low`
- explicit assumptions used for ROI / cost calculations

## Nia setup (recommended, optional)

Eunice is designed to be Nia-first when Nia is available in the runtime.

### Why use Nia

Nia improves:
- semantic codebase understanding
- dependency and reference discovery quality
- confidence in dead-code / duplication findings
- debt propagation analysis quality

### What happens if you skip Nia

Eunice still works using GitLab built-in repository tools, but:
- dependency and relationship inference is weaker
- findings rely more on path/pattern heuristics
- confidence should be lower on structural conclusions

### Important catalog limitation

This AI Catalog repository uses GitLab's catalog YAML validation, which only accepts built-in tool IDs in `agents/*.yml` and `flows/*.yml`.

That means Nia tools (`manage_resource`, `nia_explore`, `nia_read`, `nia_grep`, `search`) cannot be declared in the catalog YAML tool lists even if you use Nia at runtime.

The correct model is:
- catalog YAML: validator-safe built-in GitLab tools
- runtime project: Nia tools available via MCP/runtime integration
- prompts: prefer Nia when available, fallback to GitLab tools when unavailable

## Setup (catalog publishing)

1. Validate agent/flow YAML via pipeline.
2. Push a tag (for example `v0.1.0`) to publish/update catalog items.
3. Enable the agent/flows in your GitLab group/project.
4. Test in Duo Chat and MR/issue contexts.

## Setup (runtime project)

In the project where Eunice actually runs:
- expose GitLab tools in the agent runtime (built-in)
- optionally expose Nia tools (recommended)
- add any org assumptions/config needed for ROI and sprint planning
- run Eunice in MR / issue / scheduled contexts

## Output expectations (product, not review bot)

A strong Eunice output should include:
- prioritized debt findings
- measured GitLab signals used
- estimated assumptions used
- dependency/propagation explanation (when available)
- sprint paydown plan (ordered by impact and dependency)
- action recommendations and generated artifacts (MR note/issue)

## Notes

This repository is the catalog package. Full runtime implementations may live in a separate repo that includes custom MCP configuration, config files, and project-specific automation.
