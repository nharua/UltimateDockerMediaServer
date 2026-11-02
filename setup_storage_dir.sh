#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
echo "setup_storage_dir.sh now delegates to configure_storage.sh; pass --env-file /path/to/.env." >&2
exec bash "$SCRIPT_DIR/configure_storage.sh" "$@"
