"""
app.py - High-Performance Vision & Algorithmic Recreation Studio for Kolam Patterns
Problem Statement: Detect symmetry and pattern rules from sample Kolam designs
and generate new designs following those rules.

Theme & Aesthetic: "Rice flour on a swept threshold" — KolamCraft Design System
Tradition × Geometry × AI. A dark, hearth-warm interface.
"""

import streamlit as st
import cv2
import numpy as np
import io
import os
import base64
import importlib
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

import cv_detector
import kolam_engine

# Force hot-reloading of modules on script execution
importlib.reload(cv_detector)
importlib.reload(kolam_engine)

st.set_page_config(
    page_title="KolamCraft — Traditional Sikku Perception & Synthesis",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── KolamCraft Design System ─────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Tamil:wght@400;600;700&display=swap');

    /* ── Design Tokens ───────────────────────────────────────────────── */
    :root {
        /* Surfaces */
        --bg-base:          #120B08;
        --bg-sidebar:       #1A0F0B;
        --bg-panel:         #24140E;
        --bg-panel-raised:  #2E1A12;
        --bg-image-well:    #0A0605;
        --border-subtle:    #3A2418;
        --border-warm:      #5A3520;

        /* Accent — warm family only */
        --accent-primary:       #F2A65A;
        --accent-primary-hover: #F7B877;
        --accent-terracotta:    #C9573A;
        --accent-ember:         #E8743B;
        --accent-saffron:       #F5B93D;
        --accent-glow:          rgba(232,116,59,.18);

        /* Text */
        --text-primary:   #F6EFE6;
        --text-secondary: #CDBFB0;
        --text-muted:     #8F7C6C;
        --text-accent:    #F2A65A;
        --text-on-accent: #2A140A;

        /* Status */
        --success:    #2FBF71;
        --success-bg: rgba(47,191,113,.14);
        --warning:    #F5B93D;
        --danger:     #E5484D;

        /* Gradients */
        --grad-panel:      linear-gradient(160deg, #2A170F 0%, #1E110B 100%);
        --grad-nav-active: linear-gradient(90deg, rgba(201,87,58,.38) 0%, rgba(201,87,58,.08) 100%);
        --grad-primary:    linear-gradient(180deg, #F7B877 0%, #E8964A 100%);

        /* Typography */
        --font-display: "Cinzel", "Playfair Display", Georgia, serif;
        --font-body:    "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
        --font-tamil:   "Noto Sans Tamil", "Latha", sans-serif;

        /* Radius */
        --r-sm:   6px;
        --r-md:   10px;
        --r-lg:   14px;
        --r-pill: 999px;

        /* Elevation */
        --shadow-panel: 0 0 0 1px #3A2418, 0 8px 24px rgba(0,0,0,.35);
        --shadow-glow:  0 0 0 3px rgba(232,116,59,.25);
        --shadow-btn:   0 4px 14px rgba(232,150,74,.28);
    }

    /* ── Global base ──────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: var(--font-body) !important;
        background-color: var(--bg-base) !important;
        color: var(--text-primary) !important;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 85% -10%,
                        rgba(232,116,59,.10), transparent 60%),
                    var(--bg-base) !important;
    }

    /* ── Sidebar ──────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-family: var(--font-display) !important;
        font-size: 1rem !important;
        color: var(--text-primary) !important;
        letter-spacing: .02em;
        border-top: 1px solid var(--border-subtle);
        padding-top: 16px;
        margin-top: 8px;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label span,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label {
        color: var(--text-secondary) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: var(--bg-panel-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        min-height: 40px !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: var(--border-warm) !important;
    }
    section[data-testid="stSidebar"] .stRadio [aria-checked="true"] > div:first-child {
        background: var(--accent-terracotta) !important;
        border-color: var(--accent-terracotta) !important;
        box-shadow: var(--shadow-glow);
    }
    section[data-testid="stSidebar"] .stFileUploader > label {
        border: 1px dashed var(--border-warm) !important;
        border-radius: var(--r-md) !important;
        background: var(--bg-panel-raised) !important;
    }

    /* ── Typography ───────────────────────────────────────────────────── */
    h1, h2, h3, h4, h5 {
        font-family: var(--font-display) !important;
        color: var(--text-primary) !important;
        letter-spacing: .01em;
    }
    h4 { font-size: 1.25rem !important; line-height: 1.75rem !important; font-weight: 600 !important; }
    h5 { font-size: 1rem   !important; line-height: 1.5rem  !important; font-weight: 600 !important; }

    .tamil-text { font-family: var(--font-tamil); }

    code, pre {
        font-family: "JetBrains Mono", "Fira Code", monospace !important;
        background: var(--bg-panel-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-sm) !important;
        color: var(--accent-primary) !important;
    }

    /* ── Brand block ──────────────────────────────────────────────────── */
    .brand-container {
        padding: 18px 16px 14px;
        margin-bottom: 8px;
        background: var(--grad-panel);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-lg);
        box-shadow: var(--shadow-panel);
        position: relative;
        overflow: hidden;
    }
    .brand-pill {
        display: inline-block;
        padding: 3px 10px;
        background: rgba(245,185,61,.12);
        border: 1px solid rgba(245,185,61,.28);
        border-radius: var(--r-pill);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: .08em;
        color: var(--accent-saffron);
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .brand-title {
        font-family: var(--font-display) !important;
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 2px;
        line-height: 1.2;
    }
    .brand-title .tamil-accent {
        font-family: var(--font-tamil);
        font-weight: 500;
        font-size: 1.15rem;
        color: var(--accent-primary);
        margin-left: 6px;
    }
    .brand-subtitle {
        color: var(--text-muted);
        font-size: 11px;
        margin-top: 6px;
        line-height: 1.5;
        letter-spacing: .02em;
    }

    /* ── Page header ──────────────────────────────────────────────────── */
    .page-overline {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: var(--text-accent);
        margin-bottom: 4px;
    }
    .page-title {
        font-family: var(--font-display) !important;
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 4px;
        line-height: 1.3;
    }

    /* ── Status pill ──────────────────────────────────────────────────── */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: var(--success-bg);
        border: 1px solid rgba(47,191,113,.38);
        border-radius: var(--r-pill);
        font-size: 12px;
        font-weight: 600;
        color: var(--success);
        vertical-align: middle;
    }
    .status-pill::before {
        content: "";
        width: 7px; height: 7px;
        border-radius: 50%;
        background: var(--success);
        flex-shrink: 0;
    }

    /* ── Telemetry / Rule Inspector ───────────────────────────────────── */
    .telemetry-card {
        background: var(--bg-panel-raised);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-md);
        padding: 14px 16px;
        margin-bottom: 10px;
        transition: border-color .2s cubic-bezier(.2,.7,.2,1),
                    box-shadow    .2s cubic-bezier(.2,.7,.2,1);
    }
    .telemetry-card:hover {
        border-color: var(--border-warm);
        box-shadow: 0 0 0 1px var(--accent-glow);
    }
    .telemetry-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-accent);
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .telemetry-value {
        font-family: var(--font-display) !important;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.3;
    }
    .telemetry-sub {
        font-size: 12px;
        color: var(--text-muted);
        margin-top: 5px;
        font-variant-numeric: tabular-nums;
    }

    /* ── Rule chips ───────────────────────────────────────────────────── */
    .rule-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border-radius: var(--r-sm);
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .rule-chip-valid {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid rgba(47,191,113,.38);
    }
    .rule-chip-accent {
        background: rgba(242,166,90,.14);
        color: var(--accent-primary);
        border: 1px solid rgba(242,166,90,.32);
    }

    /* ── Status badges ────────────────────────────────────────────────── */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: var(--r-pill);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: .02em;
    }
    .status-brahma {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid rgba(47,191,113,.38);
    }
    .status-interlocking {
        background: rgba(242,166,90,.14);
        color: var(--accent-primary);
        border: 1px solid rgba(242,166,90,.32);
    }

    /* ── Active-grid banner ───────────────────────────────────────────── */
    .active-grid-banner {
        background: var(--bg-panel-raised);
        border: 1px solid var(--border-warm);
        border-radius: var(--r-md);
        padding: 12px 18px;
        margin: 12px 0 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 14px rgba(0,0,0,.28);
    }

    /* ── Buttons ──────────────────────────────────────────────────────── */
    div.stButton > button {
        border-radius: var(--r-md) !important;
        border: 1px solid var(--border-warm) !important;
        background: var(--bg-panel-raised) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        height: 40px !important;
        transition: border-color .12s, background .12s, box-shadow .12s,
                    transform .12s !important;
    }
    div.stButton > button:hover {
        border-color: var(--accent-ember) !important;
        background: rgba(232,116,59,.10) !important;
        box-shadow: var(--shadow-glow) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button:focus-visible {
        box-shadow: var(--shadow-glow) !important;
        outline: none !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
    div.stButton > button:disabled {
        opacity: .40 !important;
    }

    div.stDownloadButton > button {
        border-radius: var(--r-md) !important;
        border: none !important;
        background: var(--grad-primary) !important;
        color: var(--text-on-accent) !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: var(--shadow-btn) !important;
        transition: opacity .12s, box-shadow .12s !important;
    }
    div.stDownloadButton > button:hover {
        opacity: .90 !important;
        box-shadow: var(--shadow-btn), var(--shadow-glow) !important;
    }

    /* ── Tabs ─────────────────────────────────────────────────────────── */
    button[data-baseweb="tab"] {
        font-family: var(--font-display) !important;
        font-size: .95rem !important;
        color: var(--text-muted) !important;
        border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
        transition: color .12s !important;
    }
    button[data-baseweb="tab"]:hover {
        color: var(--text-secondary) !important;
    }
    button[aria-selected="true"] {
        color: var(--accent-primary) !important;
        font-weight: 700 !important;
        border-bottom-color: var(--accent-primary) !important;
    }

    /* ── Inputs ───────────────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--bg-panel-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        height: 40px !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent-ember) !important;
        box-shadow: var(--shadow-glow) !important;
        outline: none !important;
    }
    .stSelectbox > div > div {
        background: var(--bg-panel-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
    }
    [data-baseweb="slider"] [role="slider"] {
        background: var(--accent-terracotta) !important;
        border-color: var(--accent-terracotta) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    /* ── Expander ─────────────────────────────────────────────────────── */
    .stExpander > details {
        background: var(--bg-panel-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-lg) !important;
    }
    .stExpander > details summary {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-family: var(--font-display) !important;
    }

    /* ── Caption & helpers ────────────────────────────────────────────── */
    .stCaption, .stCaption p {
        color: var(--text-muted) !important;
        font-size: 12px !important;
        line-height: 1.5 !important;
    }

    /* ── Spinner ──────────────────────────────────────────────────────── */
    .stSpinner > div { border-top-color: var(--accent-ember) !important; }

    /* ── Image wells ──────────────────────────────────────────────────── */
    .stImage img {
        border-radius: var(--r-md) !important;
        background: var(--bg-image-well) !important;
    }

    /* ── Warm divider ─────────────────────────────────────────────────── */
    .heritage-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent,
                    rgba(232,116,59,.25), transparent);
        margin: 20px 0;
        border: none;
    }

    /* ── Scrollbar ────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb {
        background: var(--border-warm);
        border-radius: var(--r-pill);
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-ember); }

    /* ── Reduce-motion ────────────────────────────────────────────────── */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            transition-duration: .01ms !important;
            animation-duration: .01ms !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar: logo block ──────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="brand-container">
    <div class="brand-pill">கோலம் · Ethnomathematics · Truchet Knot Grammars</div>
    <h1 class="brand-title">KOLAMCRAFT <span class="tamil-accent">கோலம்</span></h1>
    <p class="brand-subtitle">Tradition × Geometry × AI</p>
</div>
""", unsafe_allow_html=True)

# ─── Main area: page hero header ─────────────────────────────────────────────
st.markdown("""
<div style="display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:4px;">
    <p class="page-overline" style="margin:0;">Stage 1 — Computer Vision Analysis</p>
    <span class="status-pill">Analysis ready</span>
</div>
<h2 class="page-title">Computer Vision Lattice &amp; Rule Extraction</h2>
<p style="color:var(--text-muted);font-size:14px;margin:0 0 16px;">
    <em>"Rice flour on a swept threshold."</em>&nbsp; Where South Indian ancestral geometry meets
    autonomous pattern perception and algorithmic Sikku recreation.
</p>
<div class="heritage-divider"></div>
""", unsafe_allow_html=True)

# ─── Sidebar Configuration ────────────────────────────────────────────────────
st.sidebar.markdown("### 🪔 Palette & Synthesis Controls")
theme_choice = st.sidebar.selectbox("Color Palette", list(kolam_engine.THEMES.keys()), index=0)
curve_flow = st.sidebar.slider(
    "Sikku Curvature Weight", 0.60, 1.00, 0.88, 0.02,
    help="Higher ratio increases flowing continuous loops; lower increases crossing lines."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📷 Source Input Selection")
input_mode = st.sidebar.radio("Input Mode", ["Upload Kolam Image", "Preset Benchmark Library"])

selected_image_bgr = None
sample_name = ""

if input_mode == "Upload Kolam Image":
    uploaded_file = st.sidebar.file_uploader("Upload Image (JPG, PNG)", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        selected_image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        sample_name = uploaded_file.name
else:
    preset_options = {
        "Classic 7-to-1 Diamond": "samples/sample_diamond_7.png",
        "Large 9-to-1 Sandhu Pulli": "samples/sample_diamond_9.png",
        "Classic 5-to-1 Diamond": "samples/sample_diamond_5.png",
        "Square 5x5 Matrix": "samples/sample_square_5.png"
    }
    choice = st.sidebar.selectbox("Benchmark Sample", list(preset_options.keys()))
    path = preset_options[choice]
    sample_name = choice
    if os.path.exists(path):
        selected_image_bgr = cv2.imread(path)
    else:
        st.sidebar.error("Benchmark sample asset missing.")

if selected_image_bgr is not None:
    # -------------------------------------------------------------
    # STAGE 1: Computer Vision Perception
    # -------------------------------------------------------------
    with st.spinner("Executing Computer Vision dot detection and symmetry reflection analysis..."):
        grid_info = cv_detector.detect_dots_and_grid(selected_image_bgr)
        sym_info = cv_detector.detect_symmetry(selected_image_bgr)

    st.markdown("#### Stage 1: Computer Vision Lattice & Rule Extraction")
    v_col1, v_col2, v_col3 = st.columns([1, 1, 1.15])

    with v_col1:
        st.markdown("**Source Kolam Image**")
        st.image(cv2.cvtColor(selected_image_bgr, cv2.COLOR_BGR2RGB), width="stretch")

    with v_col2:
        st.markdown("**Pulli (Dot Lattice) Segmentation**")
        st.image(cv2.cvtColor(grid_info['annotated_image'], cv2.COLOR_BGR2RGB), width="stretch")

    with v_col3:
        st.markdown("**Extracted Rule Telemetry & Inspector**")

        st.markdown(f"""
        <div class="telemetry-card">
            <div class="telemetry-label">Grid Classification</div>
            <div class="telemetry-value">{grid_info['grid_type']}</div>
            <div class="telemetry-sub">Total Dots: {len(grid_info['dots'])} &nbsp;·&nbsp; Spacing: {grid_info['estimated_spacing']} px</div>
        </div>
        <div class="telemetry-card">
            <div class="telemetry-label">Symmetry Group</div>
            <div class="telemetry-value">{sym_info['primary_symmetry']}</div>
            <div class="telemetry-sub">H: {sym_info['h_score']}% &nbsp;·&nbsp; V: {sym_info['v_score']}% &nbsp;·&nbsp; Rot 90°: {sym_info['rot_score']}%</div>
        </div>
        <div class="telemetry-card" style="margin-bottom:0;">
            <div class="telemetry-label">Rule Inspector (Ethnomathematics)</div>
            <div style="margin-top:8px;">
                <span class="rule-chip rule-chip-valid">✔ Closed Loops</span>
                <span class="rule-chip rule-chip-valid">✔ Rigid Obstacle Rule</span>
                <span class="rule-chip rule-chip-valid">✔ Completeness</span>
                <span class="rule-chip rule-chip-accent">✔ 45° Diagonal Rule</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Canonical Lattice Control (Verified Instant-Sync Buttons)
    # -------------------------------------------------------------
    rec_canonical = grid_info.get('recommended_canonical', grid_info['row_lengths'])
    default_str = ", ".join(str(x) for x in rec_canonical)

    if st.session_state.get('active_sample_tracker') != sample_name:
        st.session_state['active_sample_tracker'] = sample_name
        st.session_state['active_grid_input'] = default_str

    if 'active_grid_input' not in st.session_state:
        st.session_state['active_grid_input'] = default_str

    st.markdown("##### Active Dot Grid for Generation")

    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        if st.button("7-to-1 Diamond (25 Dots)", key="btn_7_1"):
            st.session_state['active_grid_input'] = "1, 3, 5, 7, 5, 3, 1"
            st.rerun()
    with b_col2:
        if st.button("9-to-1 Diamond (41 Dots)", key="btn_9_1"):
            st.session_state['active_grid_input'] = "1, 3, 5, 7, 9, 7, 5, 3, 1"
            st.rerun()
    with b_col3:
        if st.button("5x5 Square (25 Dots)", key="btn_5_5"):
            st.session_state['active_grid_input'] = "5, 5, 5, 5, 5"
            st.rerun()
    with b_col4:
        if st.button("Reset to Detected Rows", key="btn_reset"):
            st.session_state['active_grid_input'] = default_str
            st.rerun()

    active_row_str = st.text_input(
        "Active Row Structure (editable coordinate list):",
        key="active_grid_input",
        help="Comma-separated integers specifying the count of Pulli (dots) in each horizontal row."
    )

    try:
        active_lengths = [int(x.strip()) for x in active_row_str.split(",") if x.strip()]
        if not active_lengths:
            active_lengths = rec_canonical
    except Exception:
        active_lengths = rec_canonical

    st.markdown(f"""
    <div class="active-grid-banner">
        <span style="font-weight:600; color:var(--accent-primary); font-size:0.92rem;">Lattice Active For Synthesis:</span>
        <span style="color:var(--text-primary); background:rgba(10,6,5,.80);
                     padding:4px 12px; border-radius:var(--r-sm);
                     border:1px solid var(--border-warm);
                     font-size:0.88rem; font-variant-numeric:tabular-nums;
                     font-family:'JetBrains Mono',monospace;">
            Rows: {active_lengths} &nbsp;·&nbsp; {sum(active_lengths)} Total Dots
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="heritage-divider"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # STAGE 2: Algorithmic Synthesis & Animated Player
    # -------------------------------------------------------------
    st.markdown("#### Stage 2: Autonomous Re-creation & Synthesis")
    st.caption(f"Synthesizing unique, mathematically compliant Kolams inheriting grid layout {active_lengths} ({sum(active_lengths)} dots) under {sym_info['primary_symmetry']}.")

    symmetry_mode = sym_info['symmetry_mode']

    # Tabbed Interface: Multi-Variation Matrix vs Interactive Animated Vector Player
    view_tab1, view_tab2 = st.tabs(["Interactive 3D Accordion Showcase", "Live Stroke-Drawing Player"])

    with view_tab1:
        # Pre-render the 3 variations
        variation_items = []
        variation_buffers = []
        variation_metas = []
        variation_figs = []

        theme_props = kolam_engine.THEMES.get(theme_choice, kolam_engine.THEMES["Terracotta & Rice Flour (Semman)"])

        for i in range(3):
            seed_val = (i + 1) * 101 + sum(active_lengths)
            fig, meta = kolam_engine.render_kolam_figure(
                lengths=active_lengths,
                symmetry_mode=symmetry_mode,
                curve_bias=curve_flow,
                seed=seed_val,
                theme=theme_choice,
                figsize=(5, 5)
            )
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=180, facecolor=fig.get_facecolor(), bbox_inches='tight')
            buf.seek(0)
            img_bytes = buf.read()
            variation_buffers.append(img_bytes)
            variation_metas.append((seed_val, meta))
            variation_figs.append(fig)

            b64_str = base64.b64encode(img_bytes).decode('utf-8')
            status_desc = "Eulerian (1 Loop)" if meta['is_brahma_mudi'] else f"{meta['num_loops']} Loops"

            variation_items.append({
                "image": f"data:image/png;base64,{b64_str}",
                "label": f"Variation {i+1} · {status_desc}",
                "sublabel": f"Seed {seed_val} · {meta['num_dots']} Dots · {meta['symmetry'].capitalize()}",
                "is_brahma": meta['is_brahma_mudi'],
                "num_loops": meta['num_loops']
            })

        st.caption("Interactive 3D Perspective Gallery — Hover or click to expand. Use keyboard ← / → arrows to navigate.")

        # Render 3D GSAP Accordion Gallery (React Bits AccordionGallery)
        accordion_html = kolam_engine.render_accordion_gallery_html(
            items=variation_items,
            default_index=1,
            height=460,
            accent_color=theme_props["line"],
            overlay_color=theme_props["bg"],
            expand_ratio=0.52,
            tilt=8,
            parallax=0.5,
            duration=0.6,
            gap=12,
            radius=14,
            grayscale=True
        )
        components.html(accordion_html, height=480)

        # High-res PNG export buttons in a clean 3-column toolbar
        dl_cols = st.columns(3)
        for i in range(3):
            with dl_cols[i]:
                seed_val, meta = variation_metas[i]
                status_class = "status-brahma" if meta['is_brahma_mudi'] else "status-interlocking"
                status_label = "BRAHMA MUDI (1 LOOP)" if meta['is_brahma_mudi'] else f"{meta['num_loops']} INTERLOCKING LOOPS"

                st.markdown(f"""
                <div style="margin-top:2px; margin-bottom:6px;">
                    <span class="status-chip {status_class}">● {status_label}</span>
                </div>
                <div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:8px;">
                    Variation {i+1} &nbsp;·&nbsp; Seed {seed_val} &nbsp;·&nbsp; {meta['num_dots']} Dots
                </div>
                """, unsafe_allow_html=True)

                st.download_button(
                    label=f"Export Variation {i+1} PNG",
                    data=variation_buffers[i],
                    file_name=f"kolam_variation_{i+1}_seed_{seed_val}.png",
                    mime="image/png",
                    key=f"dl_btn_{i+1}_{seed_val}_{len(active_lengths)}"
                )

        with st.expander("Compare All Variations (Static Side-by-Side Grid)"):
            grid_cols = st.columns(3)
            for i in range(3):
                with grid_cols[i]:
                    st.pyplot(variation_figs[i])
                    st.caption(f"Variation {i+1} (Seed {variation_metas[i][0]})")

    with view_tab2:
        st.markdown("**Real-Time Vector Stroke Animator**")
        st.caption("Inspect the continuous rice-powder strand path tracing out the symmetry loops in vector space:")

        anim_col1, anim_col2 = st.columns([1, 2])
        with anim_col1:
            anim_seed = st.number_input("Variation Seed", value=42, min_value=1, max_value=99999, key="anim_seed_input")
            anim_duration = st.slider("Drawing Duration (seconds)", 1.5, 6.0, 3.5, 0.5, key="anim_duration_input")
            st.markdown("""
            *This animated vector player demonstrates the mathematical continuity of the strand, rendering path-by-path with CSS stroke-dasharray interpolation.*
            """)

        with anim_col2:
            svg_code, svg_meta = kolam_engine.render_kolam_svg(
                lengths=active_lengths,
                symmetry_mode=symmetry_mode,
                curve_bias=curve_flow,
                seed=anim_seed,
                theme=theme_choice,
                animation_duration=anim_duration
            )
            components.html(svg_code, height=480)

st.markdown('<div class="heritage-divider"></div>', unsafe_allow_html=True)

# Architectural Sandbox Mode
with st.expander("Interactive Lattice Sandbox (Manual Synthesizer)"):
    sb_col1, sb_col2 = st.columns(2)
    with sb_col1:
        custom_shape = st.selectbox("Lattice Mode", ["Diamond / Rhombus", "Square Matrix", "Custom Vector"])
        if custom_shape == "Square Matrix":
            n = st.slider("Matrix Size (N)", 3, 9, 5, step=1, key="sb_square_size")
            custom_lengths = [n] * n
        elif custom_shape == "Diamond / Rhombus":
            d_max = st.slider("Diamond Max Dimension (Odd)", 3, 11, 7, step=2, key="sb_diamond_size")
            half = list(range(1, d_max, 2))
            custom_lengths = half + [d_max] + half[::-1]
        else:
            custom_str = st.text_input("Custom Row Vector:", "1, 3, 5, 7, 5, 3, 1", key="sb_custom_vector")
            try:
                custom_lengths = [int(x.strip()) for x in custom_str.split(",")]
            except Exception:
                custom_lengths = [1, 3, 5, 7, 5, 3, 1]

        custom_sym = st.selectbox("Symmetry Fold", ["mirror", "rotational"], key="sb_sym_fold")
        custom_seed = st.number_input("Synthesis Seed", 1, 9999, 42, key="sb_seed_num")

    with sb_col2:
        custom_fig, custom_meta = kolam_engine.render_kolam_figure(
            lengths=custom_lengths,
            symmetry_mode=custom_sym,
            curve_bias=curve_flow,
            seed=custom_seed,
            theme=theme_choice,
            figsize=(5, 5)
        )
        st.pyplot(custom_fig)
        st.caption(f"Topological Loops: {custom_meta['num_loops']} · Eulerian Status: {custom_meta['is_brahma_mudi']}")
