"""Shared Plotly chart helpers with consistent H&M styling."""
import plotly.express as px
import plotly.graph_objects as go

HM_RED    = "#E50010"
HM_DARK   = "#1A1A1A"
HM_GRAY   = "#F5F5F5"
HM_COLORS = [
    "#E50010", "#FF6B6B", "#FFB3B3",
    "#1A1A1A", "#666666", "#AAAAAA",
    "#C8102E", "#FF8C00", "#FFC0CB",
]

LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, sans-serif", color=HM_DARK),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=16, r=16, t=40, b=16),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def apply_style(fig: go.Figure) -> go.Figure:
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_xaxes(showgrid=False, linecolor="#E0E0E0")
    fig.update_yaxes(gridcolor="#F0F0F0", linecolor="#E0E0E0")
    return fig


def bar(df, x, y, title="", color=HM_RED, **kwargs):
    fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=[color], **kwargs)
    return apply_style(fig)


def line(df, x, y, title="", color=HM_RED, **kwargs):
    fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=[color], **kwargs)
    fig.update_traces(line_width=2.5)
    return apply_style(fig)


def pie(df, names, values, title="", **kwargs):
    fig = px.pie(
        df, names=names, values=values, title=title,
        color_discrete_sequence=HM_COLORS, hole=0.45, **kwargs
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    return apply_style(fig)


def histogram(df, x, title="", nbins=30, color=HM_RED, **kwargs):
    fig = px.histogram(df, x=x, title=title, nbins=nbins,
                       color_discrete_sequence=[color], **kwargs)
    return apply_style(fig)
