#!/usr/bin/env bash
# Remove OpenClaw SEO skills installed from this repo
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/skills}"
FORCE=false
DRY_RUN=false
REMOVED=0
SKIPPED=0

usage() {
  echo "Usage: $0 [--force] [--dry-run] [--target DIR]"
  echo ""
  echo "Options:"
  echo "  --force     Also remove copied (non-symlink) installs"
  echo "  --dry-run   Show what would be done without doing it"
  echo "  --target    Override target directory (default: ~/.openclaw/skills)"
  echo "  --help      Show this help"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)   FORCE=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --target)  TARGET_DIR="$2"; shift 2 ;;
    --help)    usage ;;
    *)         echo "Unknown option: $1"; usage ;;
  esac
done

echo "OpenClaw SEO Skills Uninstaller"
echo "================================"
echo "Source:  $REPO_ROOT"
echo "Target:  $TARGET_DIR"
[ "$DRY_RUN" = true ] && echo "** DRY RUN — no changes will be made **"
echo ""

if [ ! -d "$TARGET_DIR" ]; then
  echo "Target directory does not exist. Nothing to remove."
  exit 0
fi

for skill_dir in "$REPO_ROOT"/seo-*; do
  [ -d "$skill_dir" ] || continue

  skill_name="$(basename "$skill_dir")"
  dest="$TARGET_DIR/$skill_name"

  [ -e "$dest" ] || [ -L "$dest" ] || continue

  # Symlink pointing to this repo — safe to remove
  if [ -L "$dest" ]; then
    link_target="$(readlink -f "$dest" 2>/dev/null || readlink "$dest")"
    if [ "$link_target" = "$(readlink -f "$skill_dir")" ]; then
      if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] rm $dest"
      else
        rm "$dest"
        echo "REMOVE  $skill_name (symlink)"
      fi
      REMOVED=$((REMOVED + 1))
      continue
    fi
    echo "SKIP    $skill_name (symlink points elsewhere)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Directory (copied install) — only remove with --force
  if [ -d "$dest" ]; then
    if [ "$FORCE" = true ]; then
      if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] rm -rf $dest"
      else
        rm -rf "$dest"
        echo "REMOVE  $skill_name (copied, --force)"
      fi
      REMOVED=$((REMOVED + 1))
    else
      echo "SKIP    $skill_name (copied install, use --force to remove)"
      SKIPPED=$((SKIPPED + 1))
    fi
    continue
  fi
done

echo ""
echo "Done: $REMOVED removed, $SKIPPED skipped"
