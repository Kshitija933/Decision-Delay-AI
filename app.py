"""
DecisionDelay AI — Main App (Dark Theme)
Run: streamlit run app.py
"""

import streamlit as st
import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

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

# ── All inline dark-theme styles ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

[data-testid="stSidebarNav"] { display: none; }
[data-testid="stAppViewContainer"] { animation: fadein 0.4s ease; }
@keyframes fadein { from { opacity:0; transform:translateY(5px); } to { opacity:1; transform:none; } }
.block-container { padding-top: 0.6rem !important; padding-bottom: 0 !important; }

/* ══ DARK CARDS ══ */
.da-card {
  background: #131F35;
  border: 1px solid rgba(110,231,247,0.10);
  border-radius: 14px;
  padding: 1.35rem 1.6rem;
  margin-bottom: 0.75rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.35);
  color: #E2E8F0 !important;
  transition: box-shadow 0.2s ease;
}
.da-card:hover { box-shadow: 0 6px 32px rgba(0,0,0,0.45); }
.da-card p, .da-card div, .da-card span { color: #E2E8F0 !important; }
.da-card-accent { border-left: 4px solid #6EE7F7; }
.da-card-rose   { border-left: 4px solid #FB7185; }
.da-card-amber  { border-left: 4px solid #FCD34D; }
.da-card-violet { border-left: 4px solid #A78BFA; }
.da-card-mint   { border-left: 4px solid #34D399; }

/* ══ NUDGE BOX ══ */
.nudge-box {
  background: linear-gradient(135deg,rgba(110,231,247,0.06),rgba(167,139,250,0.06));
  border: 1.5px solid rgba(110,231,247,0.20);
  border-radius: 14px;
  padding: 1.35rem 1.6rem;
  margin: 0.75rem 0;
}
.nudge-prefix   { color: #64748B !important; font-size:0.8rem; font-family:'JetBrains Mono',monospace; margin-bottom:0.35rem; }
.nudge-text     { color: #E2E8F0 !important; font-size:1.08rem; font-weight:700; line-height:1.55; }
.nudge-strategy { color: #A78BFA !important; font-size:0.8rem; margin-top:0.5rem; font-weight:600; }

/* ══ CAUSE BADGE ══ */
.cause-badge {
  background: rgba(110,231,247,0.10);
  border: 1px solid rgba(110,231,247,0.25);
  color: #6EE7F7 !important;
  padding: 0.3rem 0.85rem;
  border-radius: 99px;
  font-size: 0.82rem;
  font-weight: 700;
  display: inline-block;
}

/* ══ STAT PILL ══ */
.stat-pill {
  background: #1A2A45;
  border: 1px solid rgba(110,231,247,0.12);
  border-radius: 99px;
  padding: 0.25rem 0.8rem;
  display: inline-block;
  font-size: 0.82rem;
  color: #94A3B8 !important;
  font-weight: 600;
  margin: 0.15rem;
}

/* ══ SEVERITY ══ */
.sev-low    { color: #34D399 !important; font-weight:700; }
.sev-medium { color: #FCD34D !important; font-weight:700; }
.sev-high   { color: #FB7185 !important; font-weight:700; }

/* ══ SECTION LABEL ══ */
.section-label {
  font-size: 0.72rem;
  color: #6EE7F7 !important;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-bottom: 0.6rem;
}

/* ══ HERO HEADLINE ══ */
.hero-title {
  background: linear-gradient(135deg, #6EE7F7, #A78BFA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 2.6rem;
  font-weight: 800;
  line-height: 1.18;
  margin: 0;
}
.hero-sub {
  color: #94A3B8 !important;
  font-size: 1.05rem;
  margin-top: 0.6rem;
  line-height: 1.65;
}

/* ══ STEP NUMBER BADGE ══ */
.step-num {
  background: rgba(110,231,247,0.12);
  color: #6EE7F7 !important;
  font-weight: 800;
  font-size: 0.75rem;
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
  padding: 2.2rem 1rem 1.4rem;
  position: relative;
}
.project-hero::before {
  content: '';
  display: block;
  width: 64px; height: 3px;
  background: linear-gradient(90deg, #6EE7F7, #A78BFA, #FB7185);
  border-radius: 2px;
  margin: 0 auto 1.4rem;
}
/* Glowing orb behind name */
.project-hero::after {
  content: '';
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translate(-50%,-50%);
  width: 500px; height: 200px;
  background: radial-gradient(ellipse, rgba(110,231,247,0.07) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}
.project-name {
  font-family: 'Playfair Display', Georgia, serif !important;
  font-size: 4.8rem;
  font-weight: 800;
  font-style: normal;
  font-variant: small-caps;
  line-height: 1.0;
  letter-spacing: 0.01em;
  background: linear-gradient(135deg,
    #3B4FE8 0%,
    #6A35C8 50%,
    #9B3FC8 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
  filter: drop-shadow(0 0 24px rgba(106,53,200,0.35))
          drop-shadow(0 4px 16px rgba(0,0,0,0.5));
  position: relative;
  z-index: 1;
}
.project-sub-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 1rem;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}
.project-badge {
  background: rgba(110,231,247,0.08);
  border: 1px solid rgba(110,231,247,0.22);
  border-radius: 99px;
  padding: 0.3rem 1rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #6EE7F7 !important;
  text-transform: uppercase;
  backdrop-filter: blur(4px);
}
.project-dot { width:4px; height:4px; border-radius:50%; background:#334155; display:inline-block; }

/* ══ SIDEBAR — dark ══ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0D1A2E 0%, #0B1120 100%) !important;
  border-right: 1px solid rgba(110,231,247,0.10) !important;
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] .stButton > button {
  color: #CBD5E1 !important;
  background: #1A2A45 !important;
  box-shadow: 0 1px 6px rgba(0,0,0,0.3) !important;
  border: 1px solid rgba(110,231,247,0.12) !important;
  font-weight: 600 !important;
  text-align: left !important;
  border-radius: 10px !important;
  padding: 0.55rem 0.85rem !important;
  font-size: 0.88rem !important;
  margin-bottom: 0.25rem !important;
  transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #1E3254 !important;
  border-color: rgba(110,231,247,0.30) !important;
  color: #6EE7F7 !important;
  transform: none !important;
  box-shadow: 0 2px 12px rgba(110,231,247,0.12) !important;
}

/* ── Page title bar ── */
.page-title-bar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(110,231,247,0.08);
  border: 1px solid rgba(110,231,247,0.18);
  border-radius: 8px;
  padding: 0.35rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: #6EE7F7 !important;
  letter-spacing: 0.05em;
  margin-top: 0.5rem;
}
.sidebar-nav-title {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #334155 !important;
  padding: 0.5rem 0 0.4rem;
}

/* ══ Metric cards dark ══ */
[data-testid="metric-container"] {
  background: #131F35 !important;
  border: 1px solid rgba(110,231,247,0.12) !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 16px rgba(0,0,0,0.35) !important;
}
[data-testid="metric-container"] label {
  color: #64748B !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
}
[data-testid="stMetricValue"] {
  color: #E2E8F0 !important;
  font-weight: 900 !important;
}
[data-testid="stWidgetLabel"] { color: #94A3B8 !important; font-weight: 600 !important; }
[data-testid="stTabs"] button { color: #64748B !important; font-weight: 600 !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
  color: #6EE7F7 !important;
  font-weight: 800 !important;
  border-bottom-color: #6EE7F7 !important;
}

/* ══ PREMIUM EXPANDER ══ */
.stExpander {
  background: rgba(13, 25, 48, 0.4) !important;
  border: 1px solid rgba(110, 231, 247, 0.15) !important;
  border-radius: 12px !important;
  margin-top: 0.5rem !important;
}
.stExpander [data-testid="stExpanderDetails"] {
  background: transparent !important;
  padding: 1rem !important;
}
.stExpander summary {
  color: #E2E8F0 !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
}
.stExpander summary:hover {
  color: #6EE7F7 !important;
}

.stSelectbox label, .stSlider label,
.stTextInput label, .stTextArea label,
.stRadio label, .stCheckbox label {
  color: #94A3B8 !important;
  font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

from utils.session import init_session
init_session()

# ── PAGE REGISTRY ──
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

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<div class="sidebar-nav-title">Navigation</div>', unsafe_allow_html=True)
    for p in PAGE_META:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
    cur = st.session_state.page
    icon, label = PAGE_META.get(cur, ("🧠", cur))
    st.markdown(f'<div class="page-title-bar">{icon} &nbsp; <strong style="color:#6EE7F7;">{label}</strong></div>',
                unsafe_allow_html=True)
    st.markdown("---")
    total  = st.session_state.total_analyses
    streak = st.session_state.streak
    st.markdown(f"""
    <div style="font-size:0.85rem;">
      <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;">
        <span style="color:#64748B;">Analyses</span>
        <span style="color:#6EE7F7;font-weight:700;">{total}</span>
      </div>
      <div style="display:flex;justify-content:space-between;">
        <span style="color:#64748B;">Streak</span>
        <span style="color:#FCD34D;font-weight:700;">{streak} 🔥</span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    model_status = "✅ Trained" if os.path.exists(
        os.path.join(BASE_DIR, "models", "delay_classifier.pt")) else "⚠️ Rule-Based"
    st.markdown(f'<span class="stat-pill">Model: {model_status}</span>', unsafe_allow_html=True)
    st.markdown('<span class="stat-pill">v1.0.0</span>', unsafe_allow_html=True)

# ── ROUTE ──
page = st.session_state.get("page", "🏠 Home")

if page == "🏠 Home":
    # Project name hero
    st.markdown("""
    <div class="project-hero">
      <span class="project-name">DecisionDelay AI</span>
      <div class="project-sub-row">
        <span class="project-badge">AI &times; Cognition</span>
        <span class="project-dot"></span>
        <span class="project-badge">Behavioral Intelligence</span>
        <span class="project-dot"></span>
        <span class="project-badge">No Surveillance</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="margin:0 0 1rem;border-color:rgba(110,231,247,0.08);">', unsafe_allow_html=True)

    main_left, main_right = st.columns([1.2, 1], gap="large")

    with main_left:
        st.markdown("""
        <div style="text-align:center;margin-bottom:1rem;color:#94A3B8;font-size:0.95rem;line-height:1.6;">
          DecisionDelay AI diagnoses the psychological root cause of your inaction —
          and delivers science-backed nudges to break the delay loop.
        </div>
        """, unsafe_allow_html=True)

        dc1, dc2, dc3 = st.columns(3, gap="small")
        with dc1:
            st.markdown("""<div class="da-card da-card-accent" style="text-align:center;">
              <div style="font-size:2.2rem;">🏋️</div>
              <div style="font-weight:800;font-size:1rem;margin:0.4rem 0 0.2rem;color:#E2E8F0;">Fitness</div>
              <div style="color:#64748B;font-size:0.84rem;">Gym, workout consistency</div>
            </div>""", unsafe_allow_html=True)
        with dc2:
            st.markdown("""<div class="da-card da-card-violet" style="text-align:center;">
              <div style="font-size:2.2rem;">📚</div>
              <div style="font-weight:800;font-size:1rem;margin:0.4rem 0 0.2rem;color:#E2E8F0;">Studying</div>
              <div style="color:#64748B;font-size:0.84rem;">Exam prep, daily habits</div>
            </div>""", unsafe_allow_html=True)
        with dc3:
            st.markdown("""<div class="da-card da-card-rose" style="text-align:center;">
              <div style="font-size:2.2rem;">💼</div>
              <div style="font-weight:800;font-size:1rem;margin:0.4rem 0 0.2rem;color:#E2E8F0;">Career</div>
              <div style="color:#64748B;font-size:0.84rem;">Applications, pivots, growth</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""<style>
        div[data-testid="stButton"] > button {
          font-size:1.12rem !important; padding:1rem 2rem !important;
          border-radius:12px !important; letter-spacing:0.03em !important;
          background: linear-gradient(135deg,#6EE7F7,#A78BFA) !important;
          color: #0B1120 !important; font-weight:800 !important;
          box-shadow: 0 0 24px rgba(110,231,247,0.3) !important;
        }
        </style>""", unsafe_allow_html=True)
        if st.button("🎯  Run Self-Assessment  →", use_container_width=True):
            st.session_state.page = "🎯 Self Assessment"
            st.rerun()

    with main_right:
        st.markdown("""<div class="da-card" style="margin-top:0;">
          <div class="section-label">How It Works</div>""", unsafe_allow_html=True)
        for num, title, desc in [
            ("01","Input","Rate task difficulty, reward delay, and past attempts"),
            ("02","Analyze","Neural network classifies your delay pattern"),
            ("03","Diagnose","Identify root cause from 6 cognitive categories"),
            ("04","Nudge","Get an evidence-based behavioral intervention"),
        ]:
            st.markdown(f"""<div style="display:flex;gap:0.9rem;align-items:flex-start;margin-bottom:0.85rem;">
              <span class="step-num">{num}</span>
              <div>
                <div style="font-weight:700;font-size:0.94rem;color:#E2E8F0;">{title}</div>
                <div style="color:#64748B;font-size:0.82rem;margin-top:0.1rem;line-height:1.45;">{desc}</div>
              </div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div class="da-card" style="margin-top:0.75rem;">
          <div class="section-label">Delay Cause Categories</div>""", unsafe_allow_html=True)
        for icon, name, color in [
            ("😨","Fear of Failure","#FB7185"),("🌀","Overwhelm / Complexity","#FCD34D"),
            ("⏳","Lack of Immediate Reward","#6EE7F7"),("🔁","Past Failure Loop","#A78BFA"),
            ("🎯","Perfectionism","#FB923C"),("🧩","Decision Fatigue","#38BDF8"),
        ]:
            st.markdown(f"""<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
              <span>{icon}</span>
              <div style="flex:1;font-size:0.86rem;color:#CBD5E1;font-weight:600;">{name}</div>
              <div style="width:9px;height:9px;border-radius:50%;background:{color};
                          box-shadow:0 0 6px {color}60;flex-shrink:0;"></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "🔬 Science Explorer":
    exec(open(os.path.join(BASE_DIR,"pages","1_Science_Explorer.py"),encoding="utf-8").read())
elif page == "📊 Model Performance":
    exec(open(os.path.join(BASE_DIR,"pages","2_Model_Performance.py"),encoding="utf-8").read())
elif page == "🎯 Self Assessment":
    exec(open(os.path.join(BASE_DIR,"pages","2_Self_Assessment.py"),encoding="utf-8").read())
elif page == "📈 Analytical Dashboard":
    exec(open(os.path.join(BASE_DIR,"pages","3_Analytical_Dashboard.py"),encoding="utf-8").read())
elif page == "📅 Habit Tracker":
    exec(open(os.path.join(BASE_DIR,"pages","4_Habit_Tracker.py"),encoding="utf-8").read())
elif page == "⚖️ Compare Tasks":
    exec(open(os.path.join(BASE_DIR,"pages","5_Compare_Tasks.py"),encoding="utf-8").read())