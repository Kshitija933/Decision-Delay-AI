"""
DecisionDelay AI — Main App (Light Theme)
Run: streamlit run app.py
"""

import streamlit as st
import os, sys, webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Auto-open browser ONCE via lockfile ──
_LOCK = os.path.join(BASE_DIR, ".browser_opened.lock")
if not os.path.exists(_LOCK):
    try:
        open(_LOCK, "w").close()
        webbrowser.open("http://localhost:8501", new=1)
    except Exception:
        pass

st.set_page_config(
    page_title="DecisionDelay AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ──
css_path = os.path.join(BASE_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── All inline styles ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,900;1,9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

[data-testid="stSidebarNav"] { display: none; }
[data-testid="stAppViewContainer"] { animation: fadein 0.4s ease; }
@keyframes fadein { from { opacity:0; transform:translateY(5px); } to { opacity:1; transform:none; } }
.block-container { padding-top: 0.6rem !important; padding-bottom: 0 !important; }

/* ══ CARDS ══ */
.da-card {
  background: #FFFFFF;
  border: 1.5px solid rgba(26,86,219,0.14);
  border-radius: 14px;
  padding: 1.5rem 1.8rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 4px 20px rgba(15,23,42,0.09);
  color: #0F172A !important;
  transition: all 0.2s ease;
}
.da-card p, .da-card div, .da-card span { color: #0F172A !important; }
.da-card-accent { border-left: 4px solid #1A56DB; }
.da-card-rose   { border-left: 4px solid #F43F5E; }
.da-card-amber  { border-left: 4px solid #F59E0B; }
.da-card-violet { border-left: 4px solid #7C3AED; }
.da-card-mint   { border-left: 4px solid #10B981; }

/* ══ NUDGE BOX ══ */
.nudge-box {
  background: linear-gradient(135deg,rgba(26,86,219,0.05),rgba(124,58,237,0.05));
  border: 1.5px solid rgba(26,86,219,0.18);
  border-radius: 14px;
  padding: 1.35rem 1.6rem;
  margin: 0.75rem 0;
}
.nudge-prefix   { color: #334155 !important; font-size:0.8rem; font-family:'JetBrains Mono',monospace; margin-bottom:0.35rem; }
.nudge-text     { color: #0F172A !important; font-size:1.08rem; font-weight:700; line-height:1.55; }
.nudge-strategy { color: #7C3AED !important; font-size:0.8rem; margin-top:0.5rem; font-weight:600; }

/* ══ CAUSE BADGE ══ */
.cause-badge {
  background: rgba(26,86,219,0.08);
  border: 1px solid rgba(26,86,219,0.2);
  color: #1A56DB !important;
  padding: 0.3rem 0.85rem;
  border-radius: 99px;
  font-size: 0.82rem;
  font-weight: 700;
  display: inline-block;
}

/* ══ STAT PILL ══ */
.stat-pill {
  background: #F1F5F9;
  border: 1px solid rgba(26,86,219,0.14);
  border-radius: 99px;
  padding: 0.25rem 0.8rem;
  display: inline-block;
  font-size: 0.82rem;
  color: #1E293B !important;
  font-weight: 600;
  margin: 0.15rem;
}

/* ══ SEVERITY ══ */
.sev-low    { color: #059669 !important; font-weight:700; }
.sev-medium { color: #D97706 !important; font-weight:700; }
.sev-high   { color: #DC2626 !important; font-weight:700; }

/* ══ SECTION LABEL ══ */
.section-label {
  font-size: 0.85rem;
  color: #475569 !important;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 0.4rem;
}

/* ══ HERO HEADLINE ══ */
.hero-title {
  background: linear-gradient(135deg, #1A56DB, #7C3AED);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 2.85rem;
  font-weight: 800;
  line-height: 1.18;
  margin: 0;
}
.hero-sub {
  color: #334155 !important;
  font-size: 1.12rem;
  margin-top: 0.6rem;
  line-height: 1.65;
}

/* ══ STEP NUMBER BADGE ══ */
.step-num {
  background: rgba(26,86,219,0.10);
  color: #1A56DB !important;
  font-weight: 800;
  font-size: 0.8rem;
  padding: 0.3rem 0.55rem;
  border-radius: 7px;
  min-width: 32px;
  text-align: center;
  display: inline-block;
  flex-shrink: 0;
}

/* ══ PROJECT NAME HERO ══ */
.project-hero {
  text-align: center;
  padding: 1.6rem 1rem 1.2rem;
}
.project-hero::before {
  content: '';
  display: block;
  width: 56px; height: 4px;
  background: linear-gradient(90deg, #1A56DB, #7C3AED);
  border-radius: 2px;
  margin: 0 auto 1.3rem;
}
.project-name {
  font-family: 'Fraunces', Georgia, serif !important;
  font-size: 4.8rem;
  font-weight: 900;
  font-style: normal;
  font-variant: small-caps;
  line-height: 1.0;
  letter-spacing: 0.04em;
  background: linear-gradient(135deg, #1A56DB 0%, #7C3AED 50%, #F43F5E 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
  filter: drop-shadow(0 3px 12px rgba(26,86,219,0.20));
  text-shadow: none;
}
.project-sub-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 0.9rem;
  flex-wrap: wrap;
}
.project-badge {
  background: rgba(26,86,219,0.07);
  border: 1px solid rgba(26,86,219,0.18);
  border-radius: 99px;
  padding: 0.28rem 0.9rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #1A56DB !important;
  text-transform: uppercase;
}
.project-dot { width:5px; height:5px; border-radius:50%; background:#CBD5E1; display:inline-block; }
.project-tagline {
  font-size: 1.05rem;
  font-weight: 500;
  color: #334155 !important;
  margin-top: 0.6rem;
  display: block;
}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #DBEAFE 0%, #EFF6FF 60%, #F8FAFC 100%) !important;
}
[data-testid="stSidebar"] * { color: #1E293B !important; }
[data-testid="stSidebar"] .stButton > button {
  color: #1E293B !important;
  background: #FFFFFF !important;
  box-shadow: 0 1px 6px rgba(26,86,219,0.10) !important;
  border: 1px solid rgba(26,86,219,0.16) !important;
  font-weight: 600 !important;
  text-align: left !important;
  border-radius: 10px !important;
  padding: 0.55rem 0.85rem !important;
  font-size: 0.88rem !important;
  margin-bottom: 0.25rem !important;
  transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #DBEAFE !important;
  border-color: rgba(26,86,219,0.35) !important;
  color: #1A56DB !important;
  transform: none !important;
  box-shadow: 0 2px 10px rgba(26,86,219,0.18) !important;
}

/* ── Page title bar (shown always below nav) ── */
.page-title-bar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(26,86,219,0.07);
  border: 1px solid rgba(26,86,219,0.18);
  border-radius: 8px;
  padding: 0.35rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: #1A56DB !important;
  letter-spacing: 0.05em;
  margin-top: 0.5rem;
}

.sidebar-nav-title {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #64748B !important;
  padding: 0.5rem 0 0.4rem;
}

/* ══ Metric cards — always dark ══ */
[data-testid="metric-container"] {
  background: #FFFFFF !important;
  border: 1.5px solid rgba(26,86,219,0.12) !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 12px rgba(15,23,42,0.06) !important;
}
[data-testid="metric-container"] label {
  color: #475569 !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
}
[data-testid="stMetricValue"] {
  color: #0F172A !important;
  font-weight: 900 !important;
}
[data-testid="stWidgetLabel"] {
  color: #334155 !important;
  font-weight: 600 !important;
}
[data-testid="stTabs"] button {
  color: #334155 !important;
  font-weight: 600 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: #1A56DB !important;
  font-weight: 800 !important;
  border-bottom-color: #1A56DB !important;
}
.stSelectbox label, .stSlider label,
.stTextInput label, .stTextArea label,
.stRadio label, .stCheckbox label {
  color: #334155 !important;
  font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──
from utils.session import init_session
init_session()

# ─────────────────────────────────────────
# PAGE REGISTRY
# ─────────────────────────────────────────
PAGE_META = {
    "🏠 Home":              ("🏠", "Home"),
    "🔬 Science Explorer":  ("🔬", "Science Explorer"),
    "📊 Model Performance": ("📊", "Model Performance"),
    "🎯 Self Assessment":   ("🎯", "Self Assessment"),
    "📈 Analytical Dashboard": ("📈", "Analytical Dashboard"),
    "📅 Habit Tracker":     ("📅", "Habit Tracker"),
    "⚖️ Compare Tasks":    ("⚖️", "Compare Tasks"),
}

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-nav-title">Navigation</div>', unsafe_allow_html=True)

    for p in PAGE_META:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p

    # ── Current page indicator ──
    cur = st.session_state.page
    icon, label = PAGE_META.get(cur, ("🧠", cur))
    st.markdown(f"""
    <div class="page-title-bar">
      {icon} &nbsp; Currently: <strong style="color:#1A56DB;">{label}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    total  = st.session_state.total_analyses
    streak = st.session_state.streak
    st.markdown(f"""
    <div style="font-size:0.85rem;">
      <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;">
        <span style="color:#475569;">Analyses</span>
        <span style="color:#1A56DB;font-weight:700;">{total}</span>
      </div>
      <div style="display:flex;justify-content:space-between;">
        <span style="color:#475569;">Streak</span>
        <span style="color:#D97706;font-weight:700;">{streak} 🔥</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    model_status = "✅ Trained" if os.path.exists(
        os.path.join(BASE_DIR, "models", "delay_classifier.pt")) else "⚠️ Rule-Based"
    st.markdown(f'<span class="stat-pill">Model: {model_status}</span>', unsafe_allow_html=True)
    st.markdown('<span class="stat-pill">v1.0.0</span>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# ROUTE
# ─────────────────────────────────────────
page = st.session_state.get("page", "🏠 Home")

if page == "🏠 Home":

    # ══ TOP: Project name centred ══
    st.markdown("""
    <div class="project-hero">
      <span class="project-name">DecisionDelay AI</span>
      <div class="project-sub-row">
        <span class="project-badge">AI &times; COGNITION</span>
        <span class="project-dot"></span>
        <span class="project-badge">BEHAVIORAL INTELLIGENCE</span>
        <span class="project-dot"></span>
        <span class="project-badge">NO SURVEILLANCE</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="margin:0 0 0.8rem;border-color:rgba(26,86,219,0.10);">', unsafe_allow_html=True)

    # ══ MAIN LAYOUT: Left (Hero + Cards + Button) and Right (How It Works + Categories) ══
    main_left, main_right = st.columns([1.2, 1], gap="large")

    with main_left:
        # ══ MIDDLE: Hero text + domain cards + button ══
        st.markdown("""
        <div style="text-align:center;margin-bottom:0.5rem;">
          <h1 class="hero-title" style="justify-content:center;">
            Why do people know what to do —<br>but still don't act?
          </h1>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-bottom:1rem;color:#334155;font-size:0.95rem;line-height:1.6;">
          DecisionDelay AI diagnoses the psychological root cause of your inaction — and delivers science-backed nudges to break the delay loop.
        </div>
        """, unsafe_allow_html=True)

        # Domain cards — 3 columns inside the left column
        dc1, dc2, dc3 = st.columns(3, gap="small")
        with dc1:
            st.markdown("""<div class="da-card da-card-accent" style="text-align:center;">
              <div style="font-size:2.5rem;">🏋️</div>
              <div style="font-weight:800;font-size:1.08rem;margin:0.45rem 0 0.25rem;color:#0F172A;">Fitness</div>
              <div style="color:#475569;font-size:0.88rem;">Gym attendance, workout consistency</div>
            </div>""", unsafe_allow_html=True)
        with dc2:
            st.markdown("""<div class="da-card da-card-violet" style="text-align:center;">
              <div style="font-size:2.5rem;">📚</div>
              <div style="font-weight:800;font-size:1.08rem;margin:0.45rem 0 0.25rem;color:#0F172A;">Studying</div>
              <div style="color:#475569;font-size:0.88rem;">Exam prep, daily learning habits</div>
            </div>""", unsafe_allow_html=True)
        with dc3:
            st.markdown("""<div class="da-card da-card-rose" style="text-align:center;">
              <div style="font-size:2.5rem;">💼</div>
              <div style="font-weight:800;font-size:1.08rem;margin:0.45rem 0 0.25rem;color:#0F172A;">Career</div>
              <div style="color:#475569;font-size:0.88rem;">Job applications, pivots, growth</div>
            </div>""", unsafe_allow_html=True)

        # Add spacing before button
        st.markdown('<div style="margin-bottom:0.4rem;"></div>', unsafe_allow_html=True)

        # CTA button
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button {
          font-size: 1.18rem !important;
          padding: 1.0rem 2.0rem !important;
          border-radius: 12px !important;
          letter-spacing: 0.03em !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("🎯  Run Self-Assessment  →", use_container_width=True):
            st.session_state.page = "🎯 Self Assessment"
            st.rerun()

    with main_right:
        # ══ BOTTOM RIGHT: How It Works + Delay Cause Categories ══
        st.markdown("""<div class="da-card" style="margin-top:0;">
          <div class="section-label">How It Works</div>""", unsafe_allow_html=True)
        for num, title, desc in [
            ("01", "Input",    "Rate task difficulty, reward delay, and past attempts"),
            ("02", "Analyze",  "Neural network classifies your delay pattern"),
            ("03", "Diagnose", "Identify root cause from 6 cognitive categories"),
            ("04", "Nudge",    "Get an evidence-based behavioral intervention"),
        ]:
            st.markdown(f"""<div style="display:flex;gap:0.9rem;align-items:flex-start;margin-bottom:0.8rem;">
              <span class="step-num">{num}</span>
              <div>
                <div style="font-weight:700;font-size:1.02rem;color:#0F172A;">{title}</div>
                <div style="color:#475569;font-size:0.90rem;margin-top:0.1rem;line-height:1.45;">{desc}</div>
              </div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div style="margin-bottom:1.2rem;"></div>', unsafe_allow_html=True)

        st.markdown("""<div class="da-card" style="margin-top:0;">
          <div class="section-label">Delay Cause Categories</div>""", unsafe_allow_html=True)
        for icon, name, color in [
            ("😨", "Fear of Failure",           "#F43F5E"),
            ("🌀", "Overwhelm / Complexity",    "#F59E0B"),
            ("⏳", "Lack of Immediate Reward",  "#1A56DB"),
            ("🔁", "Past Failure Loop",         "#7C3AED"),
            ("🎯", "Perfectionism",             "#FB8500"),
            ("🧩", "Decision Fatigue",          "#0EA5E9"),
        ]:
            st.markdown(f"""<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
              <span style="font-size:1.1rem;">{icon}</span>
              <div style="flex:1;font-size:0.97rem;color:#1E293B;font-weight:600;">{name}</div>
              <div style="width:10px;height:10px;border-radius:50%;background:{color};flex-shrink:0;"></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ── PAGE ROUTING ──
elif page == "🔬 Science Explorer":
    exec(open(os.path.join(BASE_DIR, "pages", "1_Science_Explorer.py"), encoding="utf-8").read())

elif page == "📊 Model Performance":
    exec(open(os.path.join(BASE_DIR, "pages", "2_Model_Performance.py"), encoding="utf-8").read())

elif page == "🎯 Self Assessment":
    exec(open(os.path.join(BASE_DIR, "pages", "2_Self_Assessment.py"), encoding="utf-8").read())

elif page == "📈 Analytical Dashboard":
    exec(open(os.path.join(BASE_DIR, "pages", "3_Analytical_Dashboard.py"), encoding="utf-8").read())

elif page == "📅 Habit Tracker":
    exec(open(os.path.join(BASE_DIR, "pages", "4_Habit_Tracker.py"), encoding="utf-8").read())

elif page == "⚖️ Compare Tasks":
    exec(open(os.path.join(BASE_DIR, "pages", "5_Compare_Tasks.py"), encoding="utf-8").read())