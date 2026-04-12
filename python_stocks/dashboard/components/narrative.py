"""Narrative models for chart companion copy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChartNarrative:
    """Short chart explanation rendered in a fixed three-row layout."""

    what_changed: str
    why_it_matters: str
    what_to_watch_next: str
