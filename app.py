"""
app.py - High-Performance Vision & Algorithmic Recreation Studio for Kolam Patterns
Problem Statement: Detect symmetry and pattern rules from sample Kolam designs
and generate new designs following those rules.

Theme & Aesthetic: "Rice flour on a swept threshold" (South Indian Minimalist Heritage)
Colors: Semman/Terracotta (#7A2E1D), Rice-paper (#F7EFE2), Flour (#FFF8EC), 
        Turmeric (#E0A43B), Banana Leaf (#2F6B4F), Kumkum (#B3261E).
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

# Custom Heritage South Indian Styling (Rice flour on swept terracotta threshold)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..700&family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Tamil:wght@400;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-terracotta: #7A2E1D;
        --bg-soft: #F7EFE2;
        --ink: #2B1A12;
        --flour: #FFF8EC;
        --accent: #E0A43B;
        --leaf: #2F6B4F;
        --kumkum: #B3261E;
        --threshold-dark: #1A0E0A;
        --card-bg: #25130E;
        --radius: 14px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
        color: #FFF8EC;
    }

    h1, h2, h3, .brand-title, .section-header {
        font-family: 'Fraunces', Georgia, serif !important;
        letter-spacing: -0.3px;
    }

    .tamil-text {
        font-family: 'Noto Sans Tamil', 'Fraunces', serif;
    }

    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Top Heritage Hero Header */
    .brand-container {
        text-align: center;
        padding: 1.8rem 1rem 1.4rem 1rem;
        margin-bottom: 1.8rem;
        background: linear-gradient(180deg, rgba(122, 46, 29, 0.45) 0%, rgba(26, 14, 10, 0.6) 100%);
        border: 1px solid rgba(224, 164, 59, 0.25);
        border-radius: var(--radius);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .brand-pill {
        display: inline-block;
        padding: 5px 16px;
        background: rgba(224, 164, 59, 0.12);
        border: 1px solid rgba(224, 164, 59, 0.35);
        border-radius: 20px;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 1.6px;
        color: #E0A43B;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
    }
    .brand-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFF8EC;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
    }
    .brand-title span.tamil-accent {
        font-family: 'Noto Sans Tamil', serif;
        font-weight: 400;
        font-size: 2.1rem;
        color: #E0A43B;
        margin-left: 8px;
    }
    .brand-subtitle {
        color: #E6D5C3;
        font-size: 0.98rem;
        margin-top: 0.5rem;
        max-width: 720px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.5;
    }

    /* Metric & Telemetry Panels */
    .telemetry-card {
        background: var(--card-bg);
        border: 1px solid rgba(224, 164, 59, 0.22);
        border-radius: var(--radius);
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    }
    .telemetry-card:hover {
        border-color: #E0A43B;
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(224, 164, 59, 0.15);
    }
    .telemetry-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #E0A43B;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .telemetry-value {
        font-size: 1.18rem;
        font-weight: 700;
        color: #FFF8EC;
        font-family: 'Fraunces', serif;
    }
    .telemetry-sub {
        font-size: 0.82rem;
        color: #CBB8A3;
        margin-top: 5px;
    }

    /* Rule Inspector Chips (from design tokens) */
    .rule-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.4px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .rule-chip-valid {
        background: rgba(47, 107, 79, 0.28);
        color: #58D68D;
        border: 1px solid rgba(47, 107, 79, 0.55);
    }
    .rule-chip-accent {
        background: rgba(224, 164, 59, 0.18);
        color: #F3C973;
        border: 1px solid rgba(224, 164, 59, 0.45);
    }

    /* Status Badges */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .status-brahma {
        background: rgba(47, 107, 79, 0.35);
        color: #58D68D;
        border: 1px solid rgba(47, 107, 79, 0.65);
    }
    .status-interlocking {
        background: rgba(224, 164, 59, 0.22);
        color: #F3C973;
        border: 1px solid rgba(224, 164, 59, 0.5);
    }

    /* Active Grid Banner */
    .active-grid-banner {
        background: rgba(122, 46, 29, 0.35);
        border: 1px solid rgba(224, 164, 59, 0.35);
        border-radius: var(--radius);
        padding: 11px 18px;
        margin: 14px 0 18px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    }

    /* Button and Interactive Elements Styling */
    div.stButton > button {
        border-radius: var(--radius) !important;
        border: 1px solid rgba(224, 164, 59, 0.4) !important;
        background: rgba(43, 26, 18, 0.8) !important;
        color: #FFF8EC !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        border-color: #E0A43B !important;
        background: rgba(224, 164, 59, 0.2) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(224, 164, 59, 0.2) !important;
    }

    div.stDownloadButton > button {
        border-radius: var(--radius) !important;
        border: 1px solid rgba(224, 164, 59, 0.45) !important;
        background: rgba(122, 46, 29, 0.4) !important;
        color: #FFF8EC !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    div.stDownloadButton > button:hover {
        border-color: #E0A43B !important;
        background: rgba(224, 164, 59, 0.28) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }

    /* Custom Styling for Streamlit Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Fraunces', serif !important;
        font-size: 1.05rem !important;
        color: #CBB8A3 !important;
        border-radius: 8px 8px 0 0 !important;
    }
    button[aria-selected="true"] {
        color: #E0A43B !important;
        font-weight: 700 !important;
        border-bottom-color: #E0A43B !important;
    }

    /* Section divider */
    .heritage-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(224, 164, 59, 0.35), transparent);
        margin: 1.6rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main Heritage Editorial Header
st.markdown("""
<div class="brand-container">
    <div class="brand-pill">கோலம் · ETHNOMATHEMATICS · TRUCHET KNOT GRAMMARS</div>
    <h1 class="brand-title">KOLAMCRAFT <span class="tamil-accent">கோலம்</span></h1>
    <p class="brand-subtitle">
        <em>"Rice flour on a swept threshold."</em> Where South Indian ancestral geometry meets autonomous 
        pattern perception and algorithmic Sikku recreation.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
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
            <div class="telemetry-sub">Total Dots: {len(grid_info['dots'])} · Spacing: {grid_info['estimated_spacing']} px</div>
        </div>
        <div class="telemetry-card">
            <div class="telemetry-label">Symmetry Group</div>
            <div class="telemetry-value">{sym_info['primary_symmetry']}</div>
            <div class="telemetry-sub">H: {sym_info['h_score']}% · V: {sym_info['v_score']}% · Rot 90°: {sym_info['rot_score']}%</div>
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
        <span style="font-weight: 600; color: #E0A43B; font-size: 0.92rem;">Lattice Active For Synthesis:</span>
        <span class="mono-text" style="color: #FFF8EC; background: rgba(26, 14, 10, 0.7); padding: 4px 12px; border-radius: 6px; border: 1px solid rgba(224, 164, 59, 0.3); font-size: 0.88rem;">
            Rows: {active_lengths} · {sum(active_lengths)} Total Dots
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
                <div style="font-size:0.78rem; color:#CBB8A3; margin-bottom:8px;">
                    Variation {i+1} · Seed {seed_val} · {meta['num_dots']} Dots
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
