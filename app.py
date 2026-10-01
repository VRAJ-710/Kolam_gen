"""
app.py - High-Performance Vision & Algorithmic Recreation Studio for Kolam Patterns
Problem Statement: Detect symmetry and pattern rules from sample Kolam designs
and generate new designs following those rules.
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
    page_title="Kolamify Studio - Pattern Perception & Synthesis",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Architectural Styling (Sleek Obsidian & Warm Gold - Zero Generic AI Tropes)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Styles */
    .brand-container {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #1E2530;
    }
    .brand-pill {
        display: inline-block;
        padding: 4px 14px;
        background: rgba(212, 175, 55, 0.1);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        color: #D4AF37;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .brand-subtitle {
        color: #8B949E;
        font-size: 0.95rem;
        margin-top: 0.4rem;
    }

    /* Metric & Telemetry Panels */
    .telemetry-card {
        background: #141820;
        border: 1px solid #212836;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .telemetry-card:hover {
        border-color: #D4AF37;
        transform: translateY(-1px);
    }
    .telemetry-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #8B949E;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .telemetry-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F0F6FC;
    }
    .telemetry-sub {
        font-size: 0.8rem;
        color: #6E7681;
        margin-top: 4px;
    }

    /* Status Badges */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .status-brahma {
        background: rgba(46, 160, 67, 0.15);
        color: #3FB950;
        border: 1px solid rgba(46, 160, 67, 0.3);
    }
    .status-interlocking {
        background: rgba(56, 139, 253, 0.15);
        color: #58A6FF;
        border: 1px solid rgba(56, 139, 253, 0.3);
    }

    /* Radar scan pulse animation */
    @keyframes radarSweep {
        0% { transform: translateY(-100%); opacity: 0; }
        50% { opacity: 0.5; }
        100% { transform: translateY(100%); opacity: 0; }
    }
    .scan-container {
        position: relative;
        overflow: hidden;
        border-radius: 8px;
    }
    .scan-bar {
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, transparent, #D4AF37, transparent);
        animation: radarSweep 2.5s infinite linear;
    }
</style>
""", unsafe_allow_html=True)

# Main Editorial Header
st.markdown("""
<div class="brand-container">
    <div class="brand-pill">Computer Vision · Knot Grammars · Topology</div>
    <h1 class="brand-title">KOLAMIFY ARCHITECTURE</h1>
    <p class="brand-subtitle">Autonomous Heritage Pattern Recognition & Algorithmic Sikku Recreation</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown("### Palette & Synthesis Controls")
theme_choice = st.sidebar.selectbox("Color Palette", list(kolam_engine.THEMES.keys()), index=0)
curve_flow = st.sidebar.slider(
    "Sikku Curvature Weight", 0.60, 1.00, 0.88, 0.02,
    help="Higher ratio increases flowing continuous loops; lower increases crossing lines."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Source Input Selection")
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
    v_col1, v_col2, v_col3 = st.columns([1, 1, 1.1])

    with v_col1:
        st.markdown("**Source Kolam Image**")
        st.image(cv2.cvtColor(selected_image_bgr, cv2.COLOR_BGR2RGB), width="stretch")

    with v_col2:
        st.markdown("**Pulli (Dot Lattice) Segmentation**")
        st.image(cv2.cvtColor(grid_info['annotated_image'], cv2.COLOR_BGR2RGB), width="stretch")

    with v_col3:
        st.markdown("**Extracted Rule Telemetry**")
        
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
    <div style="background: rgba(212, 175, 55, 0.08); border: 1px solid rgba(212, 175, 55, 0.25); border-radius: 8px; padding: 10px 16px; margin: 12px 0 16px 0; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; color: #D4AF37;">Lattice Active For Synthesis:</span>
        <span style="font-family: monospace; color: #F0F6FC; background: #0D1117; padding: 3px 10px; border-radius: 4px; border: 1px solid #30363D;">Rows: {active_lengths} · {sum(active_lengths)} Total Dots</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

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

        theme_props = kolam_engine.THEMES.get(theme_choice, kolam_engine.THEMES["Traditional Rice Powder"])

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
            radius=16,
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
                <div style="font-size:0.78rem; color:#8B949E; margin-bottom:8px;">
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
            *This animated vector player demonstrates the mathematical continuity of the strand, rendering path-by-path with CSS stroke interpolation.*
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

st.markdown("---")
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
