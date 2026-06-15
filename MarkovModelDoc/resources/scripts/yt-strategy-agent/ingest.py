# Source: github.com/jackson-video-resources/yt-strategy-agent
# Main ingest pipeline. Run with --once for a single pass.
#
# Pipeline per cycle:
#   1. Load channel list from channels.yaml
#   2. Fetch latest 5 uploads per channel via YouTube API
#   3. Fetch transcripts for unseen videos via Apify
#   4. Extract strategy via Claude (extract.py)
#   5. Detect strategy shifts (change_detect.py)
#   6. Rebuild weighted rules (weighting.py)
#   7. Persist to SQLite + markdown files (store.py)
#   8. Send email alert (notify.py)
#
# Usage:
#   python ingest.py --once

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

import change_detect
import extract
import notify
import store
import transcript
import weighting
from auth import get_youtube_service

WINDOW = 5  # rolling video window per channel


def load_channels(path: str = "channels.yaml") -> list[dict]:
    with open(path) as f:
        return yaml.safe_load(f) or []


def get_latest_videos(youtube, channel_id: str, limit: int = WINDOW) -> list[dict]:
    """Fetch the most recent `limit` video IDs from a channel's uploads playlist."""
    # Get uploads playlist ID
    ch_resp = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    items = ch_resp.get("items", [])
    if not items:
        return []
    playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    pl_resp = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=limit,
    ).execute()

    videos = []
    for item in pl_resp.get("items", []):
        sn = item["snippet"]
        videos.append({
            "id":           sn["resourceId"]["videoId"],
            "title":        sn["title"],
            "published_at": sn["publishedAt"],
        })
    return videos


def run_once() -> int:
    """Run one full ingest cycle. Returns number of new videos processed."""
    channels = load_channels()
    youtube  = get_youtube_service()
    total_new = 0

    for ch in channels:
        handle     = ch["handle"]
        channel_id = ch["id"]
        ch_title   = ch.get("title", handle)

        videos = get_latest_videos(youtube, channel_id, WINDOW)
        new_videos = [v for v in videos if not store.seen(v["id"])]

        if not new_videos:
            continue

        # Batch fetch transcripts via Apify
        video_ids  = [v["id"] for v in new_videos]
        transcripts = transcript.fetch_transcripts(video_ids)

        for video in new_videos:
            vid_id    = video["id"]
            vid_title = video["title"]
            tx        = transcripts.get(vid_id)

            if not tx:
                store.mark_seen(vid_id, channel_id, vid_title, None)
                continue

            # Extract strategy via Claude
            try:
                extracted = extract.extract_from_transcript(tx)
            except Exception as e:
                print(f"[ingest] extract error for {vid_id}: {e}")
                store.mark_seen(vid_id, channel_id, vid_title, None)
                continue

            if not extracted:
                store.mark_seen(vid_id, channel_id, vid_title, None)
                continue

            # Prior rules before this video
            prior_rules = store.read_rules_json(handle)

            # Persist per-video notes
            store.write_video_md(handle, video, extracted)
            store.mark_seen(vid_id, channel_id, vid_title, extracted)

            # Rebuild weighted rolling strategy
            latest_extractions = store.latest_extractions(handle, n=WINDOW)
            weighting.rebuild(handle, latest_extractions)
            new_rules = store.read_rules_json(handle)

            # Detect strategy shift
            try:
                change_logged = change_detect.detect_and_log(handle, vid_id, vid_title, extracted)
            except Exception as e:
                print(f"[ingest] change_detect error: {e}")
                change_logged = False

            # Impact summary
            try:
                impact = extract.summarize_impact(extracted, prior_rules, ch_title)
            except Exception as e:
                impact = f"Impact summary unavailable: {e}"

            # Email notification
            try:
                subject = f"[{ch_title}] {vid_title}"
                body    = notify.build_email_body(
                    channel_title=ch_title,
                    video=video,
                    extracted=extracted,
                    prior_rules=prior_rules,
                    new_rules=new_rules,
                    change_logged=change_logged,
                    impact=impact,
                    handle=handle,
                )
                notify.send_email(subject, body)
            except Exception as e:
                print(f"[ingest] notify error: {e}")

            total_new += 1

    return total_new


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    args = parser.parse_args()
    if args.once:
        n = run_once()
        print(f"Done — {n} new video(s) processed.")
        sys.exit(0)
    else:
        print("Use --once to run a single cycle, or use watcher.py for continuous polling.")
        sys.exit(1)
