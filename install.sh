#!/bin/bash
set -e

echo "🌱 installing eunice - technical debt guardian"
echo ""

###############################
# 1. check prerequisites
###############################
echo "[1/7] checking prerequisites..."

command -v git >/dev/null 2>&1 || { echo "❌ git required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 required"; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "❌ pip3 required"; exit 1; }

echo "   ✓ all prerequisites met"

###############################
# 2. detect gitlab repo
###############################
echo "[2/7] detecting gitlab repository..."

# check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "❌ not in a git repository"
  echo "   run this from your gitlab project root"
  exit 1;
fi

# check if remote is gitlab
git_remote=$(git remote get-url origin 2>/dev/null || echo "")
if [[ -z "$git_remote" ]]; then
  echo "❌ no git remote found"
  exit 1
fi

if [[ ! $git_remote == *"gitlab.com"* ]] && [[ ! $git_remote == *"gitlab"* ]]; then
  echo "⚠️  remote doesn't look like gitlab"
  echo "   detected: $git_remote"
  read -p "   continue anyway? (y/n): " continue_anyway
  if [[ $continue_anyway != "y" ]]; then
    exit 1
  fi
fi

# extract project path
if [[ $git_remote =~ gitlab\.com[:/](.+)\.git ]]; then
  repo_path="${BASH_REMATCH[1]}"
  echo "   ✓ detected gitlab repo: $repo_path"
elif [[ $git_remote =~ gitlab[^/]*/(.+)\.git ]]; then
  repo_path="${BASH_REMATCH[1]}"
  echo "   ✓ detected gitlab repo: $repo_path"
else
  echo "   ⚠️  couldn't auto-detect repo path"
  read -p "   enter gitlab project path (owner/repo): " repo_path
fi

###############################
# 3. install python package
###############################
echo "[3/7] installing eunice data engine..."

# check if already installed
if python3 -c "import eunice" 2>/dev/null; then
  echo "   ✓ eunice already installed (skipping)"
else
  # install from github
  echo "   → installing from github.com/ebuka1017/eunice..."
  pip3 install --break-system-packages git+https://github.com/ebuka1017/eunice.git#subdirectory=eunice-data-engine
  
  echo "   ✓ eunice data engine installed"
fi

###############################
# 4. setup .gitlab/duo structure
###############################
echo "[4/7] setting up gitlab duo workflows..."

# create directory structure
mkdir -p .gitlab/duo/flows

# download workflow files from github
base_url="https://raw.githubusercontent.com/ebuka1017/eunice/main"

echo "   → downloading mcp.json..."
curl -fsSL "$base_url/.gitlab/duo/mcp.json" -o .gitlab/duo/mcp.json

echo "   → downloading agent-config.yml..."
curl -fsSL "$base_url/.gitlab/duo/agent-config.yml" -o .gitlab/duo/agent-config.yml

echo "   → downloading flow configs..."
curl -fsSL "$base_url/.gitlab/duo/flows/eunice-mr-review.yaml" -o .gitlab/duo/flows/eunice-mr-review.yaml
curl -fsSL "$base_url/.gitlab/duo/flows/eunice-weekly-audit.yaml" -o .gitlab/duo/flows/eunice-weekly-audit.yaml
curl -fsSL "$base_url/.gitlab/duo/flows/eunice-impact-report.yaml" -o .gitlab/duo/flows/eunice-impact-report.yaml

echo "   ✓ workflow files created in .gitlab/duo/"

###############################
# 5. create config file
###############################
echo "[5/7] creating configuration file..."

if [ -f eunice.yml ]; then
  echo "   ⚠️  eunice.yml already exists (skipping)"
else
  # download config template
  curl -fsSL "$base_url/config/eunice.yml.template" -o eunice.yml
  
  # update with detected repo path
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macos
    sed -i '' "s|project_id: null|project_id: \"$repo_path\"|g" eunice.yml
  else
    # linux
    sed -i "s|project_id: null|project_id: \"$repo_path\"|g" eunice.yml
  fi
  
  echo "   ✓ eunice.yml created (edit to customize rates)"
fi

###############################
# 6. setup nia (REQUIRED)
###############################
echo "[6/7] nia integration setup (REQUIRED)..."
echo ""
echo "⚠️  eunice requires nia for codebase analysis"
echo ""

# check if node/npx available
if ! command -v npx >/dev/null 2>&1; then
  echo "❌ node.js/npx required for nia"
  echo ""
  echo "install node.js from: https://nodejs.org/"
  echo "then run: npx nia-wizard@latest --remote"
  echo ""
  echo "after nia setup, add NIA_API_KEY to gitlab ci/cd variables"
  exit 1
fi

# check if nia already configured
if [ -f ~/.config/nia/api_key ]; then
  nia_key=$(cat ~/.config/nia/api_key)
  echo "   ✓ nia api key found: ${nia_key:0:8}..."
  
  read -p "   use existing nia key? (y/n): " use_existing
  
  if [[ $use_existing != "y" ]]; then
    npx nia-wizard@latest --remote
  fi
else
  echo "   → running nia wizard..."
  npx nia-wizard@latest --remote
fi

# verify api key saved
if [ ! -f ~/.config/nia/api_key ]; then
  echo "❌ nia setup incomplete"
  echo "   run: npx nia-wizard@latest --remote"
  exit 1
fi

nia_key=$(cat ~/.config/nia/api_key)
echo "   ✓ nia configured: ${nia_key:0:8}..."

# offer to index repo
echo ""
read -p "   index this repository with nia? (y/n): " index_repo

if [[ $index_repo == "y" ]]; then
  echo "   → indexing $repo_path (takes 5-15 min)..."
  
  # install nia-plugin if not exists
  if [ ! -d ~/.eunice/nia-plugin ]; then
    mkdir -p ~/.eunice
    git clone --quiet https://github.com/nozomio-labs/nia-plugin.git ~/.eunice/nia-plugin 2>/dev/null || true
  fi
  
  # run indexing (if plugin available)
  if [ -d ~/.eunice/nia-plugin ]; then
    cd ~/.eunice/nia-plugin/scripts
    ./repos-index.sh "$repo_path" 2>/dev/null || {
      echo "   ⚠️  indexing failed - you can index manually later"
      echo "   run: cd ~/.eunice/nia-plugin/scripts && ./repos-index.sh \"$repo_path\""
    }
    cd "$OLDPWD"
  fi
  
  echo "   ✓ repository indexed"
else
  echo "   ⏭️  skipped indexing (you can do this later)"
  echo "   run: npx nia index $repo_path"
fi

###############################
# 7. setup slack (OPTIONAL)
###############################
echo ""
echo "[7/7] slack integration (optional)..."
echo ""
echo "slack integration enables:"
echo "  - notifications in #eunice-alerts"
echo "  - interactive commands (@agent_eunice)"
echo ""
read -p "setup slack now? (y/n): " setup_slack

if [[ $setup_slack == "y" ]]; then
  echo ""
  echo "📋 slack setup instructions:"
  echo ""
  echo "1. create slack app at: https://api.slack.com/apps"
  echo "2. add bot scopes: chat:write, channels:history, app_mentions:read"
  echo "3. add app-level token with connections:write"
  echo "4. install to workspace"
  echo ""
  echo "you'll need three tokens:"
  echo "  - SLACK_BOT_TOKEN (xoxb-...)"
  echo "  - SLACK_APP_TOKEN (xapp-...)"
  echo "  - SLACK_TEAM_ID (T...)"
  echo ""
  echo "add these to gitlab ci/cd variables after installation"
  echo ""
  echo "detailed guide: https://github.com/ebuka1017/eunice#slack-setup"
else
  echo "   ⏭️  skipped slack setup"
fi

###############################
# installation complete
###############################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ eunice installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 next steps:"
echo ""
echo "1️⃣  add nia api key to gitlab:"
echo "   → go to: settings → ci/cd → variables"
echo "   → add variable: NIA_API_KEY"
echo "   → value: $(cat ~/.config/nia/api_key)"
echo "   → protected: ✓, masked: ✓"
echo ""
if [[ $setup_slack == "y" ]]; then
echo "2️⃣  (optional) add slack tokens:"
echo "   → SLACK_BOT_TOKEN = xoxb-..."
echo "   → SLACK_APP_TOKEN = xapp-..."
echo "   → SLACK_TEAM_ID = T..."
echo ""
fi
echo "3️⃣  enable eunice agents in gitlab:"
echo "   → go to: automate → ai catalog"
echo "   → search: 'eunice'"
echo "   → enable all three agents:"
echo "      • eunice-debt-detector"
echo "      • eunice-impact-analyzer"
echo "      • eunice-orchestrator"
echo ""
echo "4️⃣  commit and push:"
echo "   git add .gitlab/ eunice.yml"
echo "   git commit -m 'feat: add eunice technical debt guardian'"
echo "   git push"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 eunice will analyze your next merge request automatically!"
echo ""
echo "📚 docs: https://github.com/ebuka1017/eunice"
echo "💬 support: https://github.com/ebuka1017/eunice/issues"
echo "⚙️ config: edit eunice.yml to customize rates"
echo ""
