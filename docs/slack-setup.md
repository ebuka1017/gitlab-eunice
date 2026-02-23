# slack setup (optional)

## create the app

1. Create an app at https://api.slack.com/apps
2. Add bot scopes:
   - `chat:write`
   - `channels:history`
   - `app_mentions:read`
3. Create an app-level token with `connections:write`
4. Install the app to your workspace

## add GitLab variables

- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `SLACK_TEAM_ID`

## validate

1. Invite the bot: `/invite @eunice`
2. Trigger a Eunice flow
3. Confirm a Slack message is posted
