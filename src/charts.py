"""Plotly chart builders using one consistent, colour-blind-safe palette."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
INK, MUTED, GRID = "#10233d", "#5b6b82", "#e3e8f0"
GENDER_COLORS = {"Female": ORANGE, "Male": BLUE}
LEVEL_COLORS = {"Beginner": AQUA, "Intermediate": BLUE, "Advanced": VIOLET}
TYPE_COLORS = {"Free": AQUA, "Paid": ORANGE}
SEQ = [[0, "#eef4fc"], [1, "#6aa5e8"]]  # light enough that dark text is always readable


def _base(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=16, color=INK)),
        height=height, paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font=dict(family="Inter, Segoe UI, sans-serif", color=INK, size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(color=MUTED)),
        hoverlabel=dict(bgcolor="#ffffff", font_color=INK),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def bar(df: pd.DataFrame, x: str, y: str, title: str, color: str = BLUE, horizontal: bool = False,
        fmt: str = ",.0f", height: int = 380) -> go.Figure:
    if horizontal:
        d = df.iloc[::-1]
        fig = go.Figure(go.Bar(x=d[y], y=d[x], orientation="h", marker_color=color,
                               text=d[y], texttemplate="%{text:" + fmt + "}", textposition="outside",
                               cliponaxis=False, hovertemplate="%{y}: %{x:" + fmt + "}<extra></extra>"))
        fig.update_xaxes(showgrid=True, gridcolor=GRID, visible=False)
        fig.update_yaxes(showgrid=False)
    else:
        fig = go.Figure(go.Bar(x=df[x], y=df[y], marker_color=color, text=df[y],
                               texttemplate="%{text:" + fmt + "}", textposition="outside",
                               cliponaxis=False, hovertemplate="%{x}: %{y:" + fmt + "}<extra></extra>"))
    fig.update_traces(marker_cornerradius=4)
    return _base(fig, title, height)


def grouped_bar(ct: pd.DataFrame, title: str, colors: dict | None = None, stacked: bool = False,
                pct: bool = False, height: int = 400, horizontal: bool = False) -> go.Figure:
    """ct: rows = x categories, columns = series."""
    palette = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
    fig = go.Figure()
    for i, col in enumerate(ct.columns):
        c = (colors or {}).get(col, palette[i % len(palette)])
        suffix = "%" if pct else ""
        fmt = ".1f" if pct else ",.0f"
        if horizontal:
            fig.add_bar(y=ct.index, x=ct[col], name=str(col), marker_color=c, orientation="h",
                        hovertemplate="%{y} - " + str(col) + ": %{x:" + fmt + "}" + suffix + "<extra></extra>")
        else:
            fig.add_bar(x=ct.index, y=ct[col], name=str(col), marker_color=c,
                        hovertemplate="%{x} - " + str(col) + ": %{y:" + fmt + "}" + suffix + "<extra></extra>")
    fig.update_layout(barmode="stack" if stacked else "group", bargap=0.25)
    if stacked:
        fig.update_traces(marker_line=dict(color="#ffffff", width=2))
    else:
        fig.update_traces(marker_cornerradius=3)
    return _base(fig, title, height)


def donut(labels, values, title: str, colors: dict | None = None, height: int = 340) -> go.Figure:
    palette = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
    cols = [(colors or {}).get(l, palette[i % len(palette)]) for i, l in enumerate(labels)]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.62, sort=False, marker=dict(
        colors=cols, line=dict(color="#ffffff", width=2)), textinfo="percent", textfont=dict(size=13),
        hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>"))
    return _base(fig, title, height)


def heatmap(ct: pd.DataFrame, title: str, pct: bool = False, height: int = 460) -> go.Figure:
    z = ct.values
    txt = [[f"{v:.1f}%" if pct else f"{v:,.0f}" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ct.columns], y=[str(i) for i in ct.index], colorscale=SEQ,
        text=txt, texttemplate="%{text}", xgap=2, ygap=2, colorbar=dict(thickness=12, outlinewidth=0,
        title=dict(text="% of row" if pct else "Enrollments", side="right")),
        hovertemplate="%{y} x %{x}: %{text}<extra></extra>"))
    fig.update_traces(textfont=dict(color=INK, size=12))
    fig.update_xaxes(side="bottom", tickangle=-30 if len(ct.columns) > 6 else 0)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _base(fig, title, height)


def line(df: pd.DataFrame, x: str, y: str, title: str, color: str = BLUE, height: int = 340) -> go.Figure:
    fig = go.Figure(go.Scatter(x=df[x], y=df[y], mode="lines+markers", line=dict(color=color, width=2),
                               marker=dict(size=8, color=color, line=dict(color="#fff", width=2)),
                               hovertemplate="%{x|%b %Y}: %{y:,}<extra></extra>"))
    return _base(fig, title, height)


def lorenz(df: pd.DataFrame, title: str, height: int = 380) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=[0, 100], y=[0, 100], mode="lines", name="Equal participation",
                    line=dict(color=MUTED, dash="dot", width=1.5), hoverinfo="skip")
    fig.add_scatter(x=df["Learners %"], y=df["Enrollments %"], mode="lines", name="Actual",
                    line=dict(color=BLUE, width=2.5), fill="tonexty", fillcolor="rgba(42,120,214,0.10)",
                    hovertemplate="Top %{x:.0f}% of learners -> %{y:.0f}% of enrollments<extra></extra>")
    fig.update_xaxes(title="Cumulative % of learners (most active first)", range=[0, 100])
    fig.update_yaxes(title="Cumulative % of enrollments", range=[0, 100])
    _base(fig, title, height + 40)
    fig.update_layout(legend=dict(orientation="h", y=-0.28, x=0))
    return fig
