#!/usr/bin/env bash
# uninstall.sh - mirror of /founder-os:uninstall
#
# Usage:
#   bash uninstall.sh [--target <path>] [--dry-run] [--help]
#
# With no --target it uninstalls the folder it sits in, when that folder is a
# Founder OS install (it holds VERSION or core/). Otherwise ~/founder-os.
#
# Removes the FounderOS system layer by NAMING what it removes, never by
# wiping and restoring. Anything this script does not name survives by
# construction: your operating data (core/, cadence/, context/, brain/,
# capture/, brands/, companies/, network/, clients/, roles/, system/, rules/,
# memory/, CLAUDE.md, MEMORY.md, stack.json, os-config.yaml) and any company
# or project folder setup created at the root. The earlier version of this
# script kept a preserve-list and deleted everything else, which destroyed
# any user path the list had fallen behind on. A remove-list cannot make
# that mistake: an unknown path is left alone, not deleted.
#
# The same rule holds inside the five folders a founder adds to: skills/,
# .claude/commands/, scripts/, .claude/hooks/ and .githooks/. Only what
# shipped with Founder OS is removed (the SHIPPED_* lists below). A skill,
# command, script or hook you wrote is not on those lists, so it stays, and
# the script names it before you confirm and again at the end.
# scripts/private-name-patterns.txt (your list of names to keep out of your
# files, never in version history) is not on them either, so it stays too.
#
# The remove-list must mirror the System Layer list in
# .claude/commands/update.md, in both directions. A path added there joins
# this list in the same commit. tests/test_review_fixes_git.py checks both.
# The shipped lists must equal what the release ships; tests check them
# against git ls-files (and the file lists against every file the history
# ever shipped in those folders, so a file retired from an older release
# goes too instead of being kept as if it were yours).
#
# Targets bash 3.2+ so the macOS system bash works without brew install bash.
# Avoid ${var,,} / declare -A / mapfile / readarray (bash 4+ only).

set -euo pipefail

# ---- constants ---------------------------------------------------------------

DEFAULT_TARGET="$HOME/founder-os"
# Pre-v1.37 installs landed here. Detected below so uninstall still finds an
# older install when the default moved to ~/founder-os.
LEGACY_TARGET="$HOME/.claude/plugins/founder-os"

# install.sh stopped copying hooks to ~/.claude/hooks/ in v1.24.1; hooks now live
# inside the install directory at $TARGET/.claude/hooks/, and the shipped
# ones are removed below with the rest. Do NOT re-introduce a global hook
# removal step here: a sibling PersonalOS install shares ~/.claude/hooks/.

# System Layer directories removed whole. rules/ is deliberately absent:
# update.md classifies it as founder-personalized, so uninstall leaves it.
# state/ is on update.md's System Layer list but stays here: it holds the
# pre-edit copies of your files, so only --purge in the command removes it.
SYSTEM_DIRS=(
  "templates"
  "notion-package"
  "docs"
  "updates"
  "assets"
  ".claude-plugin"
)

# System Layer directories a founder also adds to. Only the shipped entries go.
# skills/ and .claude/commands/ are matched by top-level name. scripts/,
# .claude/hooks/ and .githooks/ are matched file by file (scripts/ has a
# hooks/ folder of its own), and the __pycache__ folders Python writes inside
# them go too: they are caches the shipped scripts made, never founder work.
PARTIAL_DIRS=(
  "skills"
  ".claude/commands"
  "scripts"
  ".claude/hooks"
  ".githooks"
)

# Every skill folder the release ships under skills/.
SHIPPED_SKILLS=(
  add-hands add-mouth add-voice approval-gates audit backup blind-spot-review
  bottleneck-diagnostic brain-log brain-pass brain-snapshot brand-interview
  brand-voice-interview business-context-loader campaign-from-theme
  capture-sweep catch-up client-update connect content-repurposer
  content-start context-persistence cross-link data-security
  decision-framework decisions-start delivery-start email-drafter
  employee-review finance-import forcing-questions founder-coaching
  founder-next-move founder-os-setup founder-review founder-scope-challenge
  github-ops handoff-protocol hire history housekeeping ingest
  knowledge-capture legal-compliance linkedin-brand-direction
  linkedin-network-scan linkedin-pack-references linkedin-post
  linkedin-power-audit linkedin-start linkedin-warm-revival lint list-pruner
  log-archive log-reply meeting-prep memory-pass menu morning-loop
  observation-rollup os-evolve own-your-history pipeline-start pitch-deck
  pre-send-check priority-triage profile-router proposal-writer prospect-init
  query queue readiness-check reconnect-prompt restore review-responder
  routines save self-diligence session-handoff ship-deliverable
  since-last-session skill-creator sop-writer strategic-analysis
  strategic-read today tune unit-economics verify voice-interview
  web-fetch-extract weekly-review what-to-change where wiki-build
  writing-score your-deliverable-template your-voice
)
# Files the release ships at the top of skills/.
SHIPPED_SKILL_FILES=(
  index.md discoverable.yaml content-pack.md decisions-pack.md delivery-pack.md
  linkedin-pack.md money-pack.md pipeline-pack.md
)
# Every command file the release ships under .claude/commands/.
SHIPPED_COMMANDS=(
  audit.md brain-pass.md brand-interview.md brand-voice-interview.md
  campaign-from-theme.md capture-meeting.md capture-sweep.md catch-up.md
  changes.md devil.md dream.md employee-review.md forcing-questions.md
  founder-review.md housekeeping.md ingest.md legal-add-source.md
  legal-setup.md legal-update.md linkedin-scan.md lint.md log-reply.md
  menu.md morning-loop.md next.md observation-rollup.md os-evolve.md
  pitch-deck.md pre-meeting.md query.md queue.md rant.md review-responder.md
  self-diligence.md setup.md ship-deliverable.md since-last-session.md
  status.md strategic-read.md today.md uninstall.md update.md verify.md
  voice-interview.md where.md wiki-build.md writing-score.md
)
# Every file the releases shipped under scripts/, by path inside scripts/.
# render-playbook.py and render-skills.py were retired in an earlier release;
# an install updated since may still hold them.
SHIPPED_SCRIPTS=(
  _common.py agent_runs.py agents_sync.py brain-pass-log.py brain-snapshot.py
  build_release.py caveman_git.py check-brand-voice-ready.py
  check-identity-ready.py check-log-has-history.py check-private-names.py
  check-voice-ready.py check_download_links.py claims_check.py connect.py
  deliverable_gate.py employee_verdict.py entity_check.py flat_yaml.py
  hooks/dispatch.py install-git-hooks.sh list-brands.py log-archive.py
  memory-diff.py menu.py observation-rollup.py open_folder.py pitch_deck.py
  private-name-patterns.txt.template query.py register_census.py
  render-playbook.py render-skills.py scrape.py selfdoc_check.py
  session_changes.py set_folder_icon.sh skill_health.py skills_sync.py
  unconfirmed_facts.py unit_math.py user-prompt-capture.py verify.py
  what-to-change.py where.py wiki-build.py writing_scorecard.py
)
# Every file the releases shipped under .claude/hooks/. Only
# session_start_brief.py ships now; the .sh and .ps1 pairs were retired when
# the hooks moved to one Python dispatcher, and an install updated since may
# still hold them.
SHIPPED_CLAUDE_HOOKS=(
  session_start_brief.py
  post-tool-use-observation.ps1 post-tool-use-observation.sh
  pre-compact-flush.ps1 pre-compact-flush.sh
  pre-tool-use-snapshot.ps1 pre-tool-use-snapshot.sh
  session-close-autosave.ps1 session-close-autosave.sh
  session-close-changes.ps1 session-close-changes.sh
  session-close-revenue-check.ps1 session-close-revenue-check.sh
  session-start-brief.ps1 session-start-brief.sh
  session-start-liveness.ps1 session-start-liveness.sh
  user-prompt-capture.ps1 user-prompt-capture.sh
)
# The git hooks the release ships under .githooks/.
SHIPPED_GITHOOKS=(
  pre-commit commit-msg pre-push
)

# Generated copies inside .claude/ are machinery too: skills_sync.py copies
# promoted skills into .claude/skills/, and agents_sync.py writes one agent
# file per seat into .claude/agents/. Both point at scripts this uninstall
# deletes, so leaving them behind leaves skills and agents that break the next
# time Claude Code opens the folder. They are found below, not listed here,
# because only what the OS generated may go: a .claude/skills/ folder whose
# name is a shipped skill, and a .claude/agents/ file carrying agents_sync.py's
# marker line. A skill or an agent you put there yourself does not match
# either test and stays.
AGENT_MARKER="generated by scripts/agents_sync.py"

# System Layer files at the root. AVATAR.md is a retired product file (moved
# to templates/avatar.md); an older install may still have it at the root.
SYSTEM_FILES=(
  ".claude/settings.json"
  "VERSION"
  "AGENTS.md"
  "GEMINI.md"
  "AVATAR.md"
  "README.md"
  "CHANGELOG.md"
  "LICENSE"
  "SECURITY.md"
  "CONTRIBUTING.md"
  "llms.txt"
  ".gitattributes"
  "Start Founder OS.bat"
  "Start Founder OS.command"
  "install.sh"
  "uninstall.sh"
)

# ---- argument parsing --------------------------------------------------------

TARGET=""
DRY_RUN=false

show_help() {
  cat <<'EOF'
FounderOS uninstaller

Usage:
  bash uninstall.sh [options]

Options:
  --target <path>  Uninstall from this folder. Without it: the folder this
                   script sits in, when that is a Founder OS install, else
                   ~/founder-os
  --dry-run        List what would be removed without removing anything
  --help           Show this help

Removes only the named system layer (the skills, commands, scripts and hooks
that shipped, templates, docs, updates, plugin manifests, the start files,
root reference files, and the skill and agent copies the OS generated in
.claude/). A skill that shipped goes whole, with anything you added inside
it, such as a legal jurisdiction pack in skills/legal-compliance/references/.
Everything else in the folder is yours and is not touched: core/,
cadence/, context/, brain/, capture/, brands/, companies/, network/,
clients/, roles/, system/, rules/, memory/, CLAUDE.md, MEMORY.md,
stack.json, os-config.yaml, any company or project folders setup created,
skills, commands, scripts and hooks you wrote, and
scripts/private-name-patterns.txt.
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      shift
      TARGET="${1:-}"
      if [[ -z "$TARGET" ]]; then
        echo "ERROR: --target requires a path argument." >&2
        exit 1
      fi
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --help|-h)
      show_help
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run 'bash uninstall.sh --help' for usage." >&2
      exit 1
      ;;
  esac
  shift
done

if [[ -z "$TARGET" ]]; then
  # The folder this script sits in, when it is an install: a ZIP install can
  # live anywhere, and uninstalling ~/founder-os instead of the folder the
  # founder ran this from removes the wrong install or nothing at all. Under
  # `curl ... | bash` there is no script file, so this test is skipped.
  SELF="${BASH_SOURCE[0]:-}"
  SELF_DIR=""
  if [[ -n "$SELF" && -f "$SELF" ]]; then
    SELF_DIR="$(cd "$(dirname "$SELF")" && pwd)"
  fi
  if [[ -n "$SELF_DIR" ]] && { [[ -f "$SELF_DIR/VERSION" ]] || [[ -d "$SELF_DIR/core" ]]; }; then
    TARGET="$SELF_DIR"
  elif [[ -d "$LEGACY_TARGET" && ! -d "$DEFAULT_TARGET" ]]; then
    # Prefer the current default ~/founder-os. Fall back to the legacy
    # ~/.claude/plugins/founder-os only if that is where the install actually is.
    TARGET="$LEGACY_TARGET"
  else
    TARGET="$DEFAULT_TARGET"
  fi
fi

# ---- helpers -----------------------------------------------------------------

info()  { printf '  %s\n' "$*"; }
ok()    { printf '  [removed] %s\n' "$*"; }
skip()  { printf '  [skip] %s\n' "$*"; }
dryrun(){ printf '  [dry-run] would remove: %s\n' "$*"; }

in_list() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    [[ "$item" == "$needle" ]] && return 0
  done
  return 1
}

# Whether a file shipped, by its path inside one of the file-by-file folders.
is_shipped_file() {
  case "$1" in
    scripts) in_list "$2" "${SHIPPED_SCRIPTS[@]}" ;;
    .claude/hooks) in_list "$2" "${SHIPPED_CLAUDE_HOOKS[@]}" ;;
    .githooks) in_list "$2" "${SHIPPED_GITHOOKS[@]}" ;;
    *) return 1 ;;
  esac
}

# Every file in one of the file-by-file folders, by its path inside it, one
# per line, leaving out what is inside Python's __pycache__ folders.
files_in() {
  ( cd "$TARGET/$1" && find . -type f ! -path '*/__pycache__/*' -print ) | sed 's#^\./##'
}

# The entries of one PARTIAL_DIRS folder that are NOT the product's, one per
# line. These stay.
kept_entries() {
  local dir="$1" entry name rel
  [[ -d "$TARGET/$dir" ]] || return 0
  case "$dir" in
    scripts|.claude/hooks|.githooks)
      while IFS= read -r rel; do
        [[ -n "$rel" ]] || continue
        if ! is_shipped_file "$dir" "$rel"; then
          printf '%s\n' "$dir/$rel"
        fi
      done < <(files_in "$dir")
      return 0
      ;;
  esac
  for entry in "$TARGET/$dir"/* "$TARGET/$dir"/.[!.]*; do
    [[ -e "$entry" ]] || continue
    name="$(basename "$entry")"
    case "$dir" in
      skills)
        in_list "$name" "${SHIPPED_SKILLS[@]}" && continue
        in_list "$name" "${SHIPPED_SKILL_FILES[@]}" && continue
        ;;
      .claude/commands)
        in_list "$name" "${SHIPPED_COMMANDS[@]}" && continue
        ;;
    esac
    printf '%s\n' "$dir/$name"
  done
  return 0
}

# The entries of one PARTIAL_DIRS folder that ARE the product's. These go.
removable_entries() {
  local dir="$1" entry name rel
  [[ -d "$TARGET/$dir" ]] || return 0
  case "$dir" in
    scripts|.claude/hooks|.githooks)
      while IFS= read -r rel; do
        [[ -n "$rel" ]] || continue
        if is_shipped_file "$dir" "$rel"; then
          printf '%s\n' "$dir/$rel"
        fi
      done < <(files_in "$dir")
      # Python's caches of the shipped scripts: rebuilt on the next run.
      ( cd "$TARGET/$dir" && find . -type d -name __pycache__ -prune -print ) | sed "s#^\./#$dir/#"
      return 0
      ;;
  esac
  for entry in "$TARGET/$dir"/* "$TARGET/$dir"/.[!.]*; do
    [[ -e "$entry" ]] || continue
    name="$(basename "$entry")"
    case "$dir" in
      skills)
        in_list "$name" "${SHIPPED_SKILLS[@]}" || in_list "$name" "${SHIPPED_SKILL_FILES[@]}" || continue
        ;;
      .claude/commands)
        in_list "$name" "${SHIPPED_COMMANDS[@]}" || continue
        ;;
    esac
    printf '%s\n' "$dir/$name"
  done
  return 0
}

# ---- inventory ---------------------------------------------------------------

echo ""
echo "FounderOS uninstaller"
echo "Target: $TARGET"
echo ""

if [[ ! -d "$TARGET" ]]; then
  info "Nothing to remove - $TARGET does not exist."
  exit 0
fi

# Find the generated copies BEFORE skills/ is touched.
GENERATED=()
if [[ -d "$TARGET/.claude/skills" ]]; then
  for d in "$TARGET/.claude/skills"/*/; do
    [[ -d "$d" ]] || continue
    name="$(basename "$d")"
    if in_list "$name" "${SHIPPED_SKILLS[@]}"; then
      GENERATED+=(".claude/skills/$name")
    fi
  done
fi
if [[ -d "$TARGET/.claude/agents" ]]; then
  for f in "$TARGET/.claude/agents"/*.md; do
    [[ -f "$f" ]] || continue
    if grep -qF "$AGENT_MARKER" "$f" 2>/dev/null; then
      GENERATED+=(".claude/agents/$(basename "$f")")
    fi
  done
fi

PARTIAL_REMOVE=()
KEPT=()
for dir in "${PARTIAL_DIRS[@]}"; do
  while IFS= read -r line; do
    [[ -n "$line" ]] && PARTIAL_REMOVE+=("$line")
  done < <(removable_entries "$dir")
  while IFS= read -r line; do
    [[ -n "$line" ]] && KEPT+=("$line")
  done < <(kept_entries "$dir")
done

# Version history set to run the save checks from .githooks. Those checks call
# scripts this removes, so the setting is turned off with them. Not when a
# hook of the founder's own stays in .githooks: the setting is what runs it.
HOOKS_PATH_SET=false
if [[ -e "$TARGET/.git" ]] && command -v git >/dev/null 2>&1; then
  if [[ "$(git -C "$TARGET" config --local --get core.hooksPath 2>/dev/null || true)" == ".githooks" ]]; then
    HOOKS_PATH_SET=true
  fi
fi
GITHOOKS_KEPT=false
for k in ${KEPT[@]+"${KEPT[@]}"}; do
  case "$k" in .githooks/*) GITHOOKS_KEPT=true ;; esac
done

echo "The following system-layer paths will be removed:"
for dir in "${SYSTEM_DIRS[@]}"; do
  if [[ -d "$TARGET/$dir" ]]; then
    echo "    $TARGET/$dir/"
  fi
done
for dir in "${PARTIAL_DIRS[@]}"; do
  if [[ -d "$TARGET/$dir" ]]; then
    echo "    $TARGET/$dir/   (what shipped with Founder OS)"
  fi
done
for file in "${SYSTEM_FILES[@]}"; do
  if [[ -f "$TARGET/$file" ]]; then
    echo "    $TARGET/$file"
  fi
done
# ${arr[@]+"${arr[@]}"}: an empty array under set -u is an error in bash 3.2,
# the bash every Mac ships.
for gen in ${GENERATED[@]+"${GENERATED[@]}"}; do
  echo "    $TARGET/$gen   (generated by the OS)"
done
if [[ "$HOOKS_PATH_SET" == true && "$GITHOOKS_KEPT" == false ]]; then
  echo "    git setting core.hooksPath (it points at .githooks, which goes)"
fi
echo ""
if [[ ${#KEPT[@]} -gt 0 ]]; then
  echo "Kept, because they are yours and did not ship with Founder OS:"
  for k in "${KEPT[@]}"; do
    echo "    $TARGET/$k"
  done
  echo ""
fi
if [[ "$HOOKS_PATH_SET" == true && "$GITHOOKS_KEPT" == true ]]; then
  echo "The git setting core.hooksPath stays on, so your own hooks in .githooks/ keep running."
  echo ""
fi
# A shipped skill goes whole, and /legal-setup, /legal-add-source and
# /legal-update write the founder's jurisdiction pack, sources and edits
# inside one. Say so before the yes.
if [[ -d "$TARGET/skills/legal-compliance/references" ]]; then
  echo "A skill that shipped goes with anything you added inside it. A legal jurisdiction"
  echo "pack, sources or edits you made with /legal-setup, /legal-add-source or /legal-update"
  echo "live in $TARGET/skills/legal-compliance/references/, so copy that folder out first to keep them."
  echo ""
fi
echo "Everything else in $TARGET is your data and will NOT be touched."
echo ""

# ---- confirm -----------------------------------------------------------------

if [[ "$DRY_RUN" == true ]]; then
  echo "Dry run - no changes made."
  exit 0
fi

printf 'Proceed with removal? [y/N] '
read -r answer
answer=$(printf '%s' "$answer" | tr '[:upper:]' '[:lower:]')
if [[ "$answer" != "y" && "$answer" != "yes" ]]; then
  info "Cancelled. Nothing was removed."
  exit 0
fi

echo ""

# ---- remove named system paths ----------------------------------------------

for gen in ${GENERATED[@]+"${GENERATED[@]}"}; do
  path="$TARGET/$gen"
  if [[ -e "$path" ]]; then
    rm -rf "$path"
    ok "$path"
  fi
done

for rel in ${PARTIAL_REMOVE[@]+"${PARTIAL_REMOVE[@]}"}; do
  path="$TARGET/$rel"
  if [[ -e "$path" ]]; then
    rm -rf "$path"
  fi
done
# A shipped subfolder (scripts/hooks/) goes once nothing of yours is in it.
for rel in "${SHIPPED_SCRIPTS[@]}"; do
  case "$rel" in
    */*) [[ -d "$TARGET/scripts/${rel%/*}" ]] && rmdir "$TARGET/scripts/${rel%/*}" 2>/dev/null || true ;;
  esac
done
for dir in "${PARTIAL_DIRS[@]}"; do
  if [[ -d "$TARGET/$dir" ]]; then
    if [[ -z "$(ls -A "$TARGET/$dir" 2>/dev/null)" ]]; then
      rmdir "$TARGET/$dir"
      ok "$TARGET/$dir"
    else
      ok "$TARGET/$dir (what shipped; yours stays)"
    fi
  fi
done

for dir in "${SYSTEM_DIRS[@]}"; do
  path="$TARGET/$dir"
  if [[ -d "$path" ]]; then
    rm -rf "$path"
    ok "$path"
  fi
done

for file in "${SYSTEM_FILES[@]}"; do
  path="$TARGET/$file"
  if [[ -f "$path" ]]; then
    rm -f "$path"
    ok "$path"
  fi
done

if [[ "$HOOKS_PATH_SET" == true && "$GITHOOKS_KEPT" == true ]]; then
  info "Left the git setting core.hooksPath on: your own hooks in .githooks/ still run."
elif [[ "$HOOKS_PATH_SET" == true ]]; then
  git -C "$TARGET" config --local --unset core.hooksPath
  info "Turned off the git setting core.hooksPath: the save checks it ran are gone, and left on it would stop every commit."
fi

# .claude/skills, .claude/agents and .claude/ itself stay if anything of the
# user's is left in them; each is removed only when empty.
for sub in ".claude/skills" ".claude/agents" ".claude"; do
  if [[ -d "$TARGET/$sub" ]] && [[ -z "$(ls -A "$TARGET/$sub" 2>/dev/null)" ]]; then
    rmdir "$TARGET/$sub"
    ok "$TARGET/$sub (empty)"
  fi
done

# ---- done --------------------------------------------------------------------

echo ""
echo "FounderOS system layer removed."
echo "Your data is still in: $TARGET"
if [[ ${#KEPT[@]} -gt 0 ]]; then
  echo "Also kept, because you made them:"
  for k in "${KEPT[@]}"; do
    echo "  $k"
  done
fi
echo "To remove your data too, delete that folder yourself - this script never does."
echo ""
echo "Two things outside this folder were not touched. Remove them by hand if you"
echo "want them gone:"
echo "  1. ~/.claude/CLAUDE.md - setup added a short Founder OS block there (who you"
echo "     are, how you like answers). Open the file and delete everything from the"
echo "     line"
echo "       <!-- FOUNDER OS START - written by Founder OS setup. Edit or delete this block freely. -->"
echo "     down to and including the line"
echo "       <!-- FOUNDER OS END -->"
echo "     The rest of the file is yours; leave it as it is."
echo "  2. The memory Claude Code keeps for this folder: the folder under"
echo "     ~/.claude/projects/ whose name ends in -$(basename "$TARGET" | sed 's/[^A-Za-z0-9]/-/g'),"
echo "     with a memory/ folder inside. Delete that memory/ folder."
echo ""
echo "Plugin path: if you installed via the Claude Code plugin marketplace, also run"
echo "  /plugin uninstall founder-os"
echo "to de-register the plugin."
