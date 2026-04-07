"""
Page 4 — Compare Tasks
Side-by-side comparison of two tasks / decisions.
"""
import streamlit as st
import plotly.graph_objects as go
from inference.predict import run_prediction
from configs.settings import APP_CFG

# ── Light-mode colour palette ──
COBALT = "#1A56DB"
ROSE   = "#F43F5E"
VIOLET = "#7C3AED"
AMBER  = "#F59E0B"
MINT   = "#10B981"
TEXT   = "#0F172A"
MUTED  = "#475569"
GRID   = "rgba(26,86,219,0.06)"

# Pastel panel backgrounds for Task A / Task B
PASTEL_A = "#EFF6FF"   # soft sky blue
PASTEL_B = "#FFF1F2"   # soft rose blush

_layout = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans,sans-serif", color=TEXT, size=12),
    margin=dict(l=20, r=20, t=35, b=20),
)

st.markdown("""
<style>
/* Task panel pastel containers */
.task-panel-a {
  background: #EFF6FF;
  border: 2px solid rgba(26,86,219,0.25);
  border-top: 4px solid #1A56DB;
  border-radius: 14px;
  padding: 1.2rem 1.3rem 1.3rem;
  margin-bottom: 0.5rem;
}
.task-panel-b {
  background: #FFF1F2;
  border: 2px solid rgba(244,63,94,0.22);
  border-top: 4px solid #F43F5E;
  border-radius: 14px;
  padding: 1.2rem 1.3rem 1.3rem;
  margin-bottom: 0.5rem;
}
.task-label-a {
  font-weight: 800;
  font-size: 0.9rem;
  color: #1A56DB !important;
  margin-bottom: 0.75rem;
  letter-spacing: 0.02em;
  display: block;
}
.task-label-b {
  font-weight: 800;
  font-size: 0.9rem;
  color: #F43F5E !important;
  margin-bottom: 0.75rem;
  letter-spacing: 0.02em;
  display: block;
}
/* Make all labels dark inside panels */
.task-panel-a label,
.task-panel-b label,
.task-panel-a .stSelectbox label,
.task-panel-b .stSelectbox label {
  color: #0F172A !important;
  font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
    <span style="font-size:1.6rem;">⚖️</span>
    <h2 style="margin:0;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.9rem;
               font-weight:800;color:#0F172A;letter-spacing:-0.02em;">Compare Tasks</h2>
  </div>
  <div style="height:3px;width:60px;background:linear-gradient(90deg,#1A56DB,#7C3AED);
              border-radius:2px;margin-bottom:0.5rem;"></div>
  <p style="color:#475569;font-size:0.96rem;margin:0;font-weight:500;">Analyze two tasks side-by-side to see which has a higher delay risk</p>
</div>
""", unsafe_allow_html=True)


def task_input_panel(label: str, panel_class: str, label_class: str, key_prefix: str):
    st.markdown(f'<div class="{panel_class}"><span class="{label_class}">{label}</span></div>',
                unsafe_allow_html=True)

    name = st.text_input("Task name", placeholder="e.g. Apply for the new role",
                         key=f"{key_prefix}_name")
    use_case = st.selectbox("Domain", APP_CFG.use_cases, key=f"{key_prefix}_uc")
    td  = st.slider("Task Difficulty",  0.0, 10.0, 5.0, 0.5, key=f"{key_prefix}_td")
    tr  = st.slider("Time-to-Reward",   0.0, 10.0, 5.0, 0.5, key=f"{key_prefix}_tr")
    pfl = st.slider("Past Failures",    0,   10,   2,   1,   key=f"{key_prefix}_pfl")
    se  = st.slider("Self-Efficacy",    0.0, 10.0, 5.0, 0.5, key=f"{key_prefix}_se")
    sl  = st.slider("Stress Level",     0.0, 10.0, 5.0, 0.5, key=f"{key_prefix}_sl")

    return {
        "name": name or label,
        "use_case": use_case,
        "task_difficulty": td,
        "time_to_reward": tr,
        "past_failure_loops": pfl,
        "self_efficacy": se,
        "stress_level": sl,
        "goal_clarity": 5.0, "social_support": 5.0,
        "intrinsic_motivation": 5.0, "habit_strength": 3.0, "distraction_level": 5.0,
    }


col_a, col_mid, col_b = st.columns([5, 1, 5], gap="small")

with col_a:
    task_a = task_input_panel("🔵 Task A", "task-panel-a", "task-label-a", "a")

with col_mid:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;height:100%;
                min-height:200px;font-size:1.5rem;font-weight:800;color:#334155;">vs</div>
    """, unsafe_allow_html=True)

with col_b:
    task_b = task_input_panel("🔴 Task B", "task-panel-b", "task-label-b", "b")

st.markdown("<br>", unsafe_allow_html=True)
run = st.button("⚖️ Compare Now", use_container_width=True, type="primary")

if run:
    with st.spinner("Analyzing both tasks..."):
        result_a = run_prediction(task_a)
        result_b = run_prediction(task_b)

    sa = result_a["delay_severity"]
    sb = result_b["delay_severity"]

    # ── Winner banner ──
    if sa < sb:
        winner_color = COBALT
        winner_msg   = f"<b>{task_a['name']}</b> has lower delay risk — tackle it first."
    elif sb < sa:
        winner_color = ROSE
        winner_msg   = f"<b>{task_b['name']}</b> has lower delay risk — tackle it first."
    else:
        winner_color = AMBER
        winner_msg   = "Both tasks have equal delay risk."

    st.markdown(f"""
    <div class="da-card" style="border-left:4px solid {winner_color};text-align:center;padding:1.25rem;">
      <div style="font-size:0.72rem;color:#475569;font-weight:700;margin-bottom:0.3rem;letter-spacing:0.1em;">RECOMMENDATION</div>
      <div style="font-size:1.1rem;color:#0F172A;font-weight:600;">{winner_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Side-by-side result cards ──
    res_a_col, res_b_col = st.columns(2, gap="medium")

    for col, result, task, color, pastel, label in [
        (res_a_col, result_a, task_a, COBALT, "#EFF6FF", "Task A"),
        (res_b_col, result_b, task_b, ROSE,   "#FFF1F2", "Task B"),
    ]:
        with col:
            cause    = result["delay_cause"]
            sev      = result["delay_severity"]
            conf     = result["confidence"]
            nudge    = result["nudge"]
            icon     = APP_CFG.cause_icons.get(cause, "🧠")
            sev_color = MINT if sev < 0.35 else AMBER if sev < 0.65 else ROSE

            st.markdown(f"""
            <div style="background:{pastel};border:1.5px solid {color}33;border-left:4px solid {color};
                        border-radius:14px;padding:1.1rem 1.3rem;margin-bottom:0.5rem;
                        box-shadow:0 2px 12px rgba(15,23,42,0.06);">
              <div style="font-size:0.72rem;font-weight:800;color:{color};
                          letter-spacing:0.08em;margin-bottom:0.5rem;">{label}: {task['name']}</div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin:0.4rem 0;">
                <div style="font-size:1.8rem;">{icon}</div>
                <div style="text-align:right;">
                  <div style="font-size:2rem;font-weight:900;color:{sev_color};line-height:1;">{sev*100:.0f}%</div>
                  <div style="font-size:0.72rem;color:#475569;font-weight:600;">Severity</div>
                </div>
              </div>
              <div style="font-weight:700;font-size:0.92rem;color:#0F172A;margin-bottom:0.2rem;">{cause}</div>
              <div style="color:#475569;font-size:0.8rem;font-weight:500;">Confidence: {conf*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="nudge-box">
              <div class="nudge-prefix">{nudge['strategy']}</div>
              <div class="nudge-text" style="font-size:0.9rem;">{nudge['action']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Comparison radar ──
    st.markdown("---")
    st.markdown("#### 📡 Profile Comparison")

    features       = ["task_difficulty","time_to_reward","past_failure_loops","self_efficacy","stress_level"]
    labels_display = ["Difficulty","Reward Delay","Past Failures","Self-Efficacy","Stress"]
    va = [task_a.get(f,5)/10 for f in features] + [task_a.get(features[0],5)/10]
    vb = [task_b.get(f,5)/10 for f in features] + [task_b.get(features[0],5)/10]
    cats = labels_display + [labels_display[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=va, theta=cats, name=task_a["name"], fill="toself",
        fillcolor="rgba(26,86,219,0.10)", line=dict(color=COBALT, width=2.5),
    ))
    fig.add_trace(go.Scatterpolar(
        r=vb, theta=cats, name=task_b["name"], fill="toself",
        fillcolor="rgba(244,63,94,0.10)", line=dict(color=ROSE, width=2.5),
    ))
    fig.update_layout(
        **_layout, height=360,
        polar=dict(
            bgcolor="#F8FAFC",
            radialaxis=dict(visible=True, range=[0,1],
                            tickfont=dict(size=9, color=MUTED),
                            gridcolor="rgba(26,86,219,0.10)"),
            angularaxis=dict(tickfont=dict(color=TEXT, size=10)),
        ),
        legend=dict(font=dict(size=11, color=TEXT)),
        title=dict(text="Task Profile Overlay", font=dict(size=14, color=TEXT)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Probability comparison bar ──
    st.markdown("#### 📊 Delay Cause Probabilities")
    causes = APP_CFG.delay_causes
    pa = [result_a["class_probabilities"].get(c, 0) for c in causes]
    pb = [result_b["class_probabilities"].get(c, 0) for c in causes]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=causes, x=pa, name=task_a["name"], orientation="h",
        marker=dict(color=COBALT, opacity=0.85),
    ))
    fig2.add_trace(go.Bar(
        y=causes, x=pb, name=task_b["name"], orientation="h",
        marker=dict(color=ROSE, opacity=0.85),
    ))
    fig2.update_layout(
        **_layout, height=290, barmode="group",
        xaxis=dict(range=[0,0.65], showgrid=False, showticklabels=False,
                   tickfont=dict(color=MUTED)),
        yaxis=dict(showgrid=False, tickfont=dict(size=10, color=TEXT)),
        legend=dict(font=dict(size=11, color=TEXT), orientation="h", y=1.1),
        title=dict(text="Cause Distribution Comparison", font=dict(size=14, color=TEXT)),
        bargap=0.2, bargroupgap=0.05,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})