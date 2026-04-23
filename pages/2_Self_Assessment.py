"""
Page — Self Assessment
The core prediction + nudge interface.
"""
import streamlit as st
from inference.predict import run_prediction
from utils.session import save_result
from utils.visualizer import (
    gauge_chart, radar_chart, probability_bar_chart,
    MINT, AMBER, CORAL
)
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
        # Synchronize sev_color with gauge thresholds
        sev_color = MINT if severity < 0.35 else AMBER if severity < 0.65 else CORAL
        m_type    = result.get("model_type", "Baseline")

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
              <div style="font-size:1.4rem;font-weight:800;color:{sev_color};">{severity*100:.1f}%</div>
              <div style="font-size:0.78rem;color:{CORAL if (severity*100-50) < 0 else MINT};font-weight:700;">
                {"▲" if (severity*100-50)>=0 else "▼"} {(severity*100-50):.1f}
              </div>
              <div style="font-size:0.7rem;color:{sev_color};font-weight:700;">{sev_level.upper()}</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.75rem;">
            <span class="stat-pill">Domain: {use_case}</span>
            <span class="stat-pill" style="color:{MINT if 'Active' in m_type else '#64748B'};">Engine: {m_type}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Charts row ──
        # Use a random UUID key to ensure 'active' refreshing and animation on every click
        import uuid
        chart_key = str(uuid.uuid4())
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(gauge_chart(severity), use_container_width=True, 
                            config={"displayModeBar": False}, key=f"gauge_{chart_key}")
        with ch2:
            st.plotly_chart(probability_bar_chart(probs), use_container_width=True, 
                            config={"displayModeBar": False}, key=f"probs_{chart_key}")

        st.plotly_chart(radar_chart(inputs), use_container_width=True, 
                        config={"displayModeBar": False}, key=f"radar_{chart_key}")

        # ── COMPREHENSIVE STRATEGIC PLAN ──
        st.markdown(f"""
        <div style="margin-top:2.5rem; margin-bottom:1.2rem;">
          <div style="font-size:0.75rem;color:#6EE7F7;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;">
            🚀 Your Strategic recovery Protocol
          </div>
          <div style="height:2px;width:50px;background:linear-gradient(90deg,#6EE7F7,#A78BFA);border-radius:1px;margin-top:0.4rem;"></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Primary nudge ──
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
          <div style="font-size:0.68rem;color:#94A3B8;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">
            🎯 Primary Behavioral Nudge
          </div>
          <div style="font-size:0.68rem;color:#6EE7F7;font-weight:800;letter-spacing:0.05em;text-transform:uppercase;">
            Strategy: {nudge['strategy']}
          </div>
        </div>
        <div class="nudge-box" style="border-left:4px solid #6EE7F7; background:rgba(110,231,247,0.08); margin-bottom:1.5rem;">
          <div class="nudge-text" style="font-size:1.18rem; color:#FFFFFF !important;">
            <strong>{nudge['action_plan']['micro_win']}</strong>
          </div>
          <div class="nudge-strategy" style="color:#6EE7F7; margin-top:0.6rem;">
            → {nudge['action_plan']['mindset_shift']}
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("💡 More nudges (3 alternatives)"):
            # Option 1: Micro-Win
            st.markdown(f"""
            <div class="alt-nudge-card">
              <div class="alt-card-header">Option 1 • Minimum Viable Action</div>
              <div class="alt-card-body">{nudge['action_plan']['micro_win']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Option 2: Recovery (cleaned)
            recovery_clean = nudge['recovery'].replace("🔥 ", "").split(": ")[-1]
            st.markdown(f"""
            <div class="alt-nudge-card">
              <div class="alt-card-header">Option 2 • Recovery Protocol</div>
              <div class="alt-card-body">{recovery_clean}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Option 3: Mindset Shift
            st.markdown(f"""
            <div class="alt-nudge-card">
              <div class="alt-card-header">Option 3 • Mindset Shift</div>
              <div class="alt-card-body">{nudge['action_plan']['mindset_shift']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top:1.5rem;margin-bottom:1rem;font-size:0.68rem;color:#94A3B8;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">⚒️ Strategic Action Plan</div>', unsafe_allow_html=True)
        
        # 2x2 Grid using columns
        g1, g2 = st.columns(2)
        
        with g1:
            # Micro-win
            st.markdown(f"""
            <div class="nudge-box" style="border-top:3px solid #34D399; background:rgba(52,211,153,0.04); min-height:110px;">
              <div style="font-size:0.65rem;color:#34D399;font-weight:800;margin-bottom:0.5rem;">⚡ MICRO-WIN (2 MIN)</div>
              <div style="font-size:0.94rem;color:#E2E8F0;line-height:1.45;"><strong>{nudge['action_plan']['micro_win']}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Environment Fix
            st.markdown(f"""
            <div class="nudge-box" style="border-top:3px solid #6EE7F7; background:rgba(110,231,247,0.04); min-height:110px;">
              <div style="font-size:0.65rem;color:#6EE7F7;font-weight:800;margin-bottom:0.5rem;">🗺️ ENVIRONMENT FIX</div>
              <div style="font-size:0.94rem;color:#E2E8F0;line-height:1.45;"><strong>{nudge['action_plan']['environment']}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        with g2:
            # Mindset Shift
            st.markdown(f"""
            <div class="nudge-box" style="border-top:3px solid #A78BFA; background:rgba(167,139,250,0.04); min-height:110px;">
              <div style="font-size:0.65rem;color:#A78BFA;font-weight:800;margin-bottom:0.5rem;">🧠 MINDSET SHIFT</div>
              <div style="font-size:0.94rem;color:#E2E8F0;line-height:1.45;"><strong>{nudge['action_plan']['mindset_shift']}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recommended Tool
            st.markdown(f"""
            <div class="nudge-box" style="border-top:3px solid #FB7185; background:rgba(251,113,133,0.04); min-height:110px;">
              <div style="font-size:0.65rem;color:#FB7185;font-weight:800;margin-bottom:0.5rem;">🛠️ RECOMMENDED TOOL</div>
              <div style="font-size:0.94rem;color:#E2E8F0;line-height:1.45;"><strong>{nudge['action_plan']['tool']}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        # ── Recovery Protocol ──
        st.markdown(f"""
        <div style="margin-top:1rem; margin-bottom:0.8rem; font-size:0.68rem; color:#FB7185; font-weight:800; letter-spacing:0.12em; text-transform:uppercase;">
          🧨 Recovery Protocol (Immediate)
        </div>
        <div class="nudge-box" style="border: 2px solid rgba(251,113,133,0.3); background:rgba(251,113,133,0.08);">
          <div style="display:flex; align-items:center; gap:1rem;">
             <div style="font-size:1.8rem; filter:drop-shadow(0 0 8px rgba(251,113,133,0.4));">🔥</div>
             <div style="font-size:1.05rem; color:#FFFFFF;">
               <strong>{nudge['recovery']}</strong>
             </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🧬 Scientific Deep Dive"):
            st.markdown(f"""
            <div class="alt-nudge-card">
              <div class="alt-card-header">Core Behavioral Mechanism</div>
              <div class="alt-card-body">"{nudge['insight']}"</div>
            </div>
            <div class="alt-nudge-card">
              <div class="alt-card-header">Methodology</div>
              <div class="alt-card-body">Utilizing <strong>{nudge['strategy']}</strong> to disrupt the {cause} pattern.</div>
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