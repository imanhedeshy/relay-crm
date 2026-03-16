#!/bin/sh

set -eu

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SERVICE_DIR="${1:?service directory is required}"
ENV_PATH="$ROOT_DIR/.env"
BACKUP_PATH="$(mktemp)"
HAD_ENV=0

if [ -f "$ENV_PATH" ]; then
  cp "$ENV_PATH" "$BACKUP_PATH"
  HAD_ENV=1
fi

restore_env() {
  if [ "$HAD_ENV" -eq 1 ]; then
    cp "$BACKUP_PATH" "$ENV_PATH"
  else
    rm -f "$ENV_PATH"
  fi

  rm -f "$BACKUP_PATH"
}

trap restore_env EXIT INT TERM HUP

cp "$ROOT_DIR/.env.example" "$ENV_PATH"
ROOT_DIR_FOR_PY="$ROOT_DIR" python3 - <<'PY'
import os
from pathlib import Path

env_path = Path(os.environ["ROOT_DIR_FOR_PY"]) / ".env"
lines = env_path.read_text().splitlines()
docker_only_prefixes = (
    "AUTH_DB_HOST=",
    "COMPANY_DB_HOST=",
    "CRM_DB_HOST=",
    "WORKFLOW_DB_HOST=",
)
filtered = [line for line in lines if not line.startswith(docker_only_prefixes)]
filtered.append("USE_POSTGRES=false")
env_path.write_text("\n".join(filtered) + "\n")
PY

. "$ROOT_DIR/.venv/bin/activate"
cd "$ROOT_DIR/$SERVICE_DIR"
python manage.py test
