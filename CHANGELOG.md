# Changelog

All notable changes to Eunice are documented in this file.

## [0.2.7] - 2026-02-24
### Changed
- Pruned stale deleted-agent entries from `.ai-catalog-mapping.json` so the mapping reflects the true single-agent catalog (`agents/eunice.yml` only).
- Kept flow mappings intact and verified mapped paths exist in the repository.

## [0.2.6] - 2026-02-24
### Changed
- Converted the AI Catalog to a true single-agent catalog (`agents/eunice.yml` as the public agent).
- Consolidated the former specialist system prompts (`collector`, `graph`, `planner`, `actioner`, `fixer`) into the single `eunice` system prompt in full, preserving them verbatim in labeled sections.
- Synced `agents/agent.yml.template` to the consolidated single-agent `eunice` prompt.
- Updated README and Wiki architecture/setup docs to present Eunice as one agent with modes and event-driven flows.
- Added explicit flow-trigger behavior guidance (mention/assign triggers and `Automate -> Sessions` debugging).

## [0.2.4] - 2026-02-24
### Changed
- Updated changelog and GitLab Wiki to document the autofix capability, rollout guidance, and latest architecture/flows.

## [0.2.5] - 2026-02-24
### Changed
- Added a `Known limitations` section to `README.md` to set expectations for early users.
- Added `Known Limitations` page to the GitLab Wiki and linked it from the wiki home page.

## [0.2.3] - 2026-02-24
### Added
- `agents/eunice-fixer.yml` for safe, gated automated remediation (draft MR only, test-verified).
- `flows/eunice-autofix.yml` to run triage -> plan -> fix -> verify -> draft MR.

### Changed
- Upgraded `flows/eunice.yml` and `flows/eunice-mr-review.yml` inline prompts to match standalone agent rigor.
- Updated `flows/eunice-weekly-triage.yml` consistency around assumptions/default labeling.
- Synced `agents/agent.yml.template` and `flows/flow.yml.template` to current Eunice architecture.
- Refreshed `README.md` for autofix capability and product positioning (without hackathon/prize framing).

## [0.2.2] - 2026-02-24
### Added
- `CHANGELOG.md` in the main catalog repo.
- GitLab Wiki pages: `Home`, `Setup`, `Architecture`, and `Changelog`.

## [0.2.1] - 2026-02-24
### Added
- Root `eunice.yml` runtime configuration template for cost, carbon, sprint, threshold, Nia, and GitLab settings.

### Changed
- Strengthened `eunice-collector` prompt with explicit CI duration collection and confidence rules.
- Strengthened `eunice-graph` prompt with propagation math and CO2 calculation methodology.
- Strengthened `eunice-planner` prompt with budget-aware sprint planning, ROI formula requirements, and defer/escalation logic.
- Strengthened `eunice-actioner` prompt with lifecycle memory (duplicate avoidance and repeat-flag escalation).
- Upgraded weekly and monthly flow prompts to match standalone agent rigor.
- Rewrote `README.md` with clearer product positioning, trust model, and example outputs.

## [0.2.0] - 2026-02-24
### Added
- Multi-agent Eunice architecture in GitLab AI Catalog format:
  - `eunice`, `eunice-collector`, `eunice-graph`, `eunice-planner`, `eunice-actioner`
- Multi-flow architecture:
  - `eunice`, `eunice-mr-review`, `eunice-weekly-triage`, `eunice-monthly-balance-sheet`
- Strict output contracts with `analysis_mode`, `confidence`, measured vs estimated signal handling.

### Changed
- Repositioned Eunice as technical debt intelligence (not generic code review).
- Added Nia-first (recommended/optional) behavior in prompts while preserving validator-safe built-in tool declarations.

## [0.1.0] - 2026-02-23
### Added
- Initial GitLab AI Catalog-compatible `eunice` agent and `eunice` flow.
- Minimal catalog repo structure (`agents/`, `flows/`, `README.md`, `LICENSE`).

### Changed
- Reduced toolsets to conservative built-in GitLab tools for schema compatibility.
