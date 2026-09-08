#!/usr/bin/env bash
# Fails when a plugin's files changed without its version changing.
#
# Usage: ./scripts/check-version-bumps.sh [base-ref]   (default: origin/main)
set -euo pipefail

base="${1:-origin/main}"

version_of() { sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1; }

changed_plugins=$(git diff --name-only "$base"...HEAD -- plugins/ \
  | awk -F/ 'NF > 1 { print $2 }' | sort -u)

if [ -z "$changed_plugins" ]; then
  echo "No plugin files changed."
  exit 0
fi

failed=0
for plugin in $changed_plugins; do
  manifest="plugins/$plugin/.claude-plugin/plugin.json"

  # Plugin deleted in this branch — nothing to bump.
  [ -f "$manifest" ] || continue

  new=$(version_of < "$manifest")
  old=$(git show "$base:$manifest" 2>/dev/null | version_of || true)

  if [ -z "$old" ]; then
    echo "ok    $plugin — new plugin at $new"
  elif [ "$old" != "$new" ]; then
    echo "ok    $plugin — $old -> $new"
  else
    echo "FAIL  $plugin — files changed but version is still $old"
    failed=1
  fi
done

if [ "$failed" -ne 0 ]; then
  cat <<'MSG'

Bump the version in the plugin's .claude-plugin/plugin.json. Without it,
`claude plugin update` cannot see the change and it ships to nobody.

  minor (0.7.0 -> 0.8.0)  a new skill/agent/command, or a change to what one does
  patch (0.7.0 -> 0.7.1)  a correction that restores intended behaviour
MSG
  exit 1
fi
