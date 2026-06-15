# Source: github.com/jackson-video-resources/yt-strategy-agent
# Recency-weighted similarity grouping for rolling 5-video window.
#
# Weighting scheme (position 0 = most recent):
#   [1.00, 0.70, 0.50, 0.35, 0.25]
#
# Similarity grouping:
#   - Model: all-MiniLM-L6-v2
#   - Threshold: cosine similarity > 0.82 → same group
#   - effective_confidence = mean(confidence_i * weight_i) across group members
#   - Groups below 0.30 min effective confidence are filtered out
#
# Processes 4 sections: buy_rules, sell_rules, risk_notes, timing_notes

from __future__ import annotations

from functools import lru_cache
from typing import Optional

import numpy as np

import store

WEIGHTS = [1.00, 0.70, 0.50, 0.35, 0.25]
SIM_THRESHOLD = 0.82
MIN_CONFIDENCE = 0.30


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def _embed(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.array([])
    model = _get_model()
    embs = model.encode(texts, normalize_embeddings=True)
    return embs


def _group(items: list[str]) -> list[list[int]]:
    """Group similar items by cosine similarity > SIM_THRESHOLD."""
    if not items:
        return []
    embs = _embed(items)
    assigned = [-1] * len(items)
    groups: list[list[int]] = []
    for i in range(len(items)):
        if assigned[i] != -1:
            continue
        group = [i]
        assigned[i] = len(groups)
        for j in range(i + 1, len(items)):
            if assigned[j] != -1:
                continue
            sim = float(np.dot(embs[i], embs[j]))
            if sim > SIM_THRESHOLD:
                group.append(j)
                assigned[j] = len(groups)
        groups.append(group)
    return groups


def _process_section(
    section_key: str,
    text_key: str,
    conf_key: str,
    extractions: list[tuple[dict, float]],
) -> list[dict]:
    """
    Process one section (buy_rules / sell_rules / risk_notes / timing_notes).
    Returns list of {text, effective_confidence, source_videos} dicts.
    """
    # Collect all items with their weights
    all_items: list[tuple[str, float, float, int]] = []  # (text, confidence, weight, video_idx)
    for video_idx, (extraction, weight) in enumerate(extractions):
        for entry in extraction.get(section_key, []):
            text = entry.get(text_key, "") or entry.get("rule", "") or entry.get("note", "")
            conf = float(entry.get("confidence", 0.5))
            if text.strip():
                all_items.append((text, conf, weight, video_idx))

    if not all_items:
        return []

    texts = [item[0] for item in all_items]
    groups = _group(texts)

    results = []
    for group_indices in groups:
        members = [all_items[i] for i in group_indices]
        # Compute effective confidence as weighted mean
        weighted_confs = [conf * weight for _, conf, weight, _ in members]
        eff_conf = sum(weighted_confs) / len(weighted_confs)
        if eff_conf < MIN_CONFIDENCE:
            continue
        # Canonical text = member from most recent video (lowest video_idx)
        best = min(members, key=lambda x: x[3])
        results.append({
            "text":                 best[0],
            "effective_confidence": round(eff_conf, 4),
            "source_videos":        list({m[3] for m in members}),
        })

    return sorted(results, key=lambda x: x["effective_confidence"], reverse=True)


def rebuild(handle: str, extractions_newest_first: list[dict]) -> None:
    """
    Rebuild the weighted rolling strategy from the latest extractions.
    Writes rules.json and strategy.md via store module.

    Args:
        handle:                  Channel @handle.
        extractions_newest_first: List of extraction dicts, newest first, max WINDOW items.
    """
    n = min(len(extractions_newest_first), len(WEIGHTS))
    weighted = [(extractions_newest_first[i], WEIGHTS[i]) for i in range(n)]

    # Strategy summary — from most recent video
    summary = ""
    if weighted:
        summary = weighted[0][0].get("strategy_summary", "")

    buy_rules   = _process_section("buy_rules",   "rule", "confidence", weighted)
    sell_rules  = _process_section("sell_rules",  "rule", "confidence", weighted)
    risk_notes  = _process_section("risk_notes",  "note", "confidence", weighted)
    timing_notes = _process_section("timing_notes", "note", "confidence", weighted)

    rules = {
        "strategy_summary": summary,
        "buy_rules":        buy_rules,
        "sell_rules":       sell_rules,
        "risk_notes":       risk_notes,
        "timing_notes":     timing_notes,
    }

    store.write_rules_json(handle, rules)
    store.write_strategy_md(handle, rules)
