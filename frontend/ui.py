import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
<style>
/* App background and global text */
.stApp {
    background: radial-gradient(1200px 600px at 15% 5%, #0f2747 0%, #071224 40%, #050b17 100%);
    color: #e6edf7;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #121826 0%, #0f172a 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
section[data-testid="stSidebar"] * {
    color: #d8e3f5 !important;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 14px;
    padding: 10px 12px;
}
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] div {
    color: #e2e8f0 !important;
}

/* Data blocks and alerts */
div.stAlert, .stCodeBlock, .stDataFrame, .stTable {
    border-radius: 12px !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    border: 1px solid #2f5ea8 !important;
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    border-color: #3b82f6 !important;
    filter: brightness(1.06);
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
    background: rgba(15, 23, 42, 0.5) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(148, 163, 184, 0.35) !important;
}
details {
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 12px;
    padding: 0.2rem 0.4rem;
}

/* Custom cards from landing page */
.hero {
    background: linear-gradient(120deg, rgba(20, 42, 84, 0.95) 0%, rgba(41, 82, 152, 0.88) 100%);
    color: #f8fbff;
    padding: 2.2rem;
    border-radius: 18px;
    border: 1px solid rgba(226, 232, 240, 0.2);
    box-shadow: 0 18px 40px rgba(2, 6, 23, 0.45);
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
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.15);
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
    background: rgba(15, 23, 42, 0.58);
    border: 1px solid rgba(148, 163, 184, 0.28);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.24);
}
.muted {
    color: #b7c4db;
}

/* Highlighted difference cards and score chips */
.diff-card {
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.65) 100%);
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    min-height: 180px;
}
.score-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.2);
    border: 1px solid rgba(96, 165, 250, 0.4);
    color: #dbeafe;
    font-weight: 600;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_top_nav(current_step: str) -> None:
    steps = [
        "1 Intake",
        "2 Generic",
        "3 Twin",
        "4 Difference",
        "5 Cases",
        "6 Graph",
        "7 Insights",
        "8 Why",
        "9 Admin",
        "10 Story",
    ]
    chips = []
    for step in steps:
        if step == current_step:
            chips.append(f"<span class='nav-chip' style='padding:6px 10px;border-radius:999px;background:#1d4ed8;color:#f8fafc;font-weight:600;cursor:default'>{step}</span>")
        else:
            chips.append(f"<span class='nav-chip' style='padding:6px 10px;border-radius:999px;background:rgba(148,163,184,.22);color:#dbe7fb;cursor:default'>{step}</span>")
    st.markdown("<div style='display:flex;gap:.45rem;flex-wrap:wrap;margin:.2rem 0 1rem 0;'>" + "".join(chips) + "</div>", unsafe_allow_html=True)


def section_card(title: str, body: str) -> None:
    st.markdown(
        f"<div class='glass-card'><h4 style='margin:0 0 .35rem 0;'>{title}</h4><div class='muted'>{body}</div></div>",
        unsafe_allow_html=True,
    )
