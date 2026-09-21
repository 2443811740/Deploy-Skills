#!/usr/bin/env bash
set -euo pipefail

RESOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "${1:-}" ]; then
  echo "ERROR: missing project root" >&2
  echo "Usage: bash setup.sh <project-root>" >&2
  exit 1
fi

if ! PROJECT_ROOT="$(cd "$1" 2>/dev/null && pwd)"; then
  echo "ERROR: project root does not exist: $1" >&2
  exit 1
fi

DEPLOY_SRC="$RESOURCE_DIR/deploy"
DEPLOY_DST="$PROJECT_ROOT/.deploy"

if [ ! -d "$DEPLOY_SRC" ]; then
  echo "ERROR: resource directory not found: $DEPLOY_SRC" >&2
  exit 1
fi

mkdir -p "$DEPLOY_DST"

for directory in docs skills; do
  if [ -d "$DEPLOY_SRC/$directory" ]; then
    mkdir -p "$DEPLOY_DST/$directory"
    cp -R "$DEPLOY_SRC/$directory/." "$DEPLOY_DST/$directory/"
    echo "  [ok] $directory/"
  fi
done

for file in candidate-drop.conf DEPLOY.md skill-index.json VERSION; do
  if [ -f "$DEPLOY_SRC/$file" ]; then
    cp "$DEPLOY_SRC/$file" "$DEPLOY_DST/$file"
    echo "  [ok] $file"
  fi
done

OBSOLETE_CANDIDATE_TEMPLATE="$DEPLOY_DST/skills/governance/alignment-skill-journal/assets/candidate-journal.md.template"
if [ -f "$OBSOLETE_CANDIDATE_TEMPLATE" ]; then
  rm "$OBSOLETE_CANDIDATE_TEMPLATE"
  echo "  [ok] obsolete candidate journal template removed"
fi

LOCAL_DIR="$DEPLOY_DST/local"
LEGACY_CANDIDATE_JOURNAL="$LOCAL_DIR/alignment-skill-candidates.md"
mkdir -p "$LOCAL_DIR"
rm -f "$LOCAL_DIR/source-repository"
if [ -f "$LEGACY_CANDIDATE_JOURNAL" ]; then
  if awk '
    $0 == "<!-- Append candidate entries below this line. -->" { marker = 1; next }
    marker && $0 !~ /^[[:space:]]*$/ { content = 1 }
    END { exit !(marker && !content) }
  ' "$LEGACY_CANDIDATE_JOURNAL"; then
    rm "$LEGACY_CANDIDATE_JOURNAL"
    echo "  [ok] empty legacy candidate journal removed"
  else
    echo "  [warn] legacy candidate journal retained; new candidates use the shared drop directory: $LEGACY_CANDIDATE_JOURNAL" >&2
  fi
fi

MARKER='# Deployment Workspace Rules'
BEGIN_MARKER='<!-- BEGIN DEPLOYMENT WORKSPACE RULES -->'
END_MARKER='<!-- END DEPLOYMENT WORKSPACE RULES -->'
ROUTING_RULES="$BEGIN_MARKER
$MARKER

If the user request involves deployment, follow the project rules in .deploy/DEPLOY.md.
At the start of every new conversation, before the first development action, follow .deploy/skills/governance/deployment-session-intake/SKILL.md. Ask for the task scope, exact build command, Python/BC server and inference command, deployment method, target-board environment and run command, and acceptance criteria. Reuse answers only within the current conversation.
Use .deploy/skill-index.json to locate the matching skill, and read that skill before execution.
After every development task governed by .deploy, evaluate whether the work produced a new reusable alignment skill candidate. Follow .deploy/skills/governance/alignment-skill-journal/SKILL.md and create one descriptively named Markdown file in the configured shared candidate directory when the candidate gate is satisfied.
$END_MARKER"

INJECTED=0
for file in CLAUDE.md AGENTS.md; do
  target="$PROJECT_ROOT/$file"
  if [ -f "$target" ]; then
    temporary_file="$(mktemp)"
    if grep -qF "$BEGIN_MARKER" "$target" && grep -qF "$END_MARKER" "$target"; then
      awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" -v rules="$ROUTING_RULES" '
        $0 == begin {
          print rules
          replacing = 1
          next
        }
        replacing && $0 == end {
          replacing = 0
          next
        }
        !replacing { print }
      ' "$target" > "$temporary_file"
      mv "$temporary_file" "$target"
      echo "  [ok] $file (rules updated)"
    elif grep -qF "$MARKER" "$target"; then
      awk -v marker="$MARKER" -v rules="$ROUTING_RULES" '
        $0 == marker {
          print rules
          replacing = 1
          next
        }
        replacing {
          if ($0 == "If the user request involves deployment, follow the project rules in .deploy/DEPLOY.md." ||
              $0 == "Use .deploy/skill-index.json to locate the matching skill, and read that skill before execution." ||
              $0 ~ /^[[:space:]]*$/) {
            next
          }
          replacing = 0
        }
        { print }
      ' "$target" > "$temporary_file"
      mv "$temporary_file" "$target"
      echo "  [ok] $file (legacy rules upgraded)"
    else
      printf '%s\n\n' "$ROUTING_RULES" > "$temporary_file"
      cat "$target" >> "$temporary_file"
      mv "$temporary_file" "$target"
      echo "  [ok] $file (rules injected)"
    fi
    INJECTED=$((INJECTED + 1))
  fi
done

if [ "$INJECTED" -eq 0 ]; then
  echo "  [warn] AGENTS.md and CLAUDE.md are absent; routing rules were not injected" >&2
fi

ERRORS=0
for file in candidate-drop.conf DEPLOY.md skill-index.json VERSION skills/deploy-router/SKILL.md skills/governance/alignment-skill-journal/scripts/create_candidate.py; do
  if [ ! -f "$DEPLOY_DST/$file" ]; then
    echo "  [fail] missing $file" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

CANDIDATE_DROP_CONFIG="$DEPLOY_DST/candidate-drop.conf"
if [ -f "$CANDIDATE_DROP_CONFIG" ]; then
  if ! CANDIDATE_DROP_DIR="$(awk '
    /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
    { path = $0; count += 1 }
    END { if (count != 1) exit 1; print path }
  ' "$CANDIDATE_DROP_CONFIG")"; then
    echo "  [fail] candidate-drop.conf must contain exactly one directory path" >&2
    ERRORS=$((ERRORS + 1))
  elif [[ "$CANDIDATE_DROP_DIR" != /* ]]; then
    echo "  [fail] candidate drop directory must be absolute: $CANDIDATE_DROP_DIR" >&2
    ERRORS=$((ERRORS + 1))
  elif [ ! -d "$CANDIDATE_DROP_DIR" ]; then
    echo "  [fail] candidate drop directory does not exist: $CANDIDATE_DROP_DIR" >&2
    ERRORS=$((ERRORS + 1))
  elif [ ! -w "$CANDIDATE_DROP_DIR" ]; then
    echo "  [fail] candidate drop directory is not writable: $CANDIDATE_DROP_DIR" >&2
    ERRORS=$((ERRORS + 1))
  else
    echo "  [ok] candidate drop directory: $CANDIDATE_DROP_DIR"
  fi
fi

if [ "$ERRORS" -gt 0 ]; then
  echo "==> Installation completed with $ERRORS error(s)" >&2
  exit 1
fi

echo "==> Done. .deploy/ initialized at $DEPLOY_DST"
