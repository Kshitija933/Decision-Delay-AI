"""
DecisionDelay AI — Visualizer (Light Mode)
All Plotly chart functions with clean white/cobalt aesthetic.
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List

# ── Light-mode theme constants ──
BG       = "#0B1120"
SURFACE  = "#131F35"
COBALT   = "#6EE7F7"
COBALT2  = "#38BDF8"
SKY      = "#38BDF8"
CORAL    = "#FB7185"
AMBER    = "#FCD34D"
VIOLET   = "#A78BFA"
MINT     = "#34D399"
MUTED    = "#64748B"
TEXT     = "#0F172A"
TEXT_SUB = "#475569"
BORDER   = "rgba(110,231,247,0.10)"

CAUSE_COLORS = {
    "Fear of Failure":           "#FB7185",
    "Overwhelm / Complexity":    "#FCD34D",
    "Lack of Immediate Reward":  "#6EE7F7",
    "Past Failure Loop":         "#A78BFA",
    "Perfectionism":             "#FB8500",
    "Decision Fatigue":          "#38BDF8",
}

_layout_base = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color=TEXT, size=13),
    margin=dict(l=30, r=30, t=50, b=10),
)


def gauge_chart(severity: float, title: str = "Delay Severity") -> go.Figure:
    color = MINT if severity < 0.35 else AMBER if severity < 0.65 else CORAL
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(severity * 100, 1),
        delta={
            "reference": 50,
            "valueformat": ".1f",
            "font": {"size": 14, "color": CORAL},
            "increasing": {"color": CORAL},
            "decreasing": {"color": CORAL},
        },
        title={"text": title, "font": {"size": 14, "color": TEXT}},
        number={
            "suffix": "%",
            "font": {"size": 36, "color": color},
            "valueformat": ".1f",
        },
        domain={"x": [0.05, 0.95], "y": [0.0, 1.0]},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": TEXT_SUB,
                "tickfont": {"color": TEXT_SUB, "size": 10},
                "nticks": 6,
            },
            "bar": {"color": color, "thickness": 0.26},
            "bgcolor": "#F3F4F6",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  35],  "color": "rgba(52,211,153,0.10)"},
                {"range": [35, 65],  "color": "rgba(252,211,77,0.10)"},
                {"range": [65, 100], "color": "rgba(251,113,133,0.10)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "value": severity * 100,
            },
        },
    ))
    fig.update_layout(
        **_layout_base,
        height=270,
        autosize=True,
    )
    return fig


def radar_chart(inputs: Dict) -> go.Figure:
    categories = ["Task Difficulty", "Time-to-Reward", "Past Failures",
                  "Self-Efficacy", "Stress Level", "Goal Clarity",
                  "Motivation", "Habit Strength"]
    keys = ["task_difficulty", "time_to_reward", "past_failure_loops",
            "self_efficacy", "stress_level", "goal_clarity",
            "intrinsic_motivation", "habit_strength"]
    values = [inputs.get(k, 5) / 10 for k in keys]
    values += values[:1]
    cats = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=cats, fill="toself",
        fillcolor="rgba(26,86,219,0.08)",
        line=dict(color=COBALT, width=2.5),
        name="Your Profile",
    ))
    fig.update_layout(
        **_layout_base, height=320,
        polar=dict(
            bgcolor="#F9FAFB",
            radialaxis=dict(visible=True, range=[0, 1],
                            tickfont=dict(color=TEXT_SUB, size=9),
                            gridcolor="rgba(209,213,219,0.5)", linecolor="rgba(209,213,219,0.5)"),
            angularaxis=dict(tickfont=dict(color=TEXT_SUB, size=10),
                             gridcolor="rgba(209,213,219,0.3)"),
        ),
        showlegend=False,
        title=dict(text="Behavioral Profile", font=dict(size=14, color=TEXT)),
    )
    return fig


def probability_bar_chart(probs: Dict[str, float]) -> go.Figure:
    causes = list(probs.keys())
    values = list(probs.values())
    colors = [CAUSE_COLORS.get(c, COBALT) for c in causes]
    short  = [c.replace(" / ", "/\n")[:22] for c in causes]

    fig = go.Figure(go.Bar(
        x=values, y=short, orientation="h",
        marker=dict(color=colors, opacity=0.85,
                    line=dict(color="rgba(255,255,255,0.6)", width=0.5)),
        text=[f"{v*100:.1f}%" for v in values],
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))
    fig.update_layout(
        **_layout_base, height=280,
        xaxis=dict(range=[0, 1.2], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=10, color=TEXT_SUB)),
        title=dict(text="Cause Probability Distribution", font=dict(size=14, color=TEXT)),
        bargap=0.28,
    )
    return fig


def severity_timeline(history: List[Dict]) -> go.Figure:
    if not history:
        return go.Figure()
    df = pd.DataFrame([{
        "time": h["timestamp"],
        "severity": h["result"]["delay_severity"],
        "cause": h["result"]["delay_cause"],
    } for h in history])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["severity"],
        mode="lines+markers",
        line=dict(color=COBALT, width=2.5, shape="spline"),
        marker=dict(
            size=11,
            color=[CAUSE_COLORS.get(c, COBALT) for c in df["cause"]],
            line=dict(width=2, color="#FFFFFF"),
        ),
        hovertemplate="<b>%{x}</b><br>Severity: %{y:.2f}<extra></extra>",
    ))
    fig.add_hrect(y0=0,    y1=0.35, fillcolor="rgba(16,185,129,0.05)",  line_width=0)
    fig.add_hrect(y0=0.35, y1=0.65, fillcolor="rgba(245,158,11,0.05)",  line_width=0)
    fig.add_hrect(y0=0.65, y1=1.0,  fillcolor="rgba(244,63,94,0.05)",   line_width=0)
    fig.update_layout(
        **_layout_base, height=300,
        xaxis=dict(showgrid=False, tickfont=dict(color=TEXT_SUB, size=10)),
        yaxis=dict(range=[0, 1.05], showgrid=True,
                   gridcolor="rgba(209,213,219,0.5)", tickfont=dict(color=TEXT_SUB, size=10)),
        title=dict(text="Severity Over Time", font=dict(size=14, color=TEXT)),
        showlegend=False,
    )
    return fig


def cause_donut(history: List[Dict]) -> go.Figure:
    if not history:
        return go.Figure()
    from collections import Counter
    causes = [h["result"]["delay_cause"] for h in history]
    counts = Counter(causes)
    labels = list(counts.keys())
    values = list(counts.values())
    colors = [CAUSE_COLORS.get(l, COBALT) for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=3)),
        textfont=dict(color=TEXT_SUB, size=10),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_layout_base, height=280,
        showlegend=True,
        legend=dict(font=dict(size=9, color=TEXT_SUB), orientation="v", x=1.0),
        title=dict(text="Cause Distribution", font=dict(size=14, color=TEXT)),
        annotations=[dict(
            text=f"<b>{sum(values)}</b><br><span style='font-size:10px'>analyses</span>",
            x=0.5, y=0.5, font_size=18, showarrow=False, font_color=TEXT,
        )],
    )
    return fig


def habit_heatmap(habit_log: List[Dict]) -> go.Figure:
    if not habit_log:
        return go.Figure()
    df = pd.DataFrame(habit_log)
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.isocalendar().week
    df["day"]  = df["date"].dt.day_name()
    pivot = df.groupby(["day", "week"])["completed"].sum().unstack(fill_value=0)
    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex([d for d in days_order if d in pivot.index])

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"W{w}" for w in pivot.columns],
        y=list(pivot.index),
        colorscale=[[0, "#E5E7EB"], [0.5, "rgba(26,86,219,0.35)"], [1, COBALT]],
        showscale=False,
        hovertemplate="<b>%{y}</b> | %{x}<br>Completions: %{z}<extra></extra>",
    ))
    fig.update_layout(
        **_layout_base, height=220,
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color=TEXT_SUB)),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color=TEXT_SUB)),
        title=dict(text="Habit Activity Heatmap", font=dict(size=14, color=TEXT)),
    )
    return fig