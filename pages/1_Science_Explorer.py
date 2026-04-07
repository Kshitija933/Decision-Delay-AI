"""
Page 1 — Science Explorer
Explains the psychology behind decision delay.
"""
import streamlit as st

st.markdown("""
<div style="margin-bottom:1.5rem;">
<div style="margin-bottom:1.5rem;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
    <span style="font-size:1.6rem;">🔬</span>
    <h2 style="margin:0;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.9rem;
               font-weight:800;color:#0F172A;letter-spacing:-0.02em;">Science Explorer</h2>
  </div>
  <div style="height:3px;width:60px;background:linear-gradient(90deg,#1A56DB,#7C3AED);
              border-radius:2px;margin-bottom:0.5rem;"></div>
  <p style="color:#475569;font-size:0.96rem;margin:0;font-weight:500;">The cognitive science behind why humans delay action</p>
</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📖 The Problem", "🧬 Delay Causes", "📐 The Framework", "🔗 References"
])

with tab1:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown("""
        <div class="da-card da-card-accent">
          <h3 style="margin:0 0 0.75rem;font-size:1.1rem;">The Action Gap</h3>
          <p style="color:#475569;line-height:1.7;">
            Humans possess remarkable self-awareness — we know exercise improves health,
            we know studying leads to better grades, we know career moves require action.
            Yet the gap between <em>knowing</em> and <em>doing</em> is one of the most
            persistent puzzles in behavioral science.
          </p>
          <p style="color:#475569;line-height:1.7;">
            This isn't laziness. Research identifies specific, predictable cognitive patterns
            that trigger inaction — and each pattern responds to a different intervention.
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="da-card da-card-amber">
          <h3 style="margin:0 0 0.75rem;font-size:1.1rem;">🧠 Temporal Motivation Theory</h3>
          <p style="color:#475569;line-height:1.7;">
            Steel (2007) formalized procrastination as:
          </p>
          <div style="background:#F8FAFC;border-radius:8px;padding:1rem;margin:0.75rem 0;font-family:'JetBrains Mono',monospace;font-size:0.9rem;color:#1A56DB;">
            Motivation = (Expectancy × Value) / (Impulsivity × Delay)
          </div>
          <p style="color:#475569;font-size:0.85rem;">
            High task difficulty reduces expectancy. Long time-to-reward increases perceived delay.
            Past failures reduce both expectancy and value simultaneously.
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="da-card da-card-violet">
          <h3 style="margin:0 0 0.75rem;font-size:1.1rem;">🎯 BJ Fogg's Behavior Model</h3>
          <p style="color:#475569;line-height:1.7;">
            Behavior = Motivation × Ability × Prompt. All three must be present simultaneously.
            DecisionDelay AI diagnoses which element is weakest and targets it directly.
          </p>
          <div style="display:flex;gap:0.75rem;margin-top:0.75rem;">
            <div style="flex:1;background:#F8FAFC;border-radius:8px;padding:0.75rem;text-align:center;">
              <div style="color:#1A56DB;font-weight:700;font-size:1.2rem;">M</div>
              <div style="color:#475569;font-size:0.75rem;margin-top:0.25rem;">Motivation</div>
            </div>
            <div style="flex:1;background:#F8FAFC;border-radius:8px;padding:0.75rem;text-align:center;">
              <div style="color:#7C3AED;font-weight:700;font-size:1.2rem;">A</div>
              <div style="color:#475569;font-size:0.75rem;margin-top:0.25rem;">Ability</div>
            </div>
            <div style="flex:1;background:#F8FAFC;border-radius:8px;padding:0.75rem;text-align:center;">
              <div style="color:#FFB703;font-weight:700;font-size:1.2rem;">P</div>
              <div style="color:#475569;font-size:0.75rem;margin-top:0.25rem;">Prompt</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="da-card">
          <div style="font-size:0.7rem;color:#475569;letter-spacing:0.1em;font-weight:700;margin-bottom:1rem;">
            KEY STATISTICS
          </div>
        """, unsafe_allow_html=True)
        stats = [
            ("20%", "of adults identify as chronic procrastinators"),
            ("95%", "admit to procrastinating some of the time"),
            ("1/3", "of daily activities are delayed on average"),
            ("40%", "of people have missed career opportunities due to delay"),
            ("3×", "more likely to procrastinate after a past failure"),
        ]
        for num, desc in stats:
            st.markdown(f"""
            <div style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid rgba(26,86,219,0.05);">
              <div style="font-size:1.8rem;font-weight:800;color:#1A56DB;">{num}</div>
              <div style="color:#475569;font-size:0.82rem;margin-top:0.15rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="da-card da-card-rose" style="margin-top:0.5rem;">
          <h4 style="margin:0 0 0.75rem;font-size:0.95rem;">No Sensors. No Surveillance.</h4>
          <p style="color:#475569;font-size:0.82rem;line-height:1.6;">
            DecisionDelay AI works entirely from self-reported psychological inputs.
            No biometric tracking, no screen monitoring, no behavioral surveillance.
            Privacy-first behavioral intelligence.
          </p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <p style="color:#475569;margin-bottom:1.5rem;">
      Six scientifically-validated delay patterns, each with distinct neural signatures and interventions.
    </p>
    """, unsafe_allow_html=True)

    causes_data = [
        {
            "icon": "😨", "name": "Fear of Failure", "color": "#FF4D6D",
            "theory": "Atkinson's Achievement Motivation Theory",
            "desc": "Avoidance behavior triggered by anticipation of negative evaluation. The perceived cost of failure outweighs the expected value of success.",
            "triggers": ["High stakes outcome", "Public performance", "Past criticism", "Imposter syndrome"],
            "intervention": "Failure-cost analysis + minimum viable action protocol",
        },
        {
            "icon": "🌀", "name": "Overwhelm / Complexity", "color": "#FFB703",
            "theory": "Cognitive Load Theory (Sweller, 1988)",
            "desc": "Working memory overload creates paralysis. When a task exceeds perceived cognitive capacity, the brain defaults to avoidance.",
            "triggers": ["Unclear first step", "Many sub-tasks", "Novel domain", "Information overload"],
            "intervention": "Task decomposition + single next action framework",
        },
        {
            "icon": "⏳", "name": "Lack of Immediate Reward", "color": "#1A56DB",
            "theory": "Hyperbolic Discounting (Ainslie, 1975)",
            "desc": "Humans discount future rewards non-linearly. Benefits weeks away feel abstract; immediate discomfort feels concrete.",
            "triggers": ["Long timeline to results", "Abstract future benefit", "Low intrinsic motivation", "No feedback loop"],
            "intervention": "Temptation bundling + implementation intentions",
        },
        {
            "icon": "🔁", "name": "Past Failure Loop", "color": "#7C3AED",
            "theory": "Learned Helplessness (Seligman, 1967)",
            "desc": "Repeated unsuccessful attempts create a conditioned association between effort and failure, suppressing future initiation.",
            "triggers": ["Multiple prior attempts failed", "Negative self-narrative", "Low self-efficacy", "Fixed mindset"],
            "intervention": "Identity reframing + variable change protocol",
        },
        {
            "icon": "🎯", "name": "Perfectionism", "color": "#FB8500",
            "theory": "Self-Determination Theory (Deci & Ryan)",
            "desc": "Maladaptive perfectionism creates an impossibly high threshold for action initiation, converting standard tasks into unattainable ideals.",
            "triggers": ["Fear of judgment", "High standards", "All-or-nothing thinking", "Unclear 'done' criteria"],
            "intervention": "Good enough threshold + time-boxing",
        },
        {
            "icon": "🧩", "name": "Decision Fatigue", "color": "#4CC9F0",
            "theory": "Ego Depletion (Baumeister, 1998)",
            "desc": "Decision-making depletes a finite cognitive resource. After multiple decisions, willpower for subsequent choices degrades significantly.",
            "triggers": ["Many daily decisions", "High-stress environment", "Decision overload", "Analysis paralysis"],
            "intervention": "Decision batching + environment design",
        },
    ]

    col1, col2 = st.columns(2, gap="medium")
    for i, c in enumerate(causes_data):
        target = col1 if i % 2 == 0 else col2
        with target:
            st.markdown(f"""
            <div class="da-card" style="border-left:3px solid {c['color']}">
              <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                <span style="font-size:1.5rem">{c['icon']}</span>
                <div>
                  <div style="font-weight:800;color:#0F172A;">{c['name']}</div>
                  <div style="color:{c['color']};font-size:0.72rem;font-family:'JetBrains Mono',monospace;">{c['theory']}</div>
                </div>
              </div>
              <p style="color:#475569;font-size:0.82rem;line-height:1.6;margin:0 0 0.75rem;">{c['desc']}</p>
              <div style="margin-bottom:0.5rem;">
                <div style="font-size:0.7rem;color:#475569;font-weight:700;margin-bottom:0.3rem;">TRIGGERS</div>
                <div>{''.join(f'<span class="stat-pill">{t}</span>' for t in c['triggers'])}</div>
              </div>
              <div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid rgba(26,86,219,0.05);">
                <div style="font-size:0.7rem;color:#475569;font-weight:700;">INTERVENTION</div>
                <div style="color:{c['color']};font-size:0.82rem;font-weight:600;margin-top:0.2rem;">{c['intervention']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="da-card da-card-accent">
      <h3 style="margin:0 0 1rem;font-size:1.1rem;">Model Input→Output Framework</h3>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown("""
        <div style="background:#F8FAFC;border-radius:10px;padding:1rem;">
          <div style="color:#1A56DB;font-weight:800;font-size:0.8rem;letter-spacing:0.1em;margin-bottom:0.75rem;">INPUTS</div>
          <div style="color:#475569;font-size:0.8rem;font-family:'JetBrains Mono',monospace;line-height:2;">
            task_difficulty<br>time_to_reward<br>past_failure_loops<br>self_efficacy<br>stress_level<br>goal_clarity<br>social_support<br>intrinsic_motivation<br>habit_strength<br>distraction_level
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#F8FAFC;border-radius:10px;padding:1rem;">
          <div style="color:#7C3AED;font-weight:800;font-size:0.8rem;letter-spacing:0.1em;margin-bottom:0.75rem;">MODEL</div>
          <div style="color:#475569;font-size:0.78rem;line-height:1.8;">
            <div style="margin-bottom:0.5rem;padding:0.5rem;background:#FFFFFF;border-radius:6px;font-family:'JetBrains Mono',monospace;">
              Feature Engineering<br>↓<br>Shared Backbone<br>[128→64 neurons]<br>↓
            </div>
            <div style="display:flex;gap:0.5rem;">
              <div style="flex:1;background:#FFFFFF;border-radius:6px;padding:0.5rem;text-align:center;font-size:0.72rem;">
                Classifier Head
              </div>
              <div style="flex:1;background:#FFFFFF;border-radius:6px;padding:0.5rem;text-align:center;font-size:0.72rem;">
                Regressor Head
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#F8FAFC;border-radius:10px;padding:1rem;">
          <div style="color:#FFB703;font-weight:800;font-size:0.8rem;letter-spacing:0.1em;margin-bottom:0.75rem;">OUTPUTS</div>
          <div style="color:#475569;font-size:0.8rem;line-height:2;">
            <span style="color:#FF4D6D;">●</span> Delay Cause (6-class)<br>
            <span style="color:#1A56DB;">●</span> Severity Score (0-1)<br>
            <span style="color:#7C3AED;">●</span> Confidence Score<br>
            <span style="color:#FFB703;">●</span> Class Probabilities<br>
            <span style="color:#4CC9F0;">●</span> Behavioral Nudge
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    refs = [
        ("Steel, P. (2007)", "The nature of procrastination: A meta-analytic and theoretical review.", "Psychological Bulletin, 133(1), 65–94."),
        ("Fogg, B.J. (2019)", "Tiny Habits: The Small Changes That Change Everything.", "Houghton Mifflin Harcourt."),
        ("Gollwitzer, P.M. (1999)", "Implementation intentions: Strong effects of simple plans.", "American Psychologist, 54(7), 493–503."),
        ("Seligman, M.E.P. (1972)", "Learned helplessness.", "Annual Review of Medicine, 23, 407–412."),
        ("Deci, E.L. & Ryan, R.M. (2000)", "The 'what' and 'why' of goal pursuits.", "Psychological Inquiry, 11(4), 227–268."),
        ("Baumeister, R.F. et al. (1998)", "Ego depletion: Is the active self a limited resource?", "JPSP, 74(5), 1252–1265."),
        ("Ainslie, G. (1975)", "Specious reward: A behavioral theory of impulsiveness.", "Psychological Bulletin, 82(4), 463–496."),
    ]
    for authors, title, journal in refs:
        st.markdown(f"""
        <div class="da-card" style="margin-bottom:0.5rem;padding:0.75rem 1rem;">
          <div style="font-weight:700;font-size:0.85rem;color:#1A56DB;">{authors}</div>
          <div style="color:#0F172A;font-size:0.85rem;margin:0.2rem 0;">{title}</div>
          <div style="color:#475569;font-size:0.78rem;font-style:italic;">{journal}</div>
        </div>
        """, unsafe_allow_html=True)