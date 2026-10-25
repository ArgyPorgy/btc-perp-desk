#!/bin/bash
# Double-click to start the BTC Perp Desk (macOS): serves the dashboard + live news feed on 127.0.0.1:8787 and opens it.
cd "$(dirname "$0")"
PORT=8787
if curl -s -m 2 "http://127.0.0.1:$PORT/api/health" | grep -q '"ok": true'; then
  open "http://127.0.0.1:$PORT"
  echo "BTC Perp Desk already running at http://127.0.0.1:$PORT"
  exit 0
fi
# an old plain file server from an earlier version (no news feed) may still hold the port: replace it
OLD=$(lsof -tiTCP:$PORT -sTCP:LISTEN 2>/dev/null)
if [ -n "$OLD" ]; then
  if ps -o command= -p "$OLD" | grep -q "http.server $PORT"; then
    kill "$OLD"; sleep 1
  else
    echo "Port $PORT is used by another program: $(ps -o command= -p "$OLD"). Close it and try again."
    read -r -p "Press Enter to close."
    exit 1
  fi
fi
python3 server.py --port $PORT &
sleep 1.5
open "http://127.0.0.1:$PORT"
echo "BTC Perp Desk running at http://127.0.0.1:$PORT  (close this window to stop it)"
wait
