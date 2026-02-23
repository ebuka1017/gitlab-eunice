# eunice setup guide

## prerequisites

- git
- python 3.9+
- pip3
- node.js + npx (for nia)
- a GitLab project you can push to

## install

```bash
curl -fsSL https://raw.githubusercontent.com/ebuka1017/eunice/main/install.sh | bash
```

## required GitLab CI/CD variable

Add this in `Settings -> CI/CD -> Variables`:

- `NIA_API_KEY`

## enable GitLab Duo agents

Go to `Automate -> AI catalog`, search `eunice`, and enable:

- `eunice-debt-detector`
- `eunice-impact-analyzer`
- `eunice-orchestrator`

## test before demo

1. Create a branch with a small intentional debt example (nested conditionals / missing tests / TODOs).
2. Push and open a merge request.
3. Confirm `eunice-mr-review` triggers.
4. Check the MR comment and created issue (if thresholds are met).
5. Record the flow for your demo video.

## common issues

- No findings: repo may not be indexed in Nia, or `NIA_API_KEY` is missing.
- No GitLab metrics: ensure the agent can read commits/issues/pipelines with `CI_JOB_TOKEN`.
- Package install fails in agent container: keep `.gitlab/duo/agent-config.yml` pointing to the GitHub subdirectory install.
