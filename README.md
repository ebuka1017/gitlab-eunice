# Eunice

**Technical debt has a real cost. Eunice calculates it, maps it, and tells you exactly what to fix first.**

Most teams know they have technical debt. Nobody knows how much it actually costs, which files are the worst offenders, or what to fix on Monday morning.

Eunice answers all three questions — using real GitLab data, not guesses.

---

## What makes Eunice different

| Other tools | Eunice |
|-------------|--------|
| "This code is complex" | "$9,440/yr cost — 12 commits × 14min review × $75/hr × 12mo = $1,890 + ..." |
| Vague suggestions | Transparent formula, every number sourced or labeled as assumed |
| Point-in-time analysis | Monthly balance sheet: debt added, debt paid down, net trend |
| Flat file list | Dependency-propagation graph — root nodes infect downstream files |
| Ignores CI waste | Wasted runner minutes → energy → CO₂ (Eco-CI methodology) |
| Always creates issues | "Do nothing" is a first-class output when ROI is weak |

---

## Architecture

### Agents

| Agent | Role |
|-------|------|
| `eunice` | General-purpose debt triage (chat-friendly, single agent) |
| `eunice-collector` | Gathers measurable GitLab signals — no estimation, no hallucination |
| `eunice-graph` | Builds propagation-aware debt map with cost and CO₂ math |
| `eunice-planner` | Turns debt graph into a budget-aware sprint plan |
| `eunice-actioner` | Writes MR comments and issues, manages lifecycle memory |
| `eunice-fixer` | **Executes the fix** — edits files, runs tests, opens a draft MR for human review |

### Flows

| Flow | Trigger | Purpose |
|------|---------|---------|
| `eunice` | On demand / chat | Full debt triage: collector → graph → planner → actioner |
| `eunice-mr-review` | On MR open | Fast path: collector → graph → actioner |
| `eunice-weekly-triage` | Every Monday | Repo-wide sprint plan as a GitLab issue |
| `eunice-monthly-balance-sheet` | Monthly | Debt added vs paid down, CO₂ trend report |
| `eunice-autofix` | On demand | **Full remediation**: triage → plan → fix → verify tests → draft MR |

---

## Trust model — how Eunice avoids hallucinated numbers

Every metric in every Eunice output is labeled as one of:

- **`measured`** — fetched directly from GitLab APIs (commits, MR durations, issue time tracking, pipeline job durations)
- **`estimated`** — derived from assumptions in `eunice.yml`

Every output also includes:
- `analysis_mode`: `nia_enhanced` or `gitlab_only`
- `confidence`: `high`, `medium`, or `low`
- `assumptions`: explicit list of every default used, with its source

If Eunice doesn't have enough data, it says so and reports a data gap rather than fabricating a number.

---

## Cost calculation

```
annual_dev_cost =
  (commits_30d × avg_mr_review_min/60 × dev_hourly_rate × 12)   ← MEASURED × ASSUMED
  + (bug_issues_count × avg_bug_fix_hours × dev_hourly_rate)     ← MEASURED × ASSUMED
  + (failed_pipelines_30d × 1.0hr × dev_hourly_rate × 12)       ← MEASURED × ASSUMED
```

All `dev_hourly_rate` and effort defaults come from `eunice.yml` — your config, your numbers.

---

## Dependency propagation

A file's true cost isn't just its own signals. If 9 other files import it, fixing it fixes all of them.

```
propagated_cost = direct_cost × propagation_multiplier
propagation_multiplier = min(1 + (dependent_count × 0.15), 4.0)
```

**Example:**
> `auth_utils.py` direct cost: **$2,100/yr**
> Dependents: **9 files**
> Propagation multiplier: **2.35×**
> **True organizational cost: $4,935/yr**
> Fix this first. Unlocks improvements in 4 downstream files automatically.

---

## CO₂ / CI waste calculation

Wasted CI minutes are both a cost problem and a carbon problem.

```
energy_kwh       = (wasted_runner_seconds / 3600) × runner_watts / 1000
co2_grams/month  = energy_kwh × grid_intensity_gco2_per_kwh
co2_kg/year      = co2_grams/month × 12 / 1000
```

**Methodology:** [Eco-CI estimation model](https://green-coding.io/projects/eco-ci/)
**Defaults:** 100W runner, 350 gCO₂/kWh global average
**Override:** set `runner_region` in `eunice.yml` for your actual grid intensity

All carbon values are labeled with their assumptions. Small numbers are fine — the value is the trend.

---

## Example output

```markdown
## 🔍 Eunice Debt Triage: `auth_utils.py`

**Annual Impact:** $4,935 (propagated) | **ROI:** 13.2x | **Confidence:** high (gitlab_only)

### Measured Signals (from GitLab)
| Signal | Value | Source |
|--------|-------|--------|
| Commits (30d) | 12 | list_commits |
| Avg MR review | 14 min | MR timestamps |
| Bug issues | 3 | gitlab_issue_search |
| Failed pipelines (30d) | 2 | get_pipeline_errors |
| Wasted runner time | 2,580s/mo | get_job_logs |

### Cost Breakdown
| Category | Calculation | Annual Cost |
|----------|-------------|-------------|
| Review overhead | 12 × 14min/60 × $75 × 12 | $1,890 |
| Bug fixes | 3 × 3hrs × $75 | $675 |
| CI failures | 2 × 1hr × $75 × 12 | $1,800 |
| Propagation (2.35×) | $4,365 × 2.35 | — |
| **Direct total** | | **$4,365** |
| **Propagated total** | | **$4,935** |

### CI Waste & Carbon
- Wasted runner time: 43 min/month
- Estimated energy: 0.072 kWh/month
- Estimated CO₂: **0.30 kg/year**
- *Eco-CI methodology | 100W runner, 350 gCO₂/kWh global average (override in eunice.yml)*

### Assumptions (from eunice.yml)
- dev_hourly_rate: $75 | avg_bug_fix_hours: 3 | runner_watts: 100

### Propagation Graph
graph TD
  auth_utils.py["auth_utils.py $4,935/yr 🔴"] -->|imports| user_service.py
  auth_utils.py -->|imports| session_manager.py
  auth_utils.py -->|imports| api_gateway.py

### Recommended Fix (6hrs, ROI: 13.2x)
1. Refactor validate_user() lines 67-89
2. Extract nested conditionals into named functions
3. Add unit tests for 3 uncovered branches

---
📊 Priority: high | 🔁 Times flagged: 1 | 💡 Sprint plan in linked issue
```

---

## Issue lifecycle memory

Eunice tracks its own findings over time:

- Before creating an issue: checks for existing `eunice-debt` issues on the same file
- If an open issue exists: adds a note instead of creating a duplicate
- If the same file is flagged 3+ times: escalates to `eunice-critical` and recommends leadership visibility
- Monthly balance sheet tracks debt added vs paid down as a running ledger

---

## Automated remediation (eunice-autofix)

Eunice doesn't just tell you what to fix — it can fix it.

The `eunice-autofix` flow runs the full triage pipeline and, for items that pass all safety gates, **writes the code changes, runs your test suite, and opens a draft MR** for your team to review and merge.

### Safety gates

Eunice will only attempt a fix if **all five gates pass**:

| Gate | Requirement | Why |
|------|-------------|-----|
| 1 | `confidence = high` | Only act on findings with 4+ measured signal types |
| 2 | `urgency = high or critical` | Only act on things that materially affect the team |
| 3 | `has_tests = true` | Tests must exist to verify the fix didn't break anything |
| 4 | `effort_hours_est <= 8` | Only contained, scoped changes — not multi-day refactors |
| 5 | `debt_type ≠ architecture_antipattern` | Structural changes require human design decisions |

If any gate fails, the fixer stops, reports which gate failed and why, and leaves the manual sprint plan for the developer to action instead.

### What the fixer does

1. Reads the target file and all dependent files
2. Runs your existing tests to confirm they pass **before touching anything**
3. Applies the targeted fix (refactor, test addition, deduplication, etc.)
4. Runs tests again to verify nothing broke
5. If tests fail after the fix: **automatically reverts** and reports what failed
6. If tests pass: opens a **draft MR** with full cost/carbon breakdown, change description, and downstream impact

### What Eunice will never do

- Auto-merge — every change requires human approval
- Touch a file without a passing test suite
- Make architectural decisions (structural refactors stay in the backlog)
- Open an MR with failing tests

### Example

```
Run eunice-autofix on src/auth/

→ Collector: 5 signal types found, confidence=high
→ Graph: auth_utils.py root node, $4,935/yr propagated cost
→ Planner: rank 1 item passes all 5 gates — autofix_eligible=true
→ Fixer: tests pass pre-change ✅
         refactored validate_user() lines 67-89
         extracted 3 nested conditionals
         tests pass post-change ✅
→ Draft MR !247 opened: "draft(eunice): fix high_complexity in auth_utils.py [high]"
   Estimated savings: $4,935/yr | ROI: 13.2x | Unlocks: 3 downstream files
```

---

## Setup

### 1. Install from AI Catalog
```
GitLab project → Automate → AI Catalog → search "eunice" → enable
```

### 2. Add `eunice.yml` to your project root
Copy and edit the config file:
```yaml
cost:
  dev_hourly_rate: 75       # your team's average
  ci_cost_per_minute: 0.005

carbon:
  runner_watts: 100
  grid_intensity_gco2_per_kwh: 350  # find yours at ember-climate.org
  runner_region: "us-east-1"

sprint:
  debt_budget_hours: 20     # hours your team will spend on debt per sprint

thresholds:
  create_issue_min_annual_cost: 3000
  create_issue_min_confidence: medium
  repeat_flag_escalation_count: 3
```

### 3. (Recommended) Add Nia for better dependency analysis
```bash
npx nia-wizard@latest --remote
npx nia index gitlab.com/your-org/your-repo
# Add NIA_API_KEY to GitLab CI/CD variables
```

### 4. Schedule flows
```yaml
# .gitlab-ci.yml
eunice-weekly:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'  # schedule for every Monday
  # trigger eunice-weekly-triage flow

eunice-monthly:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'  # schedule for 1st of month
  # trigger eunice-monthly-balance-sheet flow
```

---

## Nia integration (recommended, optional)

Without Nia, Eunice uses grep and file patterns for dependency discovery (`analysis_mode: gitlab_only`).
With Nia, Eunice uses semantic code search for accurate dependency graphs (`analysis_mode: nia_enhanced`).

The difference is visible in every output — confidence is higher, propagation edges are more accurate, and dead-code findings have fewer false positives.

Eunice never pretends Nia is available when it isn't. `analysis_mode` is always honest.

---

## Configuration reference

See [`eunice.yml`](eunice.yml) for the full config file with all options and documented defaults.

---

## FAQ

**Q: Does Eunice work with self-hosted GitLab?**
A: Yes — set `gitlab.url` in `eunice.yml`.

**Q: What if my team doesn't track time in issues?**
A: Eunice falls back to `avg_bug_fix_hours` from `eunice.yml` and labels those values as ESTIMATED.

**Q: How accurate are the cost numbers?**
A: Commit counts, MR durations, and pipeline failures are exact (from GitLab APIs). Effort estimates are from your `eunice.yml` config — the more you calibrate it, the more accurate the output.

**Q: What if Eunice finds nothing worth fixing?**
A: It says so. "Do nothing" is a first-class output. A tool that always finds problems isn't a prioritization tool.

**Q: How does CO₂ calculation work?**
A: Eco-CI methodology: runner duration × power draw → energy → grid carbon intensity → grams CO₂. All assumptions are labeled and overridable.

---

## Known limitations

- **Prompt-driven behavior can vary by repo shape.** Eunice uses strict output contracts, but unusual repo layouts or weak signals can still reduce output quality.
- **`gitlab_only` mode is weaker than `nia_enhanced`.** Without Nia, dependency graphs and dead-code detection rely on grep/pattern heuristics and may have lower confidence.
- **Cost/ROI quality depends on calibration.** If `eunice.yml` assumptions are unrealistic (hourly rate, fix effort, pipeline debug time), the prioritization math will be directionally useful but numerically off.
- **Autofix is pilot-grade, not default-safe for all repos.** `eunice-autofix` should start on test-covered repos with draft-MR review only, and be limited to safer debt types before expanding scope.
- **Tool availability varies by GitLab runtime.** Some environments may not expose the same built-in tools, which can reduce feature coverage or force more conservative fallbacks.
- **Weak test suites limit remediation confidence.** If tests are flaky, missing, or too narrow, `eunice-fixer` may correctly refuse to proceed or produce lower-confidence outcomes.

---

## License

MIT — see [LICENSE](LICENSE)

---

## Built with

- [GitLab Duo Agent Platform](https://docs.gitlab.com/user/duo_agent_platform/)
- [Anthropic Claude Sonnet 4.6](https://www.anthropic.com/)
- [Nia](https://trynia.ai/) — semantic codebase analysis (optional)
- [Eco-CI](https://green-coding.io/projects/eco-ci/) — CI carbon estimation methodology
- [Ember Climate](https://ember-climate.org/data/data-tools/carbon-intensity-tool/) — grid carbon intensity data

---

*Eunice: because "TODO: fix later" has a price tag.*
