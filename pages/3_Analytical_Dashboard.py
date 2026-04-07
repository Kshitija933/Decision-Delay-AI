"""
Page 4 — Analytical Dashboard
Post-analysis charts: visualizes scores and patterns
from Self Assessment history stored in session state.
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import os
from configs.settings import APP_CFG

# ── Palette ──
COBALT="#1A56DB"; ROSE="#F43F5E"; VIOLET="#7C3AED"
AMBER="#F59E0B";  MINT="#10B981";  SKY="#0EA5E9"
TEXT="#0F172A";   MUTED="#475569"; GRID="rgba(26,86,219,0.07)"
CAUSE_COLORS = {
    "Fear of Failure": ROSE,
    "Overwhelm / Complexity": AMBER,
    "Lack of Immediate Reward": COBALT,
    "Past Failure Loop": VIOLET,
    "Perfectionism": "#FB8500",
    "Decision Fatigue": SKY,
}
_L = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans,sans-serif", color=TEXT, size=12),
    margin=dict(l=20, r=20, t=44, b=20),
)

CAUSES  = APP_CFG.delay_causes
DOMAINS = APP_CFG.use_cases

# ── Page title ──
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
    <span style="font-size:1.6rem;">📈</span>
    <h2 style="margin:0;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.9rem;
               font-weight:800;color:#0F172A;letter-spacing:-0.02em;">Analytical Dashboard</h2>
  </div>
  <div style="height:3px;width:60px;background:linear-gradient(90deg,#1A56DB,#7C3AED);
              border-radius:2px;margin-bottom:0.5rem;"></div>
  <p style="color:#475569;font-size:0.96rem;margin:0;font-weight:500;">
    Charts and patterns from your Self Assessment analyses
  </p>
</div>
""", unsafe_allow_html=True)

# ── Pull history from session ──
history = st.session_state.get("history", [])

# ─────────────────────────────────────────────────────────────
# NO HISTORY STATE
# ─────────────────────────────────────────────────────────────
if not history:
    st.markdown("""
    <div class="da-card" style="text-align:center;padding:3rem 2rem;">
      <div style="font-size:3.5rem;margin-bottom:1rem;">📊</div>
      <div style="font-size:1.2rem;font-weight:800;color:#0F172A;margin-bottom:0.5rem;">
        No Analyses Yet
      </div>
      <div style="color:#475569;font-size:0.95rem;margin-bottom:1.5rem;line-height:1.7;">
        Run a <strong>Self Assessment</strong> first — your results will appear
        here as interactive charts and patterns.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Show demo charts with synthetic data
    st.markdown("""
    <div style="font-size:0.72rem;font-weight:800;color:#475569;letter-spacing:0.14em;
                text-transform:uppercase;margin:1.5rem 0 0.75rem;">
      Preview — Demo Data (run an assessment to see your real scores)
    </div>
    """, unsafe_allow_html=True)

    # Generate demo history
    rng = np.random.default_rng(42)
    demo = []
    for i in range(12):
        cause = rng.choice(CAUSES)
        sev   = float(np.clip(rng.normal(0.52, 0.18), 0.05, 0.95))
        domain= rng.choice(DOMAINS)
        demo.append({
            "timestamp": f"2026-04-0{(i%9)+1} {9+i%12:02d}:00",
            "result": {
                "delay_cause": cause,
                "delay_severity": round(sev, 4),
                "confidence": round(float(rng.uniform(0.55, 0.92)), 3),
                "class_probabilities": {c: round(float(rng.dirichlet(np.ones(6))[j]),3)
                                        for j, c in enumerate(CAUSES)},
            },
            "inputs": {
                "task_difficulty": round(float(rng.uniform(3,9)), 1),
                "time_to_reward":  round(float(rng.uniform(2,9)), 1),
                "past_failure_loops": int(rng.integers(0,6)),
                "self_efficacy":   round(float(rng.uniform(2,8)), 1),
                "stress_level":    round(float(rng.uniform(3,9)), 1),
                "use_case": domain,
            },
        })
    history = demo
    is_demo = True
else:
    is_demo = False

# ─────────────────────────────────────────────────────────────
# BUILD DATAFRAME FROM HISTORY
# ─────────────────────────────────────────────────────────────
rows = []
for h in history:
    r = h["result"]
    inp = h.get("inputs", {})
    rows.append({
        "timestamp":    h.get("timestamp", ""),
        "cause":        r.get("delay_cause", ""),
        "severity":     r.get("delay_severity", 0),
        "confidence":   r.get("confidence", 0),
        "domain":       inp.get("use_case", ""),
        "task_diff":    inp.get("task_difficulty", 5),
        "time_reward":  inp.get("time_to_reward", 5),
        "failures":     inp.get("past_failure_loops", 2),
        "self_eff":     inp.get("self_efficacy", 5),
        "stress":       inp.get("stress_level", 5),
    })

df = pd.DataFrame(rows)
n_analyses = len(df)

# ─────────────────────────────────────────────────────────────
# ROW 0 — KPI CARDS
# ─────────────────────────────────────────────────────────────
if is_demo:
    st.markdown('<div style="background:#FEF9C3;border:1px solid #FDE047;border-radius:10px;'
                'padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.85rem;color:#713F12;">'
                '⚠️ Showing <strong>demo data</strong>. Run Self Assessment to see your real results.'
                '</div>', unsafe_allow_html=True)

top_cause   = df["cause"].value_counts().idxmax()
avg_sev     = df["severity"].mean()
avg_conf    = df["confidence"].mean()
sev_color   = MINT if avg_sev < 0.35 else AMBER if avg_sev < 0.65 else ROSE
trend = "↓ Improving" if len(df) > 3 and df["severity"].iloc[-3:].mean() < df["severity"].iloc[:3].mean() else "→ Stable"

k1,k2,k3,k4,k5 = st.columns(5)
for col, label, val, color in [
    (k1, "Total Analyses", str(n_analyses), COBALT),
    (k2, "Top Delay Cause", top_cause[:16], ROSE),
    (k3, "Avg Severity",    f"{avg_sev*100:.0f}%", sev_color),
    (k4, "Avg Confidence",  f"{avg_conf*100:.0f}%", VIOLET),
    (k5, "Severity Trend",  trend, MINT if "↓" in trend else AMBER),
]:
    with col:
        st.markdown(f"""
        <div class="da-card" style="text-align:center;padding:0.9rem 0.5rem;">
          <div style="font-size:0.65rem;color:#475569;font-weight:800;
                      letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.4rem;">{label}</div>
          <div style="font-size:1.3rem;font-weight:900;color:{color};line-height:1.15;">{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr style="border-color:rgba(26,86,219,0.10);margin:0.5rem 0 1rem;">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ROW 1 — Severity Timeline + Cause Frequency Bar
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:0.72rem;font-weight:800;color:#475569;letter-spacing:0.14em;'
            'text-transform:uppercase;margin-bottom:0.6rem;">Your Assessment Results</div>',
            unsafe_allow_html=True)

r1a, r1b = st.columns([3, 2], gap="medium")

with r1a:
    fig1 = go.Figure()
    # Severity area
    fig1.add_trace(go.Scatter(
        x=list(range(1, n_analyses+1)),
        y=df["severity"].values,
        mode="lines+markers",
        name="Severity",
        line=dict(color=COBALT, width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(26,86,219,0.07)",
        marker=dict(
            size=9,
            color=[CAUSE_COLORS.get(c, COBALT) for c in df["cause"]],
            line=dict(width=1.5, color="white"),
        ),
        hovertemplate="<b>Analysis #%{x}</b><br>Severity: %{y:.3f}<br><extra></extra>",
    ))
    # Confidence line
    fig1.add_trace(go.Scatter(
        x=list(range(1, n_analyses+1)),
        y=df["confidence"].values,
        mode="lines",
        name="Confidence",
        line=dict(color=VIOLET, width=1.5, dash="dot"),
        hovertemplate="<b>Analysis #%{x}</b><br>Confidence: %{y:.3f}<extra></extra>",
    ))
    fig1.add_hrect(y0=0,    y1=0.35, fillcolor="rgba(16,185,129,0.05)", line_width=0)
    fig1.add_hrect(y0=0.35, y1=0.65, fillcolor="rgba(245,158,11,0.05)", line_width=0)
    fig1.add_hrect(y0=0.65, y1=1.0,  fillcolor="rgba(244,63,94,0.05)",  line_width=0)
    fig1.update_layout(**_L, height=310,
        title=dict(text="Severity & Confidence Over Time", font=dict(size=14, color=TEXT)),
        xaxis=dict(title="Analysis #", showgrid=False,
                   tickfont=dict(size=10, color=MUTED)),
        yaxis=dict(range=[0,1.05], showgrid=True, gridcolor=GRID,
                   tickfont=dict(size=10, color=MUTED)),
        legend=dict(font=dict(size=10, color=TEXT), orientation="h", y=1.12),
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

with r1b:
    cause_counts = df["cause"].value_counts().reindex(CAUSES, fill_value=0)
    cause_counts = cause_counts[cause_counts > 0]
    fig2 = go.Figure(go.Bar(
        y=cause_counts.index,
        x=cause_counts.values,
        orientation="h",
        marker=dict(
            color=[CAUSE_COLORS.get(c, COBALT) for c in cause_counts.index],
            opacity=0.9,
            line=dict(color="white", width=0.5),
        ),
        text=[str(v) for v in cause_counts.values],
        textposition="outside",
        textfont=dict(color=TEXT, size=12),
    ))
    fig2.update_layout(**_L, height=310,
        title=dict(text="Your Delay Causes Frequency", font=dict(size=14, color=TEXT)),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color=TEXT)),
        bargap=0.3,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────────────────────
# ROW 2 — Severity Gauge + Domain Donut
# ─────────────────────────────────────────────────────────────
st.markdown('<hr style="border-color:rgba(26,86,219,0.10);margin:0.5rem 0 1rem;">', unsafe_allow_html=True)
st.markdown('<div style="font-size:0.72rem;font-weight:800;color:#475569;letter-spacing:0.14em;'
            'text-transform:uppercase;margin-bottom:0.6rem;">Score Breakdown</div>',
            unsafe_allow_html=True)

r2a, r2b, r2c = st.columns(3, gap="medium")

with r2a:
    # Gauge for average severity
    sev_val = avg_sev * 100
    gauge_color = MINT if avg_sev < 0.35 else AMBER if avg_sev < 0.65 else ROSE
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(sev_val, 1),
        delta={"reference": 50, "valueformat": ".1f"},
        title={"text": "Avg Delay Severity", "font": {"size": 13, "color": TEXT}},
        number={"suffix": "%", "font": {"size": 30, "color": gauge_color}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": MUTED, "size": 9}},
            "bar": {"color": gauge_color, "thickness": 0.28},
            "bgcolor": "#F1F5F9",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  35],  "color": "rgba(16,185,129,0.10)"},
                {"range": [35, 65],  "color": "rgba(245,158,11,0.10)"},
                {"range": [65, 100], "color": "rgba(244,63,94,0.10)"},
            ],
        },
    ))
    fig3.update_layout(**_L, height=260)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with r2b:
    # Confidence gauge
    conf_val = avg_conf * 100
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(conf_val, 1),
        title={"text": "Avg Model Confidence", "font": {"size": 13, "color": TEXT}},
        number={"suffix": "%", "font": {"size": 30, "color": COBALT}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": MUTED, "size": 9}},
            "bar": {"color": COBALT, "thickness": 0.28},
            "bgcolor": "#F1F5F9",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60],  "color": "rgba(244,63,94,0.08)"},
                {"range": [60, 80], "color": "rgba(245,158,11,0.08)"},
                {"range": [80, 100],"color": "rgba(26,86,219,0.08)"},
            ],
        },
    ))
    fig4.update_layout(**_L, height=260)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

with r2c:
    # Domain donut
    if df["domain"].notna().any() and df["domain"].str.len().gt(0).any():
        dom_counts = df["domain"].value_counts()
    else:
        dom_counts = pd.Series({d: 0 for d in DOMAINS})
        dom_counts[DOMAINS[0]] = n_analyses
    fig5 = go.Figure(go.Pie(
        labels=dom_counts.index, values=dom_counts.values,
        hole=0.60,
        marker=dict(colors=[COBALT, VIOLET, ROSE],
                    line=dict(color="white", width=3)),
        textfont=dict(size=10, color=TEXT),
        hovertemplate="<b>%{label}</b><br>%{value} analyses (%{percent})<extra></extra>",
    ))
    fig5.update_layout(**_L, height=260,
        title=dict(text="Domain Breakdown", font=dict(size=13, color=TEXT)),
        showlegend=True,
        legend=dict(font=dict(size=9, color=TEXT), orientation="v"),
        annotations=[dict(text=f"<b>{n_analyses}</b><br><span style='font-size:9px'>total</span>",
                          x=0.5, y=0.5, font_size=16, showarrow=False, font_color=TEXT)],
    )
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────────────────────
# ROW 3 — Input Score Radar (your avg inputs)
# ─────────────────────────────────────────────────────────────
st.markdown('<hr style="border-color:rgba(26,86,219,0.10);margin:0.5rem 0 1rem;">', unsafe_allow_html=True)
st.markdown('<div style="font-size:0.72rem;font-weight:800;color:#475569;letter-spacing:0.14em;'
            'text-transform:uppercase;margin-bottom:0.6rem;">Your Input Profile</div>',
            unsafe_allow_html=True)

r3a, r3b = st.columns([2, 3], gap="medium")

with r3a:
    radar_labels = ["Task Diff", "Time→Reward", "Past Fails", "Self-Efficacy", "Stress"]
    radar_cols   = ["task_diff","time_reward","failures","self_eff","stress"]
    user_vals    = [df[c].mean()/10 for c in radar_cols]
    user_vals   += user_vals[:1]
    cats         = radar_labels + [radar_labels[0]]

    fig6 = go.Figure()
    fig6.add_trace(go.Scatterpolar(
        r=user_vals, theta=cats, name="Your Avg",
        fill="toself",
        fillcolor="rgba(26,86,219,0.12)",
        line=dict(color=COBALT, width=2.5),
    ))
    # Healthy baseline
    baseline = [0.4, 0.3, 0.2, 0.7, 0.4, 0.4]
    fig6.add_trace(go.Scatterpolar(
        r=baseline, theta=cats, name="Healthy Baseline",
        fill="toself",
        fillcolor="rgba(16,185,129,0.08)",
        line=dict(color=MINT, width=1.5, dash="dot"),
    ))
    fig6.update_layout(**_L, height=320,
        title=dict(text="Your Avg Input vs Healthy Baseline", font=dict(size=13, color=TEXT)),
        polar=dict(
            bgcolor="#F8FAFC",
            radialaxis=dict(visible=True, range=[0,1],
                            tickfont=dict(size=8, color=MUTED),
                            gridcolor="rgba(26,86,219,0.08)"),
            angularaxis=dict(tickfont=dict(color=TEXT, size=9)),
        ),
        legend=dict(font=dict(size=9, color=TEXT), x=0.75, y=1.1),
    )
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

with r3b:
    # Bar chart of avg input scores per analysis dimension
    input_labels = ["Task Difficulty","Time to Reward","Past Failures","Self-Efficacy","Stress Level"]
    input_cols   = ["task_diff","time_reward","failures","self_eff","stress"]
    avgs  = [df[c].mean() for c in input_cols]
    stdvs = [df[c].std() for c in input_cols]
    bar_c = [ROSE if (l in ["Task Difficulty","Past Failures","Stress Level"] and v > 6)
             else MINT if v < 4 else COBALT
             for l, v in zip(input_labels, avgs)]

    fig7 = go.Figure(go.Bar(
        x=input_labels, y=avgs,
        error_y=dict(type="data", array=stdvs, color=MUTED, thickness=1.5, width=5),
        marker=dict(color=bar_c, opacity=0.88, line=dict(color="white", width=0.5)),
        text=[f"{v:.1f}" for v in avgs],
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))
    fig7.add_hline(y=5, line=dict(color=MUTED, width=1, dash="dot"),
                   annotation_text="Midpoint (5)", annotation_font=dict(color=MUTED, size=9))
    fig7.update_layout(**_L, height=320,
        title=dict(text="Your Average Input Scores (0–10 scale)", font=dict(size=13, color=TEXT)),
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color=TEXT), tickangle=-10),
        yaxis=dict(range=[0, 12], showgrid=True, gridcolor=GRID,
                   tickfont=dict(size=10, color=MUTED)),
        bargap=0.3,
    )
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────────────────────
# ROW 4 — Probability Heatmap (last analysis)
# ─────────────────────────────────────────────────────────────
st.markdown('<hr style="border-color:rgba(26,86,219,0.10);margin:0.5rem 0 1rem;">', unsafe_allow_html=True)
st.markdown('<div style="font-size:0.72rem;font-weight:800;color:#475569;letter-spacing:0.14em;'
            'text-transform:uppercase;margin-bottom:0.6rem;">Cause Probability — All Analyses</div>',
            unsafe_allow_html=True)

prob_rows = []
for h in history:
    probs = h["result"].get("class_probabilities", {})
    if probs:
        prob_rows.append({c: probs.get(c, 0) for c in CAUSES})

if prob_rows:
    prob_df = pd.DataFrame(prob_rows)
    fig8 = go.Figure(go.Heatmap(
        z=prob_df.values,
        x=[c.replace(" / ","/") for c in prob_df.columns],
        y=[f"#{i+1}" for i in range(len(prob_df))],
        colorscale=[[0,"#EFF6FF"],[0.5,"#BFDBFE"],[1,COBALT]],
        text=np.round(prob_df.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=9, color=TEXT),
        showscale=True,
        colorbar=dict(thickness=10, len=0.85,
                      title=dict(text="Prob", font=dict(size=10, color=TEXT)),
                      tickfont=dict(size=9, color=TEXT)),
        hovertemplate="Analysis %{y}<br><b>%{x}</b><br>Probability: %{z:.3f}<extra></extra>",
    ))
    fig8.update_layout(**_L, height=max(280, 40*len(prob_df)+80),
        title=dict(text="Delay Cause Probability per Analysis", font=dict(size=14, color=TEXT)),
        xaxis=dict(tickfont=dict(size=9, color=TEXT), tickangle=-20, showgrid=False),
        yaxis=dict(tickfont=dict(size=10, color=TEXT), showgrid=False),
    )
    st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────────────────────
# ROW 5 — Severity Distribution Histogram + Box
# ─────────────────────────────────────────────────────────────
st.markdown('<hr style="border-color:rgba(26,86,219,0.10);margin:0.5rem 0 1rem;">', unsafe_allow_html=True)
st.markdown('<div style="font-size:0.72rem;font-weight:800;color:#475569;letter-spacing:0.14em;'
            'text-transform:uppercase;margin-bottom:0.6rem;">Severity Distribution</div>',
            unsafe_allow_html=True)

r5a, r5b = st.columns(2, gap="medium")

with r5a:
    sev_vals = df["severity"].values
    bins = np.linspace(0, 1, 16)
    counts_h, edges = np.histogram(sev_vals, bins=bins)
    mid = (edges[:-1] + edges[1:]) / 2
    bar_cols = [MINT if m < 0.35 else AMBER if m < 0.65 else ROSE for m in mid]
    fig9 = go.Figure(go.Bar(
        x=mid, y=counts_h,
        marker=dict(color=bar_cols, opacity=0.88, line=dict(color="white", width=0.5)),
        hovertemplate="Severity: %{x:.2f}<br>Count: %{y}<extra></extra>",
    ))
    fig9.add_vline(x=sev_vals.mean(), line=dict(color=COBALT, width=2, dash="dot"),
                   annotation_text=f"mean {sev_vals.mean():.2f}",
                   annotation_font=dict(color=COBALT, size=10))
    fig9.update_layout(**_L, height=270,
        title=dict(text="Your Severity Score Distribution", font=dict(size=13, color=TEXT)),
        xaxis=dict(title="Severity", showgrid=False,
                   tickfont=dict(size=10, color=MUTED)),
        yaxis=dict(showgrid=True, gridcolor=GRID,
                   tickfont=dict(size=10, color=MUTED)),
        bargap=0.08, showlegend=False,
    )
    st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})

with r5b:
    # Cause-colored scatter of all analyses
    fig10 = go.Figure()
    for cause in CAUSES:
        sub = df[df["cause"]==cause]
        if len(sub) == 0: continue
        fig10.add_trace(go.Scatter(
            x=list(sub.index + 1),
            y=sub["severity"].values,
            mode="markers",
            name=cause[:18],
            marker=dict(
                color=CAUSE_COLORS.get(cause, COBALT),
                size=10, opacity=0.85,
                line=dict(width=1.5, color="white"),
                symbol="circle",
            ),
            hovertemplate=f"<b>{cause}</b><br>Analysis #%{{x}}<br>Severity: %{{y:.3f}}<extra></extra>",
        ))
    fig10.update_layout(**_L, height=270,
        title=dict(text="Severity by Cause (per Analysis)", font=dict(size=13, color=TEXT)),
        xaxis=dict(title="Analysis #", showgrid=False,
                   tickfont=dict(size=10, color=MUTED)),
        yaxis=dict(range=[0, 1.05], showgrid=True, gridcolor=GRID,
                   title="Severity", tickfont=dict(size=10, color=MUTED)),
        legend=dict(font=dict(size=8, color=TEXT), x=1.01),
    )
    st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────────────────────
# RAW TABLE
# ─────────────────────────────────────────────────────────────
st.markdown('<hr style="border-color:rgba(26,86,219,0.10);margin:0.5rem 0 1rem;">', unsafe_allow_html=True)
with st.expander("📋 Full Analysis History Table"):
    display_df = df[["timestamp","cause","severity","confidence","domain",
                      "task_diff","time_reward","failures","self_eff","stress"]].copy()
    display_df.columns = ["Time","Cause","Severity","Confidence","Domain",
                          "Task Diff","Time→Reward","Failures","Self-Eff","Stress"]
    display_df["Severity"] = display_df["Severity"].apply(lambda x: f"{x*100:.1f}%")
    display_df["Confidence"] = display_df["Confidence"].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(display_df.iloc[::-1], use_container_width=True, hide_index=True)