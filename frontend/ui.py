import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
<style>
/* ----------------------------
   CardioTwin Clinical Theme
   Premium hospital dark (calm)
----------------------------- */

:root{
  --bg0:#070b14;
  --bg1:#0b1220;
  --panel: rgba(255,255,255,0.06);
  --panel-strong: rgba(255,255,255,0.09);
  --border: rgba(148,163,184,0.20);
  --text:#eaf0fb;
  --muted:#b9c6dd;
  --accent:#0ea5e9;   /* calm clinical blue */
  --accent2:#14b8a6;  /* teal highlight */
}

/* App background and global text */
.stApp {
  background: radial-gradient(1200px 680px at 12% 0%, rgba(14,165,233,0.18) 0%, rgba(7,11,20,0) 55%),
              radial-gradient(1000px 600px at 92% 12%, rgba(20,184,166,0.14) 0%, rgba(7,11,20,0) 52%),
              linear-gradient(180deg, var(--bg1) 0%, var(--bg0) 100%);
  color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.03) 100%);
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
  color: var(--text) !important;
}

/* Headings */
h1, h2, h3, h4 { letter-spacing: 0.15px; }

/* Metric cards */
div[data-testid="metric-container"] {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 10px 12px;
  box-shadow: 0 16px 34px rgba(0,0,0,0.22);
}
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] div {
  color: var(--text) !important;
}

/* Data blocks and alerts */
div.stAlert, .stCodeBlock, .stDataFrame, .stTable {
    border-radius: 12px !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: rgba(255,255,255,0.07) !important;
    color: var(--text) !important;
    font-weight: 600 !important;
    transition: all 140ms ease-in-out !important;
    box-shadow: 0 14px 30px rgba(0,0,0,0.18);
}
.stButton > button:hover {
    border-color: rgba(14, 165, 233, 0.55) !important;
    background: rgba(255,255,255,0.10) !important;
}
.stButton > button[kind="primary"] {
    border: 1px solid rgba(14,165,233,0.75) !important;
    background: linear-gradient(135deg, rgba(14,165,233,0.95) 0%, rgba(20,184,166,0.92) 100%) !important;
    color: #06101e !important;
    box-shadow: 0 18px 40px rgba(14,165,233,0.22);
}
.stButton > button[kind="primary"]:hover {
    border-color: rgba(20,184,166,0.85) !important;
    filter: brightness(1.03);
}
.stButton > button, button, [role="button"] {
    cursor: pointer !important;
}

/* Reduce annoying text-selection/caret behavior on click targets */
button, [role="button"], .nav-chip, .stMetric, summary {
    user-select: none !important;
    -webkit-user-select: none !important;
}

/* Inputs and expanders */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
  background: rgba(255,255,255,0.06) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
/* Selects */
div[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
}
div[data-baseweb="select"] span { color: var(--text) !important; }
div[data-baseweb="select"] svg { fill: var(--muted) !important; }

details {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.2rem 0.4rem;
    box-shadow: 0 14px 34px rgba(0,0,0,0.18);
}

/* Custom cards from landing page */
.hero {
    background: linear-gradient(120deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.05) 100%);
    color: var(--text);
    padding: 2.2rem;
    border-radius: 18px;
    border: 1px solid var(--border);
    box-shadow: 0 22px 48px rgba(0,0,0,0.22);
}
.hero h1 {
    margin-bottom: 0.35rem;
}
.hero p {
    margin-top: 0;
}
.card {
    background: #ffffff !important;
    color: #0f172a !important;
    border-radius: 14px;
    padding: 1rem;
    border: 1px solid rgba(15, 23, 42, 0.10);
    box-shadow: 0 14px 34px rgba(2, 6, 23, 0.10);
    margin-bottom: 0.9rem;
}
.card h3, .card p, .card li, .card span {
    color: #0f172a !important;
}

/* Better spacing for titles */
h1, h2, h3 {
    letter-spacing: 0.2px;
}

.glass-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 16px 36px rgba(0,0,0,0.18);
}
.muted {
    color: var(--muted);
}

/* Highlighted difference cards and score chips */
.diff-card {
    background: var(--panel-strong);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    min-height: 180px;
    box-shadow: 0 16px 36px rgba(0,0,0,0.18);
}
.score-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(14,165,233,0.14);
    border: 1px solid rgba(14,165,233,0.30);
    color: var(--text);
    font-weight: 600;
}

/* Make page-link nav look like calm pills */
a[data-testid="stPageLink-NavLink"] {
  border-radius: 999px !important;
  border: 1px solid var(--border) !important;
  background: rgba(255,255,255,0.06) !important;
}
a[data-testid="stPageLink-NavLink"]:hover {
  border-color: rgba(14,165,233,0.55) !important;
  background: rgba(255,255,255,0.09) !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_top_nav(current_step: str) -> None:
    steps = [
        ("1 Intake", "pages/1_Patient_Analysis.py"),
        ("2 Generic", "pages/2_GPT_vs_Twin.py"),
        ("3 Twin", "pages/3_Vimlesh_Twin.py"),
        ("4 Difference", "pages/4_GPT_Twin_Comparison.py"),
        ("5 Cases", "pages/5_Evidence_Panel.py"),
        ("6 Graph", "pages/7_Graph_Intelligence.py"),
        ("7 Insights", "pages/8_Comparison_Insights.py"),
        ("8 Why", "pages/9_Why_This_Recommendation.py"),
        ("9 Admin", "pages/10_Admin_Dataset.py"),
        ("10 Explainability", "pages/11_Backend_Story.py"),
    ]
    nav_cols = st.columns(len(steps), gap="small")
    for idx, (label, target) in enumerate(steps):
        with nav_cols[idx]:
            st.page_link(target, label=label, disabled=(label == current_step))


def section_card(title: str, body: str) -> None:
    st.markdown(
        f"<div class='glass-card'><h4 style='margin:0 0 .35rem 0;'>{title}</h4><div class='muted'>{body}</div></div>",
        unsafe_allow_html=True,
    )
