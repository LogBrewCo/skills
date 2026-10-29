#!/usr/bin/env bash
# Builds the Gemini CLI extension archive at the path in $1. Gemini CLI loads
# extension skills only from skills/ at the extension root, so the archive
# holds gemini-extension.json, a copy of plugins/logbrew/skills, README.md, and
# LICENSE at its root. Gemini CLI installs the archive from the newest GitHub
# release.
set -euo pipefail
[[ $# -eq 1 ]] || { echo "usage: $0 OUTPUT.tar.gz" >&2; exit 2; }
root="$(cd "$(dirname "$0")/.." && pwd)"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
cp "$root/gemini-extension.json" "$root/README.md" "$root/LICENSE" "$stage/"
cp -R "$root/plugins/logbrew/skills" "$stage/skills"
COPYFILE_DISABLE=1 tar -czf "$1" -C "$stage" gemini-extension.json README.md LICENSE skills
