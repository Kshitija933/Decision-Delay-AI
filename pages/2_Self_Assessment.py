"""
Page — Self Assessment
The core prediction + nudge interface.
"""
import streamlit as st
from inference.predict import run_prediction
from utils.session import save_result
from utils.visualizer import gauge_chart, radar_chart, probability_bar_chart
from configs.settings import APP_CFG

st.markdown("""
<div style="margin-bottom:1.5rem;">
<div style="margin-bottom:1.5rem;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
    <span style="font-size:1.6rem;">🎯</span>
    <h2 style="margin:0;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.9rem;
               font-weight:800;color:#0F172A;letter-spacing:-0.02em;">Self Assessment</h2>
  </div>
  <div style="height:3px;width:60px;background:linear-gradient(90deg,#1A56DB,#7C3AED);
              border-radius:2px;margin-bottom:0.5rem;"></div>
  <p style="color:#475569;font-size:0.96rem;margin:0;font-weight:500;">Diagnose your delay pattern — get a personalized behavioral nudge</p>
</div>
</div>
""", unsafe_allow_html=True)

col_form, col_result = st.columns([2, 3], gap="large")

with col_form:
    st.markdown("#### ⚙️ Your Situation")

    use_case = st.selectbox(
        "What area are you working on?",
        APP_CFG.use_cases,
        help="Select the domain you want to assess",
    )

    st.markdown("---")
    st.markdown("**Core Inputs**")

    task_difficulty = st.slider(
        "Task Difficulty", 0.0, 10.0, 5.0, 0.5,
        help="How hard does this task feel to you personally?"
    )
    time_to_reward = st.slider(
        "Time-to-Reward", 0.0, 10.0, 5.0, 0.5,
        help="How delayed is the payoff? (0=immediate, 10=very distant)"
    )
    past_failure_loops = st.slider(
        "Past Failure Loops", 0, 10, 2, 1,
        help="How many times have you started and stopped this before?"
    )

    # ── FIX: set defaults BEFORE the expander, then override inside it ──
    self_efficacy        = 5.0
    stress_level         = 5.0
    goal_clarity         = 5.0
    social_support       = 5.0
    intrinsic_motivation = 5.0
    habit_strength       = 3.0
    distraction_level    = 5.0

    with st.expander("🔬 Extended Profile (improves accuracy)"):
        self_efficacy = st.slider("Self-Efficacy", 0.0, 10.0, 5.0, 0.5,
                                   help="How confident are you that you can succeed?")
        stress_level = st.slider("Stress Level", 0.0, 10.0, 5.0, 0.5,
                                  help="How stressed are you currently?")
        goal_clarity = st.slider("Goal Clarity", 0.0, 10.0, 5.0, 0.5,
                                  help="How clear is your goal or end state?")
        social_support = st.slider("Social Support", 0.0, 10.0, 5.0, 0.5,
                                    help="How supported do you feel by others?")
        intrinsic_motivation = st.slider("Intrinsic Motivation", 0.0, 10.0, 5.0, 0.5,
                                          help="Do you WANT to do this, or feel you HAVE to?")
        habit_strength = st.slider("Habit Strength", 0.0, 10.0, 3.0, 0.5,
                                    help="How established is this behavior in your routine?")
        distraction_level = st.slider("Distraction Level", 0.0, 10.0, 5.0, 0.5,
                                       help="How much are you pulled away by distractions?")

    analyze_clicked = st.button("🔍 Analyze My Delay Pattern", use_container_width=True, type="primary")

with col_result:
    if analyze_clicked:
        inputs = {
            "use_case": use_case,
            "task_difficulty": task_difficulty,
            "time_to_reward": time_to_reward,
            "past_failure_loops": past_failure_loops,
            "self_efficacy": self_efficacy,
            "stress_level": stress_level,
            "goal_clarity": goal_clarity,
            "social_support": social_support,
            "intrinsic_motivation": intrinsic_motivation,
            "habit_strength": habit_strength,
            "distraction_level": distraction_level,
        }

        with st.spinner("Analyzing behavioral pattern..."):
            result = run_prediction(inputs)

        save_result(result, inputs)

        cause     = result["delay_cause"]
        severity  = result["delay_severity"]
        conf      = result["confidence"]
        probs     = result["class_probabilities"]
        nudge     = result["nudge"]
        alt_n     = result.get("alt_nudges", [])
        icon      = APP_CFG.cause_icons.get(cause, "🧠")
        color     = APP_CFG.cause_colors.get(cause, "#1A56DB")
        sev_level = nudge["severity_level"]
        sev_color = {"low": "#1A56DB", "medium": "#FFB703", "high": "#FF4D6D"}.get(sev_level, "#1A56DB")

        # ── Diagnosis card ──
        st.markdown(f"""
        <div class="da-card" style="border-left:4px solid {color};margin-bottom:1rem;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="font-size:0.7rem;color:#475569;font-weight:700;letter-spacing:0.1em;">PRIMARY DELAY CAUSE</div>
              <div style="display:flex;align-items:center;gap:0.75rem;margin-top:0.4rem;">
                <span style="font-size:2rem;">{icon}</span>
                <div>
                  <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">{cause}</div>
                  <div style="font-size:0.78rem;color:{color};">Confidence: {conf*100:.1f}%</div>
                </div>
              </div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:0.7rem;color:#475569;font-weight:700;">SEVERITY</div>
              <div style="font-size:1.6rem;font-weight:800;color:{sev_color};">{severity*100:.0f}%</div>
              <div style="font-size:0.7rem;color:{sev_color};font-weight:700;">{sev_level.upper()}</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.75rem;">
            <span class="stat-pill">Domain: {use_case}</span>
            <span class="stat-pill">Model: {result.get('model_used','rule_based').replace('_',' ').title()}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Charts row ──
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(gauge_chart(severity), use_container_width=True, config={"displayModeBar": False})
        with ch2:
            st.plotly_chart(probability_bar_chart(probs), use_container_width=True, config={"displayModeBar": False})

        st.plotly_chart(radar_chart(inputs), use_container_width=True, config={"displayModeBar": False})

        # ── Primary nudge ──
        st.markdown(f"""
        <div style="font-size:0.7rem;color:#475569;font-weight:700;letter-spacing:0.1em;margin-bottom:0.5rem;">
          🎯 BEHAVIORAL NUDGE — STRATEGY: {nudge['strategy'].upper()}
        </div>
        <div class="nudge-box">
          <div class="nudge-prefix">{nudge['prefix']}</div>
          <div class="nudge-text">{nudge['action']}</div>
          <div class="nudge-strategy">→ {nudge['strategy']}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Alt nudges ──
        if alt_n:
            with st.expander(f"💡 More nudges ({len(alt_n)} alternatives)"):
                for i, an in enumerate(alt_n, 1):
                    st.markdown(f"""
                    <div class="nudge-box" style="margin-bottom:0.5rem;">
                      <div class="nudge-prefix">Option {i} · {an['strategy']}</div>
                      <div class="nudge-text">{an['action']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:400px;text-align:center;color:#475569;">
          <div style="font-size:4rem;margin-bottom:1rem;">🧠</div>
          <div style="font-size:1.1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">
            Ready to Analyze
          </div>
          <div style="font-size:0.85rem;max-width:300px;line-height:1.6;">
            Adjust the sliders on the left to describe your situation,
            then click <strong style="color:#1A56DB;">Analyze My Delay Pattern</strong>.
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.history:
            st.markdown("---")
            last = st.session_state.history[-1]
            cause = last["result"]["delay_cause"]
            icon = APP_CFG.cause_icons.get(cause, "🧠")
            st.markdown(f"""
            <div class="da-card" style="text-align:center;">
              <div style="font-size:0.7rem;color:#475569;font-weight:700;margin-bottom:0.5rem;">LAST ANALYSIS</div>
              <div style="font-size:1.5rem;">{icon}</div>
              <div style="font-weight:700;">{cause}</div>
              <div style="color:#475569;font-size:0.78rem;">Severity: {last['result']['delay_severity']*100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)