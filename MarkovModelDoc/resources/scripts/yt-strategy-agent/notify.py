# Source: github.com/jackson-video-resources/yt-strategy-agent
# SMTP email sender for video brief alerts.
# Sends via Gmail App Password (smtp.gmail.com:587 with TLS).
#
# Required env vars:
#   SMTP_HOST     = smtp.gmail.com
#   SMTP_PORT     = 587
#   SMTP_USER     = your@gmail.com
#   SMTP_PASSWORD = xxxx xxxx xxxx xxxx  (Gmail App Password)
#   EMAIL_TO      = recipient@email.com

from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "EMAIL_TO"]


def _check_config() -> None:
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        raise RuntimeError(f"Missing email config vars: {missing}. Check your .env file.")


def _format_rules(rules: list[dict], top_n: int = 5) -> str:
    if not rules:
        return "  (none)\n"
    lines = []
    for r in rules[:top_n]:
        text = r.get("text", r.get("rule", r.get("note", "")))
        conf = r.get("effective_confidence", r.get("confidence", 0))
        lines.append(f"  [{conf:.0%}] {text}")
    return "\n".join(lines) + "\n"


def _diff_rule_sets(prior: list[dict], new: list[dict]) -> tuple[list[str], list[str]]:
    prior_texts = {r.get("text", "") for r in (prior or [])}
    new_texts   = {r.get("text", "") for r in (new or [])}
    added   = [t for t in new_texts   if t not in prior_texts]
    removed = [t for t in prior_texts if t not in new_texts]
    return added, removed


def build_email_body(
    channel_title: str,
    video: dict,
    extracted: dict,
    prior_rules: dict | None,
    new_rules: dict | None,
    change_logged: bool,
    impact: str,
    handle: str,
) -> str:
    vid_url = f"https://www.youtube.com/watch?v={video['id']}"
    lines = [
        f"Channel:    {channel_title} (@{handle})",
        f"Video:      {video['title']}",
        f"URL:        {vid_url}",
        f"Published:  {video.get('published_at', 'unknown')}",
        "",
        "─" * 60,
        "IMPACT SUMMARY",
        "─" * 60,
        impact,
        "",
    ]

    if change_logged:
        lines += ["⚠️  STRATEGY SHIFT DETECTED — see changelog.md", ""]

    lines += [
        "─" * 60,
        "STRATEGY SUMMARY (this video)",
        "─" * 60,
        extracted.get("strategy_summary", "(none)"),
        "",
        "BUY RULES:",
        _format_rules(extracted.get("buy_rules", [])),
        "SELL RULES:",
        _format_rules(extracted.get("sell_rules", [])),
        "RISK NOTES:",
        _format_rules(extracted.get("risk_notes", [])),
        "TIMING NOTES:",
        _format_rules(extracted.get("timing_notes", [])),
    ]

    if prior_rules and new_rules:
        added_buy, removed_buy = _diff_rule_sets(
            prior_rules.get("buy_rules", []), new_rules.get("buy_rules", [])
        )
        added_sell, removed_sell = _diff_rule_sets(
            prior_rules.get("sell_rules", []), new_rules.get("sell_rules", [])
        )
        if added_buy or removed_buy or added_sell or removed_sell:
            lines += [
                "",
                "─" * 60,
                "ROLLING RULES — CHANGES",
                "─" * 60,
            ]
            for rule in added_buy:
                lines.append(f"  + BUY:  {rule}")
            for rule in removed_buy:
                lines.append(f"  - BUY:  {rule}")
            for rule in added_sell:
                lines.append(f"  + SELL: {rule}")
            for rule in removed_sell:
                lines.append(f"  - SELL: {rule}")

    if new_rules:
        lines += [
            "",
            "─" * 60,
            "CURRENT ROLLING STRATEGY",
            "─" * 60,
            new_rules.get("strategy_summary", "(none)"),
            "",
            "TOP BUY RULES:",
            _format_rules(new_rules.get("buy_rules", [])),
            "TOP SELL RULES:",
            _format_rules(new_rules.get("sell_rules", [])),
        ]

    lines += [
        "",
        "─" * 60,
        f"Files on VPS: ~/yt-strategy-agent/channels/{handle}/",
        "─" * 60,
    ]

    return "\n".join(lines)


def send_email(subject: str, body: str) -> None:
    """Send a plain-text email via SMTP with TLS."""
    _check_config()

    msg = MIMEMultipart()
    msg["From"]    = os.environ["SMTP_USER"]
    msg["To"]      = os.environ["EMAIL_TO"]
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as server:
        server.starttls()
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        server.send_message(msg)
