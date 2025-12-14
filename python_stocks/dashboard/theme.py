"""Shared theming configuration for the dashboard."""

from __future__ import annotations

from typing import Dict

Theme = Dict[str, str]


THEMES: Dict[str, Theme] = {
    "light": {
        "mode": "light",
        "background": "#f8fafc",
        "panel": "#ffffff",
        "text": "#0f172a",
        "muted_text": "#475569",
        "accent": "#2563eb",
        "accent_alt": "#16a34a",
        "grid": "rgba(148, 163, 184, 0.4)",
        "plot_bg": "#ffffff",
        "paper_bg": "#ffffff",
    },
    "dark": {
        "mode": "dark",
        "background": "#0b1224",
        "panel": "#111827",
        "text": "#e2e8f0",
        "muted_text": "#cbd5e1",
        "accent": "#38bdf8",
        "accent_alt": "#a3e635",
        "grid": "rgba(148, 163, 184, 0.25)",
        "plot_bg": "#0f172a",
        "paper_bg": "#0f172a",
    },
}

DEFAULT_THEME_KEY = "light"


def get_theme(mode: str | None) -> Theme:
    """Return the theme configuration for the requested mode.

    Unknown modes gracefully fall back to the default palette.
    """

    if not mode:
        return THEMES[DEFAULT_THEME_KEY]
    return THEMES.get(mode, THEMES[DEFAULT_THEME_KEY])


def surface_style(theme: Theme) -> Dict[str, str]:
    return {
        "backgroundColor": theme["panel"],
        "color": theme["text"],
        "border": f"1px solid {theme['grid']}",
        "padding": "16px",
        "borderRadius": "12px",
        "boxShadow": "0 8px 30px rgba(0,0,0,0.08)",
    }


def page_style(theme: Theme) -> Dict[str, str]:
    return {
        "backgroundColor": theme["background"],
        "color": theme["text"],
        "minHeight": "100vh",
        "padding": "24px",
        "transition": "background-color 0.2s ease, color 0.2s ease",
        "fontFamily": "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
    }
