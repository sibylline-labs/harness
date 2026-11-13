#!/usr/bin/env bash
# SessionStart hook: state the org's current doctrine posture at the top of a new
# session's context.
#
# Reads the doctrine `eris doctrine pull` materializes for the org:
#
#   ~/.eris/doctrine/<orgId>/doctrine.md
#     active: <slug>
#
#     ## <slug>
#     <Name line>
#     - <body bullet>
#
# The org is ERIS_ORG when set, else the only org directory present. With no
# doctrine, or several orgs and no ERIS_ORG, it says so and states no posture:
# a guessed posture is worse than an unresolved one. When `eris` is on PATH and
# the posture carries a policy, the effective gate map (`eris doctrine gates`)
# follows. Every path exits 0 so a session never fails to start on this hook.
set +e
cat >/dev/null 2>&1   # drain the hook payload so the pipe never blocks

root="${HOME}/.eris/doctrine"
CAP=4000

org="${ERIS_ORG:-}"
if [ -z "$org" ] && [ -d "$root" ]; then
    orgs=$(find "$root" -mindepth 1 -maxdepth 1 ! -name '.*' 2>/dev/null)
    if [ "$(printf '%s\n' "$orgs" | grep -c .)" = "1" ]; then
        org=$(basename "$orgs")
    fi
fi

echo "━━━ DOCTRINE ━━━"
file="${root}/${org}/doctrine.md"
if [ -z "$org" ] || [ ! -f "$file" ]; then
    if [ -z "$org" ] && [ -d "$root" ]; then
        echo "Posture unresolved: several orgs under ${root}; set ERIS_ORG to choose one."
    else
        echo "Posture unresolved: no doctrine pulled yet. Run 'eris doctrine pull'."
    fi
    exit 0
fi

slug=$(sed -n 's/^active:[[:space:]]*//p' "$file" | head -n 1 | tr -d '[:space:]')
if [ -z "$slug" ]; then
    echo "Posture unresolved: ${file} names no 'active:' posture."
    exit 0
fi

section=$(awk -v slug="$slug" '
    /^## / { if (found) exit; h = $0; sub(/^## /, "", h); gsub(/[[:space:]]+$/, "", h); if (h == slug) { found = 1; next } }
    found && /^```/ { exit }
    found { print }
' "$file" | head -c "$CAP")

if [ -z "$section" ]; then
    echo "Posture '${slug}' has no '## ${slug}' section in ${file}; treat it as unresolved."
    exit 0
fi
printf 'Treat this as the org'"'"'s current posture for this session.\n\n%s\n' "$section"

if command -v eris >/dev/null 2>&1; then
    gates=$(eris doctrine gates 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$gates" ]; then
        printf '\n### effective gates\n%s\n' "$gates"
    fi
fi
exit 0
