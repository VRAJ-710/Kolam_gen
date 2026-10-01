"""
kolam_engine.py - Core Generative Engine for Sikku Kolams
Renders mathematically valid, highly aesthetic, traditional Kolam patterns.
Uses weighted Truchet knot theory, symmetry folding, and loop graph analysis.
"""

import math
import random
import io
import base64
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SPACING = 60
RADIUS = SPACING / 2

THEMES = {
    "Traditional Rice Powder": {"bg": "#211510", "line": "#fffbf0", "dot": "#ffffff", "glow": "#ffecd1"},
    "Temple Saffron & Gold": {"bg": "#1c0b1e", "line": "#f6c344", "dot": "#ffffff", "glow": "#ffd166"},
    "Midnight Indigo": {"bg": "#121629", "line": "#e2c044", "dot": "#ffffff", "glow": "#f4d35e"},
    "Terracotta Dawn": {"bg": "#2e1511", "line": "#f7ede2", "dot": "#ffffff", "glow": "#f5cac3"}
}

def create_dots(lengths):
    """
    Takes a list of row lengths and centers them into a coordinate set.
    """
    dots = set()
    W = max(lengths)
    H = len(lengths)
    for y, length in enumerate(reversed(lengths)):
        offset = (W - length) // 2
        for x in range(length):
            dots.add((offset + x, y))
    return dots, W, H

def get_grid_point(x, y, W, H, spacing=SPACING):
    """Centered Cartesian coordinates."""
    offset_x = (W - 1) * spacing / 2.0
    offset_y = (H - 1) * spacing / 2.0
    return (x * spacing - offset_x, y * spacing - offset_y)

def generate_tile_matrix(W, H, symmetry_mode="mirror", curve_bias=0.88, seed=None):
    """
    Generates tile matrix with curve dominance for authentic flowing Sikku aesthetics.
    curve_bias: fraction of cells assigned to smooth looping arcs (A, B) vs crosses (C).
    """
    if seed is not None:
        random.seed(seed)

    num_cells_x = W + 1
    num_cells_y = H + 1

    # In authentic Sikku Kolam, loops/arcs dominate (>85%) to produce flowing lotus petals
    # Straight crosses (C) occur sparingly as bridge intersections.
    p_arc = curve_bias / 2.0
    p_cross = 1.0 - curve_bias
    choices = ["A", "B", "C"]
    weights = [p_arc, p_arc, p_cross]

    raw_matrix = [
        [random.choices(choices, weights=weights)[0] for _ in range(num_cells_y)]
        for _ in range(num_cells_x)
    ]

    cell_orientations = {}

    for cx in range(num_cells_x):
        for cy in range(num_cells_y):
            mx = num_cells_x - 1 - cx
            my = num_cells_y - 1 - cy

            rx, flipped_h = (cx, False) if cx <= mx else (mx, True)
            ry, flipped_v = (cy, False) if cy <= my else (my, True)

            ori = raw_matrix[rx][ry]

            if symmetry_mode in ("mirror", "rotational"):
                # Bilateral reflection across axes
                if flipped_h != flipped_v:
                    if ori == "A": ori = "B"
                    elif ori == "B": ori = "A"

            cell_orientations[(cx, cy)] = ori

    return cell_orientations

def analyze_loops(W, H, dots, cell_orientations):
    """
    Graph analysis to count closed loops in the generated Kolam.
    Returns: (num_loops, is_brahma_mudi)
    """
    adj = {}

    def add_edge(p1, p2):
        adj.setdefault(p1, []).append(p2)
        adj.setdefault(p2, []).append(p1)

    for i in range(-1, W):
        for j in range(-1, H):
            cell_dots = {
                'bl': (i, j), 'br': (i + 1, j),
                'tl': (i, j + 1), 'tr': (i + 1, j + 1)
            }
            existing_dots = {k: v for k, v in cell_dots.items() if v in dots}
            count = len(existing_dots)
            if count == 0:
                continue

            mb = (i + 0.5, j)
            mt = (i + 0.5, j + 1)
            ml = (i, j + 0.5)
            mr = (i + 1, j + 0.5)

            if count == 4:
                cell_x, cell_y = i + 1, j + 1
                ori = cell_orientations.get((cell_x, cell_y), "A")
                if ori == "C":
                    add_edge(ml, mr)
                    add_edge(mb, mt)
                elif ori == "A":
                    add_edge(ml, mt)
                    add_edge(mr, mb)
                elif ori == "B":
                    add_edge(mb, ml)
                    add_edge(mt, mr)
            else:
                for arc in existing_dots.keys():
                    if arc == 'bl': add_edge(mb, ml)
                    elif arc == 'br': add_edge(mr, mb)
                    elif arc == 'tr': add_edge(mt, mr)
                    elif arc == 'tl': add_edge(ml, mt)

    visited = set()
    num_loops = 0
    for node in adj:
        if node not in visited:
            num_loops += 1
            queue = [node]
            visited.add(node)
            while queue:
                curr = queue.pop(0)
                for neighbor in adj.get(curr, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

    is_brahma_mudi = (num_loops == 1)
    return num_loops, is_brahma_mudi

def render_kolam_figure(lengths, symmetry_mode="mirror", curve_bias=0.88, seed=None,
                        figsize=(6, 6), theme="Traditional Rice Powder"):
    """
    Renders an aesthetically superior, mathematically authentic Sikku Kolam.
    """
    dots, W, H = create_dots(lengths)
    cell_orientations = generate_tile_matrix(W, H, symmetry_mode=symmetry_mode,
                                             curve_bias=curve_bias, seed=seed)
    num_loops, is_brahma_mudi = analyze_loops(W, H, dots, cell_orientations)

    colors = THEMES.get(theme, THEMES["Traditional Rice Powder"])
    bg_color = colors["bg"]
    line_color = colors["line"]
    dot_color = colors["dot"]

    fig, ax = plt.subplots(figsize=figsize, facecolor=bg_color)
    ax.set_facecolor(bg_color)
    ax.set_aspect('equal')
    ax.axis('off')

    line_width = 3.2

    # Draw Pulli (Dots)
    for x, y in dots:
        px, py = get_grid_point(x, y, W, H)
        ax.scatter([px], [py], s=40, color=dot_color, edgecolors=(1.0, 1.0, 1.0, 0.4),
                   linewidths=1.5, zorder=6)

    def draw_arc(center, start_angle, end_angle):
        arc = patches.Arc(center, 2 * RADIUS, 2 * RADIUS,
                          angle=0, theta1=start_angle, theta2=end_angle,
                          color=line_color, lw=line_width, capstyle='round', zorder=3)
        ax.add_patch(arc)

    def draw_line(p1, p2):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=line_color,
                lw=line_width, solid_capstyle='round', zorder=3)

    for i in range(-1, W):
        for j in range(-1, H):
            cell_dots = {
                'bl': (i, j), 'br': (i + 1, j),
                'tl': (i, j + 1), 'tr': (i + 1, j + 1)
            }
            existing_dots = {k: v for k, v in cell_dots.items() if v in dots}
            count = len(existing_dots)
            if count == 0:
                continue

            mb = get_grid_point(i + 0.5, j, W, H)
            mt = get_grid_point(i + 0.5, j + 1, W, H)
            ml = get_grid_point(i, j + 0.5, W, H)
            mr = get_grid_point(i + 1, j + 0.5, W, H)

            if count == 4:
                cell_x, cell_y = i + 1, j + 1
                ori = cell_orientations.get((cell_x, cell_y), "A")

                if ori == "C":
                    draw_line(ml, mr)
                    draw_line(mb, mt)
                else:
                    arcs_to_draw = ['tl', 'br'] if ori == 'A' else ['tr', 'bl']
                    for arc in arcs_to_draw:
                        dot_pos = cell_dots[arc]
                        c = get_grid_point(dot_pos[0], dot_pos[1], W, H)
                        if arc == 'br': draw_arc(c, 90, 180)
                        elif arc == 'tl': draw_arc(c, 270, 360)
                        elif arc == 'bl': draw_arc(c, 0, 90)
                        elif arc == 'tr': draw_arc(c, 180, 270)
            else:
                for arc in existing_dots.keys():
                    dot_pos = cell_dots[arc]
                    c = get_grid_point(dot_pos[0], dot_pos[1], W, H)
                    if arc == 'bl': draw_arc(c, 0, 90)
                    elif arc == 'br': draw_arc(c, 90, 180)
                    elif arc == 'tr': draw_arc(c, 180, 270)
                    elif arc == 'tl': draw_arc(c, 270, 360)

    # Margin bounds
    span = (max(W, H) + 1.2) * SPACING / 2.0
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)
    plt.tight_layout()

    metadata = {
        "num_dots": len(dots),
        "grid_shape": f"{W}x{H}",
        "row_lengths": lengths,
        "symmetry": symmetry_mode,
        "num_loops": num_loops,
        "is_brahma_mudi": is_brahma_mudi,
        "seed": seed
    }
    return fig, metadata


def render_kolam_svg(lengths, symmetry_mode="mirror", curve_bias=0.88, seed=None,
                     theme="Traditional Rice Powder", animation_duration=3.5):
    """
    Renders an interactive, self-drawing animated SVG vector Kolam.
    Uses CSS stroke-dashoffset animation for real-time stroke drawing effects.
    """
    dots, W, H = create_dots(lengths)
    cell_orientations = generate_tile_matrix(W, H, symmetry_mode=symmetry_mode,
                                             curve_bias=curve_bias, seed=seed)
    num_loops, is_brahma_mudi = analyze_loops(W, H, dots, cell_orientations)

    colors = THEMES.get(theme, THEMES["Traditional Rice Powder"])
    bg_color = colors["bg"]
    line_color = colors["line"]
    dot_color = colors["dot"]

    spacing = SPACING
    radius = RADIUS
    pad = 40
    box_w = (W + 1) * spacing + pad * 2
    box_h = (H + 1) * spacing + pad * 2
    cx_offset = box_w / 2.0
    cy_offset = box_h / 2.0

    def pt(gx, gy):
        ox = (W - 1) * spacing / 2.0
        oy = (H - 1) * spacing / 2.0
        return (gx * spacing - ox + cx_offset, -(gy * spacing - oy) + cy_offset)

    path_cmds = []

    def add_arc(c, s_deg, e_deg):
        sx = c[0] + radius * math.cos(math.radians(s_deg))
        sy = c[1] - radius * math.sin(math.radians(s_deg))
        ex = c[0] + radius * math.cos(math.radians(e_deg))
        ey = c[1] - radius * math.sin(math.radians(e_deg))
        path_cmds.append(f"M {sx:.1f} {sy:.1f} A {radius:.1f} {radius:.1f} 0 0 0 {ex:.1f} {ey:.1f}")

    def add_line(p1, p2):
        path_cmds.append(f"M {p1[0]:.1f} {p1[1]:.1f} L {p2[0]:.1f} {p2[1]:.1f}")

    for i in range(-1, W):
        for j in range(-1, H):
            cell_dots = {
                'bl': (i, j), 'br': (i + 1, j),
                'tl': (i, j + 1), 'tr': (i + 1, j + 1)
            }
            existing = {k: v for k, v in cell_dots.items() if v in dots}
            count = len(existing)
            if count == 0:
                continue

            mb = pt(i + 0.5, j)
            mt = pt(i + 0.5, j + 1)
            ml = pt(i, j + 0.5)
            mr = pt(i + 1, j + 0.5)

            if count == 4:
                cell_x, cell_y = i + 1, j + 1
                ori = cell_orientations.get((cell_x, cell_y), "A")
                if ori == "C":
                    add_line(ml, mr)
                    add_line(mb, mt)
                else:
                    arcs = ['tl', 'br'] if ori == 'A' else ['tr', 'bl']
                    for a in arcs:
                        c = pt(cell_dots[a][0], cell_dots[a][1])
                        if a == 'br': add_arc(c, 90, 180)
                        elif a == 'tl': add_arc(c, 270, 360)
                        elif a == 'bl': add_arc(c, 0, 90)
                        elif a == 'tr': add_arc(c, 180, 270)
            else:
                for a in existing.keys():
                    c = pt(cell_dots[a][0], cell_dots[a][1])
                    if a == 'bl': add_arc(c, 0, 90)
                    elif a == 'br': add_arc(c, 90, 180)
                    elif a == 'tr': add_arc(c, 180, 270)
                    elif a == 'tl': add_arc(c, 270, 360)

    combined_path = " ".join(path_cmds)
    unique_id = f"k_{abs(hash(seed or 42)) % 100000}"

    svg = f'''<svg id="{unique_id}" viewBox="0 0 {box_w:.1f} {box_h:.1f}" xmlns="http://www.w3.org/2000/svg" style="background:{bg_color}; border-radius:10px; width:100%; height:auto; display:block;">
<defs>
    <filter id="glow_{unique_id}" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="1.2" result="blur" />
        <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
        </feMerge>
    </filter>
</defs>
<style>
    @keyframes drawPath_{unique_id} {{
        from {{ stroke-dashoffset: 7000; }}
        to {{ stroke-dashoffset: 0; }}
    }}
    .path_{unique_id} {{
        stroke: {line_color};
        stroke-width: 3.5;
        stroke-linecap: round;
        stroke-linejoin: round;
        fill: none;
        stroke-dasharray: 7000;
        stroke-dashoffset: 0;
        animation: drawPath_{unique_id} {animation_duration}s cubic-bezier(0.4, 0.0, 0.2, 1) forwards;
        filter: url(#glow_{unique_id});
    }}
    .dot_{unique_id} {{
        fill: {dot_color};
        stroke: rgba(255,255,255,0.4);
        stroke-width: 1.5;
    }}
</style>
'''
    # Render dots
    for x, y in dots:
        d = pt(x, y)
        svg += f'<circle cx="{d[0]:.1f}" cy="{d[1]:.1f}" r="4.0" class="dot_{unique_id}" />\n'

    svg += f'<path d="{combined_path}" class="path_{unique_id}" />\n'
    svg += '</svg>'

    metadata = {
        "num_dots": len(dots),
        "grid_shape": f"{W}x{H}",
        "row_lengths": lengths,
        "symmetry": symmetry_mode,
        "num_loops": num_loops,
        "is_brahma_mudi": is_brahma_mudi,
        "seed": seed
    }
    return svg, metadata

def render_accordion_gallery_html(
    items,
    default_index=1,
    height=460,
    accent_color="#D4AF37",
    overlay_color="#080B10",
    text_color="#FFFFFF",
    expand_ratio=0.52,
    tilt=8,
    parallax=0.5,
    duration=0.6,
    gap=12,
    radius=16,
    grayscale=True
):
    """
    Renders an interactive 3D GSAP Accordion Gallery (React Bits AccordionGallery component).
    items: list of dicts with keys:
        - image: data URI (data:image/png;base64,...)
        - label: string (e.g. 'Variation 1')
        - sublabel: string (e.g. 'Seed 142 · 25 Dots')
        - is_brahma: bool
        - num_loops: int
    """
    items_json = json.dumps(items)
    gray_val = 0.65 if grayscale else 0.0

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    color: {text_color};
    overflow: hidden;
    user-select: none;
    -webkit-font-smoothing: antialiased;
  }}

  .accordion-gallery {{
    --ag-accent: {accent_color};
    --ag-overlay: {overlay_color};
    --ag-text: {text_color};
    --ag-gap: {gap}px;
    --ag-radius: {radius}px;
    --ag-media-size: 380px;

    display: flex;
    flex-direction: row;
    gap: var(--ag-gap);
    width: 100%;
    max-width: 100%;
    perspective: 1400px;
    perspective-origin: 50% 50%;
    height: {height}px;
    padding: 6px 2px;
  }}

  .ag-panel {{
    position: relative;
    flex: 1 1 0;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
    border-radius: var(--ag-radius);
    cursor: pointer;
    display: block;
    text-decoration: none;
    outline: none;
    transform-style: preserve-3d;
    transform-origin: center center;
    background: #0A0713;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 10px 30px -18px rgba(0, 0, 0, 0.8);
    will-change: flex-grow, transform;
    -webkit-tap-highlight-color: transparent;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
  }}

  .ag-panel:focus-visible {{
    box-shadow: 0 0 0 2px var(--ag-accent), 0 10px 30px -18px rgba(0, 0, 0, 0.8);
  }}

  .ag-panel--active {{
    border-color: rgba(212, 175, 55, 0.5);
    box-shadow: 0 14px 40px -12px rgba(212, 175, 55, 0.3), 0 0 24px rgba(0, 0, 0, 0.9);
  }}

  .ag-panel__frame {{
    position: absolute;
    inset: 0;
    overflow: hidden;
    border-radius: inherit;
    background: {overlay_color};
  }}

  .ag-panel__media {{
    position: absolute;
    top: 50%;
    left: 50%;
    width: var(--ag-media-size);
    height: 100%;
    will-change: transform, filter;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .ag-panel__media img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 18px;
    display: block;
    user-select: none;
    -webkit-user-drag: none;
  }}

  .ag-panel__overlay {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    background: linear-gradient(180deg, transparent 40%, rgba(8, 11, 16, 0.82) 80%, rgba(8, 11, 16, 0.96) 100%);
  }}

  .ag-panel__badge {{
    position: absolute;
    top: 14px;
    right: 14px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 11px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    z-index: 3;
    pointer-events: none;
    backdrop-filter: blur(8px);
    transition: opacity 0.3s ease;
  }}
  .badge-brahma {{
    background: rgba(46, 160, 67, 0.22);
    color: #3FB950;
    border: 1px solid rgba(46, 160, 67, 0.4);
  }}
  .badge-interlocking {{
    background: rgba(56, 139, 253, 0.22);
    color: #58A6FF;
    border: 1px solid rgba(56, 139, 253, 0.4);
  }}

  .ag-panel__download {{
    position: absolute;
    top: 14px;
    left: 14px;
    z-index: 4;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 11px;
    border-radius: 6px;
    background: rgba(13, 17, 23, 0.85);
    border: 1px solid rgba(212, 175, 55, 0.4);
    color: var(--ag-accent);
    font-size: 0.72rem;
    font-weight: 600;
    text-decoration: none;
    backdrop-filter: blur(8px);
    opacity: 0;
    transform: translateY(-4px);
    transition: opacity 0.3s ease, transform 0.3s ease, background 0.2s ease, border-color 0.2s ease;
    cursor: pointer;
    pointer-events: auto;
  }}
  .ag-panel__download:hover {{
    background: rgba(212, 175, 55, 0.25);
    color: #FFF;
    border-color: var(--ag-accent);
  }}
  .ag-panel--active .ag-panel__download {{
    opacity: 1;
    transform: translateY(0);
  }}

  .ag-panel__label {{
    position: absolute;
    left: 18px;
    bottom: 18px;
    right: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    pointer-events: none;
    z-index: 2;
  }}

  .ag-panel__bar {{
    flex: 0 0 auto;
    width: 3.5px;
    height: 32px;
    border-radius: 3px;
    background: var(--ag-accent);
    opacity: 0;
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.8);
  }}

  .ag-panel__text-group {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow: hidden;
  }}

  .ag-panel__text {{
    color: var(--ag-text);
    font-weight: 700;
    font-size: clamp(0.95rem, 1.25vw, 1.25rem);
    letter-spacing: 0.01em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    opacity: 0;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.8);
  }}

  .ag-panel__sub {{
    color: #8B949E;
    font-family: monospace;
    font-size: 0.74rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    opacity: 0;
  }}

  @media (max-width: 520px) {{
    .accordion-gallery {{
      flex-direction: column;
      perspective: none;
      height: auto !important;
    }}
    .ag-panel {{
      min-height: 120px;
      transform: none !important;
    }}
  }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
</head>
<body>

<div id="galleryRoot" class="accordion-gallery" role="list" aria-label="Kolam Accordion Gallery"></div>

<script>
  const items = {items_json};
  const count = items.length;
  let active = Math.min(Math.max({default_index}, 0), count - 1);
  const expandRatio = {expand_ratio};
  const duration = {duration};
  const ease = "power3.out";
  const tilt = {tilt};
  const parallax = {parallax};
  const gap = {gap};
  const baseGray = {gray_val};
  let currentTimeline = null;
  let mediaSize = 380;

  const root = document.getElementById('galleryRoot');

  // Build DOM
  items.forEach((item, i) => {{
    const panel = document.createElement('div');
    panel.className = `ag-panel${{i === active ? ' ag-panel--active' : ''}}`;
    panel.setAttribute('role', 'listitem');
    panel.setAttribute('tabindex', '0');
    panel.setAttribute('aria-label', item.label);

    const isBrahma = item.is_brahma;
    const badgeClass = isBrahma ? 'badge-brahma' : 'badge-interlocking';
    const badgeText = isBrahma ? '● BRAHMA MUDI (1 LOOP)' : `● INTERLOCKING (${{item.num_loops}} LOOPS)`;

    panel.innerHTML = `
      <div class="ag-panel__badge ${{badgeClass}}">${{badgeText}}</div>
      <a class="ag-panel__download" href="${{item.image}}" download="${{item.label.toLowerCase().replace(/\\s+/g, '_')}}.png" title="Download High-Res PNG">
        ⬇ Export PNG
      </a>
      <div class="ag-panel__frame">
        <div class="ag-panel__media">
          <img src="${{item.image}}" alt="${{item.label}}" draggable="false" />
        </div>
        <div class="ag-panel__overlay"></div>
      </div>
      <div class="ag-panel__label">
        <div class="ag-panel__bar"></div>
        <div class="ag-panel__text-group">
          <div class="ag-panel__text">${{item.label}}</div>
          <div class="ag-panel__sub">${{item.sublabel}}</div>
        </div>
      </div>
    `;

    panel.addEventListener('mouseenter', () => {{
      if (active !== i) {{
        active = i;
        updateActiveClasses();
        applyLayout(true);
      }}
    }});

    panel.addEventListener('click', (e) => {{
      if (e.target.closest('.ag-panel__download')) return;
      if (active !== i) {{
        active = i;
        updateActiveClasses();
        applyLayout(true);
      }}
    }});

    panel.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {{
        e.preventDefault();
        active = (active + 1) % count;
        updateActiveClasses();
        applyLayout(true);
      }} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{
        e.preventDefault();
        active = (active - 1 + count) % count;
        updateActiveClasses();
        applyLayout(true);
      }}
    }});

    root.appendChild(panel);
  }});

  const panels = Array.from(root.querySelectorAll('.ag-panel'));

  function updateActiveClasses() {{
    panels.forEach((p, idx) => {{
      if (idx === active) {{
        p.classList.add('ag-panel--active');
        p.setAttribute('aria-current', 'true');
      }} else {{
        p.classList.remove('ag-panel--active');
        p.removeAttribute('aria-current');
      }}
    }});
  }}

  function measure() {{
    const rect = root.getBoundingClientRect();
    const usable = Math.max(rect.width - gap * (count - 1), 120);
    const r = Math.min(Math.max(expandRatio, 0.2), 0.9);
    mediaSize = Math.max(140, usable * r * 1.15);
    root.style.setProperty('--ag-media-size', `${{mediaSize}}px`);
  }}

  function applyLayout(animate) {{
    if (!panels.length) return;
    const r = Math.min(Math.max(expandRatio, 0.2), 0.9);
    const grow = count > 1 ? (r * (count - 1)) / (1 - r) : 1;

    if (currentTimeline) currentTimeline.kill();
    const dur = animate ? duration : 0;
    const tl = gsap.timeline();

    panels.forEach((panel, i) => {{
      const isActive = i === active;
      const media = panel.querySelector('.ag-panel__media');
      const bar = panel.querySelector('.ag-panel__bar');
      const text = panel.querySelector('.ag-panel__text');
      const sub = panel.querySelector('.ag-panel__sub');

      const rot = isActive ? 0 : (i < active ? tilt : -tilt);
      tl.to(panel, {{ flexGrow: isActive ? grow : 1, rotateY: rot, duration: dur, ease: ease }}, 0);

      if (media) {{
        const drift = Math.max(-1.5, Math.min(1.5, active - i));
        const shift = drift * parallax * mediaSize * 0.06;
        const gray = isActive ? 0 : baseGray;
        const dim = isActive ? 0 : 0.28;

        tl.to(media, {{
          xPercent: -50,
          yPercent: -50,
          x: isActive ? 0 : shift,
          filter: `grayscale(${{gray}}) brightness(${{1 - dim}})`,
          duration: dur,
          ease: ease
        }}, 0);
      }}

      if (bar && text) {{
        if (isActive) {{
          tl.to([bar, text, sub].filter(Boolean), {{
            opacity: 1,
            x: 0,
            duration: dur,
            ease: ease,
            stagger: 0.05
          }}, 0);
        }} else {{
          tl.to([bar, text, sub].filter(Boolean), {{
            opacity: 0,
            x: -14,
            duration: dur * 0.6,
            ease: ease
          }}, 0);
        }}
      }}
    }});

    currentTimeline = tl;
  }}

  measure();
  applyLayout(false);

  const ro = new ResizeObserver(() => {{
    measure();
    applyLayout(false);
  }});
  ro.observe(root);
</script>
</body>
</html>
"""

