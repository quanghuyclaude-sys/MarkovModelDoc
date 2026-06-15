# Source: github.com/jackson-video-resources/yt-strategy-agent
# Long-running watcher process — polls every 10 minutes (600 seconds).
# Calls ingest.run_once() on each cycle.
# Logs UTC timestamp and new video count per cycle.
# Designed for systemd / PM2 deployment on VPS.
#
# Usage:
#   python watcher.py
#
# Deployment:
#   systemctl enable --now watcher   (after bootstrap_vps.sh)

from __future__ import annotations

import time
import traceback
from datetime import datetime, timezone

import ingest

INTERVAL_SECONDS = 600  # 10 minutes


def main() -> None:
    print(f"[watcher] Starting — polling every {INTERVAL_SECONDS}s", flush=True)
    while True:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"[watcher] {ts} cycle starting", flush=True)
        try:
            new_count = ingest.run_once()
            print(f"[watcher] {ts} ok — {new_count} new video(s)", flush=True)
        except Exception:
            print(f"[watcher] {ts} ERROR:", flush=True)
            traceback.print_exc()
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
