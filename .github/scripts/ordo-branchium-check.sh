#!/usr/bin/env bash
# Ordo Branchium — branch-name inquisitor for pull requests.
set -euo pipefail

BRANCH="${1:?branch name required}"

ORDINES='cantica|fabrica|litania|purgatio|codex|cogitator|auspex|exterminatus|crusade'
PATTERN="^(${ORDINES})/[a-z0-9][a-z0-9-]{2,47}$"

FORBIDDEN='^(main|master|develop|release|staging)$'

pick_message() {
  local branch="$1" reason="$2"
  local -a wrath
  wrath=(
    "⚙ **THE MACHINE SPIRIT GROWS WRATHFUL.** Branch \`${branch}\` bears no sacred *ordo*. The Cogitator records a **naming heresy** (${reason}). Rename to \`<ordo>/<slug>\` per [Ordo Branchium](https://github.com/${GITHUB_REPOSITORY}/blob/main/CONTRIBUTING.md#2-create-a-branch--ordo-branchium)."
    "⚙ **HERESY DETECTA — PROFANATIO BRANCHIUM.** \`${branch}\` profanes the branch registry. ${reason} Consult the [sacred ordines](https://github.com/${GITHUB_REPOSITORY}/blob/main/.github/BRANCH_POLICY.md)."
    "⚙ **ACCUSATION OF HERESY (nomen vanum).** The branch \`${branch}\` has no Mechanicus ordo. ${reason} The Machine demands: \`cantica/\`, \`purgatio/\`, \`codex/\`, \`fabrica/\`, \`litania/\`, \`cogitator/\`, \`auspex/\`, \`exterminatus/\`, or \`crusade/\`."
    "⚙ **IRA MACHINAE — BRANCH ANATHEMA.** \`${branch}\` shall not pass. ${reason} *From the weakness of naming discipline, heresy enters the forge.*"
    "⚙ **EXCOMMUNICATIO NOMINIS.** Branch \`${branch}\` is cast out until rebaptized. ${reason} Example: \`purgatio/divisor-nihil-guard\`."
  )
  local idx=$(( RANDOM % ${#wrath[@]} ))
  printf '%s' "${wrath[$idx]}"
}

if [[ "$BRANCH" =~ ^dependabot/ ]]; then
  echo "verdict=machine-spirit" >> "${GITHUB_OUTPUT:-/dev/null}"
  echo "⚙ Branch \`${BRANCH}\` — the **Machine Spirit** (Dependabot) tends the sacred pins. *Ordo Branchium* waived by cult dispensation for \`dependabot/*\`."
  exit 0
fi

if [[ "$BRANCH" =~ $FORBIDDEN ]]; then
  MSG=$(pick_message "$BRANCH" "Sacred trunk names (\`main\`, \`master\`, …) are reserved.")
  echo "verdict=heresy" >> "${GITHUB_OUTPUT:-/dev/null}"
  echo "message<<EOF" >> "${GITHUB_OUTPUT:-/dev/null}"
  echo "$MSG" >> "${GITHUB_OUTPUT:-/dev/null}"
  echo "EOF" >> "${GITHUB_OUTPUT:-/dev/null}"
  echo "$MSG"
  exit 1
fi

if [[ "$BRANCH" =~ $PATTERN ]]; then
  echo "verdict=placed" >> "${GITHUB_OUTPUT:-/dev/null}"
  if [[ "$BRANCH" =~ ^auspex/ ]]; then
    echo "auspex=true" >> "${GITHUB_OUTPUT:-/dev/null}"
    echo "⚙ Branch \`${BRANCH}\` — *auspex* reconnaissance. Mark this PR as **Draft** unless promoting to a full ordo."
  else
    echo "⚙ Branch \`${BRANCH}\` — the Machine Spirit is **placatus**. Ordo Branchium satisfied."
  fi
  exit 0
fi

REASON='Expected `<ordo>/<slug>` — lowercase kebab-case slug, 3–48 characters, no nested paths.'
if [[ "$BRANCH" == */*/* ]]; then
  REASON='Nested paths are forbidden (\`cantica/fabrica/foo\`). One ordo only.'
elif [[ "$BRANCH" =~ [A-Z] ]]; then
  REASON='Uppercase detected. The Cult writes branches in lowercase only.'
elif [[ ! "$BRANCH" == */* ]]; then
  REASON='No ordo prefix. Every branch must begin with a sacred ordo and \`/\`.'
fi

MSG=$(pick_message "$BRANCH" "$REASON")
echo "verdict=heresy" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "message<<EOF" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "$MSG" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "EOF" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "$MSG"
exit 1
