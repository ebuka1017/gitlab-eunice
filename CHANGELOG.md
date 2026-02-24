# Changelog

All notable changes to Eunice are documented in this file.

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
