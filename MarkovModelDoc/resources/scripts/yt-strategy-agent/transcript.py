# Source: github.com/jackson-video-resources/yt-strategy-agent
# Fetches YouTube video transcripts via Apify (karamelo/youtube-transcripts actor).
# Handles IP rotation that YouTube requires from cloud servers.
#
# Requirements:
#   APIFY_TOKEN in .env
#   pip install apify-client python-dotenv
#
# Usage:
#   from transcript import fetch_transcripts
#   results = fetch_transcripts(["videoId1", "videoId2"])
#   # returns {"videoId1": "transcript text", "videoId2": None}

from __future__ import annotations

import html
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "karamelo/youtube-transcripts"
MAX_RETRIES = 8


def fetch_transcripts(video_ids: list[str]) -> dict[str, str | None]:
    """
    Fetch transcripts for a list of YouTube video IDs via Apify.

    Args:
        video_ids: List of YouTube video IDs (not full URLs).

    Returns:
        Dict mapping video_id → transcript text (str) or None if unavailable.

    Raises:
        RuntimeError: If APIFY_TOKEN is not set.
    """
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN not set in environment or .env file.")

    client = ApifyClient(token)

    urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]

    run = client.actor(ACTOR_ID).call(
        run_input={
            "urls":         urls,
            "outputFormat": "singleStringText",
            "maxRetries":   MAX_RETRIES,
        }
    )

    results: dict[str, str | None] = {vid: None for vid in video_ids}

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        # Extract video ID from URL
        url = item.get("url", "")
        vid_id = url.split("v=")[-1].split("&")[0] if "v=" in url else None
        if not vid_id or vid_id not in results:
            continue

        captions = item.get("captions", "") or item.get("transcript", "")
        if captions:
            results[vid_id] = html.unescape(str(captions))

    return results
