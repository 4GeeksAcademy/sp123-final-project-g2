#!/usr/bin/env bash
fuser -k 3001/tcp || true
sleep 0.5
PY=$(pipenv --py 2>/dev/null || true)
if [ -z "$PY" ]; then
  PY=$(which python || true)
fi
"$PY" -m flask run --host=0.0.0.0 --port=3001
