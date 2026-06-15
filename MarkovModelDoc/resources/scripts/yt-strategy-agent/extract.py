# Source: github.com/jackson-video-resources/yt-strategy-agent
# Extracts structured trading strategies from YouTube transcripts using Claude API.
# Uses prompt caching for cost efficiency (system prompt cached as ephemeral).
#
# Model: claude-opus-4-7
# Max tokens: 4096
# Output: pure JSON (no markdown fences)
#
# JSON schema returned:
# {
#   "strategy_summary": str,
#   "buy_rules":    [{"rule": str, "confidence": float, "source_quote": str}],
#   "sell_rules":   [{"rule": str, "confidence": float, "source_quote": str}],
#   "risk_notes":   [{"note": str, "confidence": float, "source_quote": str}],
#   "timing_notes": [{"note": str, "confidence": float, "source_quote": str}],
#   "executed_trades": [{"asset": str, "direction": str, "entry": str, "exit": str, "outcome": str}],
#   "strategy_shift": {"changed": bool, "what_changed": str, "vs_prior": str}
# }
#
# Confidence scores (0.0-1.0) indicate statement clarity.
# source_quote: verbatim from transcript, <=200 chars.
# Empty arrays when section has no relevant content.

from __future__ import annotations

import json
import os
from typing import Optional

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    base_url=os.environ.get("ANTHROPIC_BASE_URL"),
)

SYSTEM_PROMPT = """You are a quantitative trading strategy extraction specialist.

Your job is to read YouTube trading video transcripts and extract concrete, actionable trading rules.

EXTRACTION RULES:
1. Extract only concrete, rules-based trading conditions — not vague commentary
2. Confidence scores (0.0-1.0) reflect how clearly the rule was stated:
   - 1.0 = explicit rule with exact numbers ("buy when RSI drops below 30")
   - 0.7 = clear rule without exact numbers ("buy on RSI oversold")
   - 0.4 = implied rule or inference ("seems to wait for pullbacks")
3. source_quote: exact verbatim text from the transcript, max 200 characters
4. Empty arrays when a section has no relevant content
5. strategy_shift.changed = true only when the trader explicitly says they changed their approach

OUTPUT: Return ONLY a valid JSON object. No markdown fences. No commentary. No explanation."""

EXTRACTION_SCHEMA = {
    "strategy_summary": "string — 2-3 sentence overview of the overall approach",
    "buy_rules": [{"rule": "string", "confidence": "float 0.0-1.0", "source_quote": "string <=200 chars"}],
    "sell_rules": [{"rule": "string", "confidence": "float 0.0-1.0", "source_quote": "string <=200 chars"}],
    "risk_notes": [{"note": "string", "confidence": "float 0.0-1.0", "source_quote": "string <=200 chars"}],
    "timing_notes": [{"note": "string", "confidence": "float 0.0-1.0", "source_quote": "string <=200 chars"}],
    "executed_trades": [{"asset": "string", "direction": "long|short", "entry": "string", "exit": "string", "outcome": "string"}],
    "strategy_shift": {"changed": "bool", "what_changed": "string", "vs_prior": "string"},
}

USER_PROMPT_TEMPLATE = """Extract trading rules from this transcript.

Return JSON matching this schema exactly:
{schema}

Transcript:
{transcript}"""


def extract_from_transcript(transcript: str) -> Optional[dict]:
    """
    Send a transcript to Claude with cached system prompt.
    Returns parsed JSON dict or None on failure.
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(
        schema=json.dumps(EXTRACTION_SCHEMA, indent=2),
        transcript=transcript,
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        print(f"[extract] Error: {e}")
        return None


def summarize_impact(
    new_extraction: dict,
    prior_rules: Optional[dict],
    channel_handle: str,
) -> str:
    """
    Analyze how a newly extracted strategy affects an existing paper-trading spec.
    Returns a 3-5 sentence brief.
    """
    if not prior_rules:
        return "No prior rules on record — this is the initial strategy extraction."

    prompt = f"""You are a trading strategy analyst.

Compare these two strategy states and produce a 3-5 sentence impact brief:
- What has changed in bias, conviction, or key levels?
- Are any invalidation levels dangerously close to current price?
- Should position sizing be adjusted?
- What is the recommended next action?

Channel: {channel_handle}

Prior rules (JSON):
{json.dumps(prior_rules, indent=2)}

New extraction (JSON):
{json.dumps(new_extraction, indent=2)}

Respond with plain text only. No headers. No bullet points. 3-5 sentences."""

    try:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Impact summary unavailable: {e}"
