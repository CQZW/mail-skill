#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$DIR/doctor.py" "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python "$DIR/doctor.py" "$@"
fi

if command -v node >/dev/null 2>&1; then
  exec node "$DIR/doctor.js" "$@"
fi

echo "No supported runtime found. Install Python or Node.js." >&2
exit 1
