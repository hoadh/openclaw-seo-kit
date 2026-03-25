#!/usr/bin/env bash
# Install OpenClaw SEO skills from this repo to OpenClaw environment
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/skills}"
MODE="symlink"
DRY_RUN=false
INSTALLED=0
SKIPPED=0
ERRORS=0

usage() {
  echo "Usage: $0 [--copy] [--dry-run] [--target DIR]"
  echo ""
  echo "Options:"
  echo "  --copy      Copy files instead of symlink (portable install)"
  echo "  --dry-run   Show what would be done without doing it"
  echo "  --target    Override target directory (default: ~/.openclaw/skills)"
  echo "  --help      Show this help"
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy)    MODE="copy"; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --target)  TARGET_DIR="$2"; shift 2 ;;
    --help)    usage ;;
    *)         echo "Unknown option: $1"; usage ;;
  esac
done

echo "OpenClaw SEO Skills Installer"
echo "=============================="
echo "Source:  $REPO_ROOT"
echo "Target:  $TARGET_DIR"
echo "Mode:    $MODE"
[ "$DRY_RUN" = true ] && echo "** DRY RUN — no changes will be made **"
echo ""

# Create target directory if needed
if [ ! -d "$TARGET_DIR" ]; then
  if [ "$DRY_RUN" = true ]; then
    echo "[dry-run] mkdir -p $TARGET_DIR"
  else
    mkdir -p "$TARGET_DIR"
    echo "Created: $TARGET_DIR"
  fi
fi

# Find all seo-* directories with SKILL.md or scripts/ (shared-utils has no SKILL.md)
for skill_dir in "$REPO_ROOT"/seo-*; do
  [ -d "$skill_dir" ] || continue

  skill_name="$(basename "$skill_dir")"
  dest="$TARGET_DIR/$skill_name"

  # Verify it's a valid skill (has SKILL.md) or shared utility (has scripts/)
  if [ ! -f "$skill_dir/SKILL.md" ] && [ ! -d "$skill_dir/scripts" ]; then
    echo "SKIP  $skill_name (no SKILL.md or scripts/)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Check if already installed
  if [ -e "$dest" ]; then
    if [ -L "$dest" ]; then
      existing_target="$(readlink -f "$dest" 2>/dev/null || readlink "$dest")"
      if [ "$existing_target" = "$(readlink -f "$skill_dir")" ]; then
        echo "SKIP  $skill_name (already linked)"
        SKIPPED=$((SKIPPED + 1))
        continue
      fi
    fi
    echo "SKIP  $skill_name (already exists at $dest)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Install
  if [ "$DRY_RUN" = true ]; then
    if [ "$MODE" = "copy" ]; then
      echo "[dry-run] cp -r $skill_dir $dest"
    else
      echo "[dry-run] ln -s $skill_dir $dest"
    fi
    INSTALLED=$((INSTALLED + 1))
  else
    if [ "$MODE" = "copy" ]; then
      cp -r "$skill_dir" "$dest"
      echo "COPY  $skill_name"
    else
      ln -s "$skill_dir" "$dest"
      echo "LINK  $skill_name -> $skill_dir"
    fi
    INSTALLED=$((INSTALLED + 1))
  fi
done

echo ""
echo "Done: $INSTALLED installed, $SKIPPED skipped, $ERRORS errors"
