"""Reusable layout primitives for the dashboard UI."""

from __future__ import annotations

from typing import Iterable, List, Optional

from dash import html

from python_stocks.dashboard.theme import Theme, get_theme, surface_style

SPACING = {"xs": "6px", "sm": "10px", "md": "16px", "lg": "24px"}


def muted_text(theme: Theme) -> dict:
    return {"color": theme["muted_text"], "margin": 0}


def page_header(
    title: str, subtitle: str, *, theme_key: str, controls: Optional[List] = None
) -> html.Div:
    theme = get_theme(theme_key)
    header_children: List = [
        text_stack(
            [
                html.Span(
                    subtitle,
                    style={
                        "fontSize": "14px",
                        "fontWeight": 600,
                        "color": theme["muted_text"],
                    },
                ),
                html.H1(title, style={"margin": 0, "fontSize": "26px"}),
            ],
            gap="4px",
        )
    ]
    if controls:
        header_children.append(
            html.Div(
                controls,
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": SPACING["sm"],
                    "flexWrap": "wrap",
                },
            )
        )
    return html.Div(
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "gap": SPACING["md"],
            "flexWrap": "wrap",
        },
        children=header_children,
    )


def text_stack(children: Iterable, gap: str = SPACING["sm"]) -> html.Div:
    return html.Div(
        children=children,
        style={"display": "flex", "flexDirection": "column", "gap": gap},
    )


def surface_card(
    *,
    theme_key: str,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    children: Optional[List] = None,
    footer: Optional[html.Div] = None,
) -> html.Div:
    theme = get_theme(theme_key)
    body: List = []
    if title:
        body.append(html.H3(title, style={"margin": 0, "fontWeight": 700}))
    if subtitle:
        body.append(html.P(subtitle, style=muted_text(theme) | {"fontSize": "14px"}))
    if children:
        body.extend(children)
    if footer:
        body.append(footer)
    return html.Div(
        style=surface_style(theme)
        | {"display": "flex", "flexDirection": "column", "gap": SPACING["sm"]},
        children=body,
    )


def pill(label: str, *, theme_key: str) -> html.Span:
    theme = get_theme(theme_key)
    return html.Span(
        label,
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "gap": "6px",
            "padding": "4px 10px",
            "borderRadius": "999px",
            "fontSize": "12px",
            "background": f"rgba(37, 99, 235, {0.12 if theme['mode']=='light' else 0.25})",
            "color": theme["accent"],
            "border": f"1px solid {theme['grid']}",
        },
    )


def button_link(
    label: str, *, href: str, theme_key: str, primary: bool = True
) -> html.A:
    theme = get_theme(theme_key)
    base_style = {
        "display": "inline-flex",
        "alignItems": "center",
        "justifyContent": "center",
        "padding": "10px 16px",
        "borderRadius": "12px",
        "fontWeight": 600,
        "textDecoration": "none",
        "transition": "transform 0.1s ease, box-shadow 0.1s ease",
        "border": f"1px solid {theme['grid']}",
    }
    if primary:
        base_style |= {
            "background": theme["accent"],
            "color": "#0b1224" if theme["mode"] == "light" else "#0f172a",
            "boxShadow": "0 10px 30px rgba(37,99,235,0.25)",
        }
    else:
        base_style |= {"background": "transparent", "color": theme["text"]}
    return html.A(label, href=href, style=base_style)


def eyebrow(label: str, *, theme_key: str) -> html.Span:
    theme = get_theme(theme_key)
    return html.Span(
        label,
        style={
            "textTransform": "uppercase",
            "letterSpacing": "0.08em",
            "fontSize": "12px",
            "color": theme["muted_text"],
        },
    )


def kpi_stat(*, label: str, value: str, caption: str, theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "4px",
            "padding": "10px 12px",
            "borderRadius": "12px",
            "background": f"rgba(22, 163, 74, {0.08 if theme['mode']=='light' else 0.2})",
            "border": f"1px solid {theme['grid']}",
        },
        children=[
            html.Span(label, style={"fontSize": "12px", "color": theme["muted_text"]}),
            html.Strong(value, style={"fontSize": "20px"}),
            html.Span(
                caption, style={"fontSize": "13px", "color": theme["muted_text"]}
            ),
        ],
    )


def section_header(
    *, title: str, description: str, theme_key: str, eyebrow_text: Optional[str] = None
) -> html.Div:
    theme = get_theme(theme_key)
    return html.Div(
        children=[
            *(
                [eyebrow(eyebrow_text, theme_key=theme_key)]
                if eyebrow_text
                else []
            ),
            html.Div(title, style={"fontWeight": 700, "fontSize": "20px"}),
            html.P(description, style=muted_text(theme)),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "6px",
        },
    )


def section_block(
    *,
    title: str,
    description: str,
    theme_key: str,
    content: List,
    eyebrow_text: Optional[str] = None,
) -> html.Section:
    return html.Section(
        style={"display": "flex", "flexDirection": "column", "gap": SPACING["md"]},
        children=[
            section_header(
                title=title,
                description=description,
                theme_key=theme_key,
                eyebrow_text=eyebrow_text,
            ),
            content,
        ],
    )


def responsive_grid(
    children: List, *, min_width: str = "240px", gap: str = SPACING["md"]
) -> html.Div:
    return html.Div(
        children=children,
        style={
            "display": "grid",
            "gridTemplateColumns": f"repeat(auto-fit, minmax({min_width}, 1fr))",
            "gap": gap,
        },
    )


def hero_banner(
    *,
    title: str,
    subtitle: str,
    thesis: str,
    kpis: List[html.Div],
    actions: List[html.A],
    theme_key: str,
) -> html.Div:
    theme = get_theme(theme_key)
    gradient = (
        "linear-gradient(135deg, rgba(56,189,248,0.16), rgba(79,70,229,0.16))"
        if theme["mode"] == "light"
        else "linear-gradient(135deg, rgba(14,165,233,0.25), rgba(99,102,241,0.25))"
    )
    thesis_box = html.Div(
        [
            html.Strong("Can't beat the market? "),
            html.Span(thesis),
        ],
        style={
            "padding": "10px 12px",
            "borderRadius": "12px",
            "background": f"rgba(15,23,42,{0.04 if theme['mode']=='light' else 0.35})",
            "border": f"1px solid {theme['grid']}",
            "fontStyle": "italic",
        },
    )
    return html.Div(
        className="hero-grid",
        style={
            "padding": SPACING["lg"],
            "borderRadius": "18px",
            "background": gradient,
            "border": f"1px solid {theme['grid']}",
            "display": "grid",
            "gridTemplateColumns": "1.6fr 1fr",
            "gap": SPACING["md"],
            "alignItems": "center",
            "boxShadow": "0 20px 60px rgba(15,23,42,0.12)",
        },
        children=[
            text_stack(
                [
                    pill(
                        "Can't beat the market? Start by matching it.",
                        theme_key=theme_key,
                    ),
                    html.H2(title, style={"margin": 0}),
                    html.P(subtitle, style=muted_text(theme) | {"fontSize": "16px"}),
                    thesis_box,
                    html.Div(
                        actions,
                        style={
                            "display": "flex",
                            "gap": SPACING["sm"],
                            "flexWrap": "wrap",
                        },
                    ),
                ],
                gap=SPACING["sm"],
            ),
            responsive_grid(kpis, min_width="200px", gap=SPACING["sm"]),
        ],
    )
