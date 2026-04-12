#!/usr/bin/env bash
# Link all open issues from the repo to the GitHub Project "skiMate" (Projects v2).
#
# Prerequisites:
#   gh auth refresh -h github.com -s read:project -s project
#   (complete the browser/device flow when prompted)
#
# Find your project number: gh project list --owner YOUR_LOGIN
#
# Usage:
#   ./scripts/gh_link_issues_to_project.sh
# Optional overrides: GITHUB_PROJECT_NUMBER, GITHUB_PROJECT_OWNER, GITHUB_REPO
#
# Default project is user 15273 / project 5 (skiMate):
#   https://github.com/users/15273/projects/5

set -euo pipefail

OWNER="${GITHUB_PROJECT_OWNER:-15273}"
REPO="${GITHUB_REPO:-15273/SkiPlannerAI}"
PROJECT_NUMBER="${GITHUB_PROJECT_NUMBER:-5}"

if ! gh auth status -h github.com &>/dev/null; then
  echo "Error: gh is not authenticated. Run: gh auth login"
  exit 1
fi

echo "Linking open issues from $REPO to project #$PROJECT_NUMBER (owner: $OWNER)..."
count=0
skipped=0

while IFS= read -r num; do
  [[ -z "$num" ]] && continue
  url="https://github.com/${REPO}/issues/${num}"
  if out=$(gh project item-add "${PROJECT_NUMBER}" --owner "${OWNER}" --url "${url}" 2>&1); then
    echo "  added #$num"
    count=$((count + 1))
  else
    # Duplicate items often return an error; missing scopes show in $out
    echo "  skip #$num — ${out:-unknown error}"
    skipped=$((skipped + 1))
  fi
done < <(gh issue list --repo "${REPO}" --state open --limit 500 --json number --jq '.[].number' | sort -n)

echo "Done. Added: $count, skipped/failed: $skipped"
if (( count == 0 && skipped > 0 )); then
  echo ""
  echo "Nothing new was linked. If you see scope errors, run:"
  echo "  gh auth refresh -h github.com -s read:project -s project"
  echo "If issues were already on the project, skips are expected."
fi
