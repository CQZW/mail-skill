#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1 && python3 -c "import cryptography" >/dev/null 2>&1; then
  exec python3 "$DIR/prepare-tool-args.py" "$@"
fi

if command -v python >/dev/null 2>&1 && python -c "import cryptography" >/dev/null 2>&1; then
  exec python "$DIR/prepare-tool-args.py" "$@"
fi

if command -v node >/dev/null 2>&1; then
  exec node "$DIR/prepare-tool-args.js" "$@"
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$DIR/prepare-tool-args.py" "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python "$DIR/prepare-tool-args.py" "$@"
fi

echo "No supported runtime found. Install Python or Node.js." >&2
exit 1
