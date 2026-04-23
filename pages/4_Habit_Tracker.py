"""
Page 3 — Habit Tracker
Log daily habit completions, view streaks and heatmaps.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.session import log_habit
from utils.visualizer import habit_heatmap, severity_timeline, cause_donut
from configs.settings import APP_CFG

st.markdown("""
<div style="margin-bottom:0.8rem;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
    <span style="font-size:1.6rem;">📅</span>
    <h2 style="margin:0;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.9rem;
               font-weight:800;color:#E2E8F0;letter-spacing:-0.02em;">Habit Tracker</h2>
  </div>
  <div style="height:3px;width:60px;background:linear-gradient(90deg,#38BDF8,#A78BFA);
              border-radius:2px;margin-bottom:0.5rem;"></div>
  <p style="color:#94A3B8;font-size:0.96rem;margin:0;font-weight:500;">Track daily actions, streaks, and behavioral progress</p>
</div>
""", unsafe_allow_html=True)

col_log, col_stats = st.columns([2, 3], gap="large")

with col_log:
    st.markdown("#### ✏️ Log Today's Action")

    domain = st.selectbox("Domain", APP_CFG.use_cases, key="ht_domain")
    action_note = st.text_area(
        "What did you do today?",
        placeholder="e.g. Completed 20-min workout, read 10 pages...",
        height=100, key="ht_note"
    )
    completed = st.radio(
        "Did you complete your planned action?",
        ["✅ Yes, completed!", "🔄 Partial", "❌ Not today"],
        horizontal=False, key="ht_completed"
    )
    if st.button("📝 Log Entry", use_container_width=True):
        success = completed.startswith("✅")
        log_habit(domain, success, action_note)
        if success:
            st.success(f"🔥 Logged! Streak: {st.session_state.streak}")
            st.balloons()
        else:
            st.info("Logged. Tomorrow is a new start.")

    # ── Streak display ──
    streak = st.session_state.streak
    streak_color = "#38BDF8" if streak >= 7 else "#FCD34D" if streak >= 3 else "#94A3B8"
    st.markdown(f"""
    <div class="da-card" style="text-align:center;margin-top:0.5rem;">
      <div style="font-size:0.7rem;color:#67E8F9;font-weight:700;margin-bottom:0.5rem;letter-spacing:0.1em;">CURRENT STREAK</div>
      <div style="font-size:3.5rem;font-weight:800;color:{streak_color};">{streak}</div>
      <div style="color:#94A3B8;font-size:0.85rem;">consecutive days</div>
      {"<div style='margin-top:0.5rem;font-size:1.2rem;'>🔥🔥🔥</div>" if streak >= 7 else ""}
      {"<div style='margin-top:0.5rem;font-size:1.2rem;'>🔥</div>" if 2 < streak < 7 else ""}
    </div>
    """, unsafe_allow_html=True)

    # ── Quick stats ──
    log = st.session_state.habit_log
    if log:
        total_logs = len(log)
        completed_count = sum(1 for e in log if e["completed"])
        rate = completed_count / total_logs * 100
        st.markdown(f"""
        <div class="da-card" style="margin-top:0.5rem;">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
            <div style="text-align:center;">
              <div style="font-size:1.5rem;font-weight:800;color:#38BDF8;">{total_logs}</div>
              <div style="font-size:0.75rem;color:#94A3B8;">Total Logs</div>
            </div>
            <div style="text-align:center;">
              <div style="font-size:1.5rem;font-weight:800;color:#FCD34D;">{rate:.0f}%</div>
              <div style="font-size:0.75rem;color:#94A3B8;">Completion Rate</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

with col_stats:
    log = st.session_state.habit_log
    history = st.session_state.history

    if log:
        st.markdown("#### 🗓️ Activity Heatmap")
        fig_hm = habit_heatmap(log)
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

    if history:
        st.markdown("#### 📉 Delay Severity Over Time")
        fig_tl = severity_timeline(history)
        st.plotly_chart(fig_tl, use_container_width=True, config={"displayModeBar": False})

        st.markdown("#### 🍩 Delay Cause Breakdown")
        fig_dn = cause_donut(history)
        st.plotly_chart(fig_dn, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:300px;text-align:center;">
          <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
          <div style="font-weight:700;color:#E2E8F0;">No analysis history yet</div>
          <div style="font-size:0.85rem;margin-top:0.3rem;color:#94A3B8;">
            Run a Self Assessment to see patterns here
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Log table ──
    if log:
        st.markdown("#### 📋 Entry Log")
        df_log = pd.DataFrame(log)
        df_log["Status"] = df_log["completed"].map({True: "✅", False: "❌"})
        df_log = df_log[["date", "time", "domain", "Status", "note"]].rename(columns={
            "date": "Date", "time": "Time", "domain": "Domain", "note": "Note"
        })
        st.dataframe(
            df_log.tail(20).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

    # ── Tips ──
    st.markdown("""
    <div class="da-card da-card-violet" style="margin-top:0.5rem;">
      <div style="font-weight:700;margin-bottom:0.5rem;color:#E2E8F0;">💡 Streak Science</div>
      <div style="color:#CBD5E1;font-size:0.82rem;line-height:1.7;">
        Research shows habits become automatic at ~66 days (Lally et al., 2010).
        A 3-day streak activates identity reinforcement. A 7-day streak begins
        neurological pattern formation. Missing once is recoverable — missing twice
        creates a new pattern.
      </div>
    </div>
    """, unsafe_allow_html=True)