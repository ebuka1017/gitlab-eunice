# eunice: technical debt guardian

**calculate the exact dollar cost of every messy file in your codebase.**

eunice is an ai agent that finds expensive technical debt and tells you exactly how to fix it. powered by real gitlab data, not guesses.

---

## what eunice does

- 💰 **calculates real costs** using gitlab commit data, mr times, bug fixes, and ci/cd metrics
- 📊 **ranks by roi** - shows impact vs effort for every debt item
- 🎯 **creates actionable issues** with step-by-step fix instructions
- 📈 **tracks progress** with monthly impact reports
- 🌱 **measures sustainability** - carbon footprint reduction from optimizations

---

## the problem

technical debt costs companies **$2.41 trillion annually**. developers waste **23-42%** of their week dealing with bad code. but most tools just say "this is complex" without showing the business impact.

**eunice is different:**

| other tools | eunice |
|-------------|--------|
| "this code is complex" | "$9,440/year cost based on 12 commits, 14min avg review time" |
| vague suggestions | transparent breakdown with gitlab links to verify |
| point-in-time analysis | monthly reports showing debt paid + hours saved |
| generic priorities | roi-driven ranking (impact / effort) |

---

## installation

### one-command setup

```bash
curl -fsSL https://raw.githubusercontent.com/ebuka1017/eunice/main/install.sh | bash
```

**what this does:**
1. installs eunice data engine (python package)
2. creates `.gitlab/duo/` workflows
3. sets up nia integration (required)
4. creates `eunice.yml` config file
5. optionally configures slack

### manual setup

see [setup guide](docs/setup-guide.md) for detailed instructions.

---

## quick start

### 1. run installer
```bash
cd your-gitlab-project
curl -fsSL https://raw.githubusercontent.com/ebuka1017/eunice/main/install.sh | bash
```

### 2. add nia api key to gitlab
```
settings → ci/cd → variables
add: NIA_API_KEY = your-key-here
```

### 3. enable eunice agents
```
automate → ai catalog
search: "eunice"
enable all three agents
```

### 4. commit and push
```bash
git add .gitlab/ eunice.yml
git commit -m "feat: add eunice"
git push
```

### 5. create merge request
eunice analyzes automatically! 🎉

---

## example output

### merge request comment
```markdown
## 💰 technical debt analysis: auth.py

### annual impact: $5,040

#### measured from gitlab (last 30 days)
| metric | value | source |
|--------|-------|--------|
| commits | 12 | [see commits]({commit_links}) |
| avg mr review | 14 min | [mrs]({mr_links}) |
| bug fix hours (annual tracked) | 18 hrs | [issues]({issue_links}) |
| ci failures | 2 | [pipelines]({pipeline_links}) |

#### cost breakdown
| category | calculation | annual cost |
|----------|-------------|-------------|
| review overhead | 12/mo × 14min × $75/hr × 12mo | $1,890 |
| bug fixes | 18hrs × $75/hr | $1,350 |
| ci failures | 2/mo × 1hr × $75/hr × 12mo | $1,800 |
| **total** | | **$5,040** |

#### assumptions (from eunice.yml)
- dev hourly rate: $75 (edit in eunice.yml)
- avg ci failure debug: 1 hour

#### fix effort: 6 hours
**roi: 11.2x** (save $5,040 for $450 investment)

#### recommended fix
1. refactor validate_user() (lines 67-89)
2. extract nested conditionals
3. add unit tests

---
📊 priority score: 9.2/10
```

---

## how it works

### the three agents

**1. eunice-debt-detector** (claude sonnet 4.5)
- scans code for complexity, dead code, outdated dependencies
- uses nia for semantic code search
- returns findings with evidence

**2. eunice-impact-analyzer** (claude opus 4.6)
- queries gitlab api for real metrics
- calculates costs using transparent formulas
- ranks by roi (impact / effort)

**3. eunice-orchestrator** (claude opus 4.6)
- creates gitlab issues with fix steps
- posts to slack (optional)
- tracks progress over time

### the workflows

**eunice-mr-review** → runs on every merge request  
**eunice-weekly-audit** → comprehensive scan every monday  
**eunice-impact-report** → monthly progress report

---

## configuration

edit `eunice.yml` to customize:

```yaml
cost_assumptions:
  dev_hourly_rate: 75  # your team's average
  compute_cost_per_minute: 0.02  # gitlab runner cost

effort_assumptions:
  avg_bug_fix_hours: 3
  avg_refactor_hours_per_100_loc: 2

thresholds:
  create_issue_annual_cost: 5000  # create issue if cost >= $5k
  create_issue_roi: 50  # or if roi >= 50x
```

---

## slack integration (optional)

eunice can post to slack and respond to commands like:

```
@agent_eunice analyze auth.py
@agent_eunice what's our weekly debt?
@agent_eunice create weekly report
```

### setup instructions

1. **create slack app**: https://api.slack.com/apps
2. **add bot scopes**: 
   - `chat:write`
   - `channels:history`
   - `app_mentions:read`
3. **create app-level token** with `connections:write`
4. **install to workspace**
5. **add tokens to gitlab ci/cd variables**:
   ```
   SLACK_BOT_TOKEN = xoxb-...
   SLACK_APP_TOKEN = xapp-...
   SLACK_TEAM_ID = T...
   ```
6. **invite bot to channel**: `/invite @eunice`

detailed guide: [slack setup](docs/slack-setup.md)

---

## nia integration (required)

eunice uses nia as its source of truth for codebase analysis.

### why nia?

- **reduces hallucinations** by 43%
- **provides full context** (not truncated like web search)
- **indexes your actual code** for accurate pattern matching

### setup nia

```bash
# install nia
npx nia-wizard@latest --remote

# index your repository
npx nia index gitlab.com/your-org/your-repo

# add api key to gitlab
# settings → ci/cd → variables
# NIA_API_KEY = your-key
```

see [nia documentation](https://trynia.ai/docs) for more.

---

## data transparency

### what's measured (from gitlab)
- commit frequency per file
- merge request review times
- bug issue time tracking
- pipeline durations and failures

### what's configured (by you)
- developer hourly rate
- ci/cd compute costs
- effort estimates

**every metric shows both:**
```json
{
  "annual_cost": 9440,
  "measured_from_gitlab": {
    "commits": [link],
    "mrs": [link],
    "bugs": [link]
  },
  "assumptions_used": {
    "dev_rate": 75,
    "source": "eunice.yml"
  }
}
```

---

## faq

**q: does eunice work with self-hosted gitlab?**  
a: yes! just update `gitlab_config.url` in eunice.yml

**q: can i use different models?**  
a: yes, edit the `model` field in workflow yamls

**q: what if my team doesn't track time in issues?**  
a: eunice estimates from commit frequency + review times

**q: how accurate are the cost calculations?**  
a: they use your gitlab data + your config assumptions. edit eunice.yml for accuracy.

**q: does this work for other languages besides python?**  
a: yes! eunice analyzes any language gitlab tracks.

**q: can i disable slack integration?**  
a: yes, it's optional. just don't add slack tokens.

---

## contributing

contributions welcome! open an issue or PR.

---

## license

mit license - see [LICENSE](LICENSE)

---

## support

- 📚 [documentation](docs/)
- 💬 [github issues](https://github.com/ebuka1017/eunice/issues)
- 🔗 [gitlab duo docs](https://docs.gitlab.com/user/duo_agent_platform/)

---

## acknowledgments

built with:
- [gitlab duo agent platform](https://about.gitlab.com/gitlab-duo/)
- [anthropic claude](https://www.anthropic.com/)
- [nia](https://trynia.ai/) - codebase analysis
- [python-gitlab](https://python-gitlab.readthedocs.io/)

---

**made with ❤️ for developers who hate technical debt**

*eunice: because your codebase deserves better than "TODO: refactor this later"*
