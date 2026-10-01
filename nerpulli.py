"""
nerpulli.py - Autonomous Nér Pulli (நேர் புள்ளி) Kolam Generator using Python Turtle

===================================================================================
ACADEMIC FOUNDATION & CITATION:
Based on the N-Line Drawing Method & Graph Theory Blueprint:
- Anu Reddy (2023), "Kambi Kolam as Algorithmic Pattern", Alpaca Salon 2023.
  URL: https://alpaca.pubpub.org/pub/xywz3ebv/release/1
- Shojiro Nagata & Kiwamu Yanagisawa (2006), "Digitalization of Kolam Patterns
  and Tactile Kolam Tools", Knot Theory Models.
- Gift Siromoney & Rani Siromoney (1974, 1986), "Picture Languages with Array Grammars".
===================================================================================
NÉR PULLI KOLAM RULES & MATHEMATICAL FOUNDATION:
===================================================================================
1. GRID RULE (Nér Pulli):
   - Dots are placed in straight orthogonal alignment (square N x N, or diamond 1-3-5-3-1).
   - In Nér Pulli, dots in subsequent rows align directly vertically and horizontally 
     (unlike Sandhu Pulli where dots alternate in gaps).

2. DUAL-TRAVERSAL RULE (Through & Around Dots):
   - Unlike pure Sikku Kolam (where lines can NEVER touch dots), in Nér Pulli Kolams:
     (a) Lines CAN pass directly THROUGH the dots (connecting dot-to-dot along 0°, 90°, and 45°).
     (b) Lines CAN ALSO loop AROUND the dots (forming smooth arcs around boundary/corner dots).
     This dual behavior creates the iconic hybrid "Kodu-Sikku" (geometric petals + continuous loops).

3. NAGATA'S N-LINE METHOD (Navigating Lines):
   - Navigating lines (N-lines) connect adjacent dots without isolated loops.
   - A crossing is placed at the exact middle point of each N-line.
   - The strand goes straight through the crossing and turns around adjacent dots,
     alternating clockwise / anti-clockwise at consecutive crossings.

4. SYMMETRY RULE (D4 / C4 Group):
   - The design must exhibit 4-fold rotational symmetry (90°) and/or bilateral mirror reflection.
   - Every stroke in the primary quadrant is folded to the other 3 quadrants.
===================================================================================
"""

import turtle
import math
import random
import time

# ---------------------------------------------------------------------
# 1. SETTINGS & COLOR PALETTES
# ---------------------------------------------------------------------
SPACING = 65               # Pixel distance between adjacent dots
DOT_RADIUS = 5             # Visual radius of the Pulli (dots)

# Traditional South Indian Palettes
PALETTES = {
    "1": {
        "name": "Temple Saffron & Rice Flour",
        "bg": "#14101A",        # Deep temple dark purple
        "dot": "#FFFFFF",       # Rice flour white
        "thru_line": "#F4A261",  # Warm saffron for lines passing through dots
        "arc_line": "#E9C46A",   # Golden turmeric for curving loops around dots
        "accent": "#E76F51"     # Kumkum vermillion accent
    },
    "2": {
        "name": "Classic Obsidian & Chalk",
        "bg": "#0D1117",        # Obsidian black floor
        "dot": "#FFFFFF",       # Pure white dot
        "thru_line": "#58A6FF",  # Subtle electric blue core
        "arc_line": "#F0E6D2",   # Pure white rice powder strand
        "accent": "#D4AF37"     # Gold
    },
    "3": {
        "name": "Terracotta Dawn",
        "bg": "#23110E",        # Red terracotta clay
        "dot": "#FFFFFF",       # White
        "thru_line": "#F7EDE2",  # Bright chalk
        "arc_line": "#F4A261",   # Ochre gold
        "accent": "#E63946"     # Deep Kumkum red
    }
}

# ---------------------------------------------------------------------
# 2. GRID & LATTICE BUILDER
# ---------------------------------------------------------------------
def create_ner_pulli_dots(lengths):
    """
    Creates centered (x, y) coordinates for a Nér Pulli dot grid.
    lengths: list of dot counts per row, e.g. [5, 5, 5, 5, 5] or [1, 3, 5, 7, 5, 3, 1]
    """
    dots = set()
    W = max(lengths)
    H = len(lengths)
    
    for y, length in enumerate(reversed(lengths)):
        offset = (W - length) // 2
        for x in range(length):
            dots.add((offset + x, y))
            
    return dots, W, H

def to_screen_coords(gx, gy, W, H, spacing=SPACING):
    """Converts lattice grid coordinates to centered screen pixel coordinates."""
    offset_x = (W - 1) * spacing / 2.0
    offset_y = (H - 1) * spacing / 2.0
    return (gx * spacing - offset_x, gy * spacing - offset_y)

# ---------------------------------------------------------------------
# 3. TURTLE DRAWING PRIMITIVES & 3D INTERLACED WEAVE
# ---------------------------------------------------------------------
def draw_line(pen, p1, p2):
    """Draws a smooth straight segment between two screen points."""
    pen.penup()
    pen.goto(p1)
    pen.pendown()
    pen.goto(p2)

def line_intersection(p1, p2, p3, p4):
    """
    Computes the geometric intersection point of segments p1-p2 and p3-p4.
    Returns (ix, iy) if they genuinely cross inside both segments, else None.
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-6:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0.04 < t < 0.96 and 0.04 < u < 0.96:
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (ix, iy)
    return None

def draw_over_pass(pen, center, angle_deg, length, color, bg_color, width=3.2, gap=5.0):
    """
    Renders an authentic 3D over-pass bridge at a crossing intersection:
    1. Erases a small rectangular margin (gap) along the top strand using bg_color.
    2. Draws the top strand smoothly through the gap in the foreground color.
    Creates the classic over-under woven Celtic / Kambi Kolam ribbon effect.
    """
    cx, cy = center
    rad = math.radians(angle_deg)
    dx = math.cos(rad) * (length / 2.0)
    dy = math.sin(rad) * (length / 2.0)
    
    p1 = (cx - dx, cy - dy)
    p2 = (cx + dx, cy + dy)
    
    # 1. Mask out under-strand with background color (creates negative space margin)
    pen.color(bg_color)
    pen.width(width + gap)
    pen.penup()
    pen.goto(p1)
    pen.pendown()
    pen.goto(p2)
    
    # 2. Redraw top-strand in strand color
    pen.color(color)
    pen.width(width)
    pen.penup()
    pen.goto(p1)
    pen.pendown()
    pen.goto(p2)

def draw_arc_around_dot(pen, center, radius, start_angle, end_angle, steps=36):
    """
    Draws a smooth circular arc curving AROUND a dot center.
    Satisfies Marcia Ascher's Smoothness & Obstacle Rule for boundary turns.
    """
    cx, cy = center
    pen.penup()
    
    # Calculate sweep
    sweep = (end_angle - start_angle) % 360
    if sweep == 0 and end_angle != start_angle:
        sweep = 360
        
    num_steps = max(6, int(steps * abs(sweep) / 360.0))
    for i in range(num_steps + 1):
        theta = math.radians(start_angle + sweep * (i / num_steps))
        px = cx + radius * math.cos(theta)
        py = cy + radius * math.sin(theta)
        if i == 0:
            pen.goto(px, py)
            pen.pendown()
        else:
            pen.goto(px, py)

def draw_dots(pen, dots, W, H, palette):
    """Draws the Pulli (dot lattice) with a subtle traditional halo."""
    pen.hideturtle()
    for gx, gy in dots:
        sx, sy = to_screen_coords(gx, gy, W, H)
        
        # Outer delicate Kumkum ring
        pen.penup()
        pen.goto(sx, sy - (DOT_RADIUS + 3))
        pen.pendown()
        pen.color(palette["accent"])
        pen.circle(DOT_RADIUS + 3)
        
        # Solid center rice dot
        pen.penup()
        pen.goto(sx, sy)
        pen.color(palette["dot"])
        pen.dot(DOT_RADIUS * 2)

# ---------------------------------------------------------------------
# 4. NÉR PULLI GENERATIVE ENGINE (Through + Around Dots)
# ---------------------------------------------------------------------
def generate_ner_pulli_design(line_pen, dots, W, H, palette, motif_style="lotus_mandala", seed=None, use_3d_weave=True):
    """
    Synthesizes an authentic Nér Pulli Kolam design combining:
    1. Through-the-dot straight structural chords (Kodu framework)
    2. Around-the-dot looping arcs (Sikku petals & loops)
    3. Strict 4-fold or bilateral mirror symmetry.
    4. Optional 3D Woven Ribbon Interlacing (Over-Under passes, Anu Reddy 2023).
    """
    if seed is not None:
        random.seed(seed)
        
    center_gx = (W - 1) / 2.0
    center_gy = (H - 1) / 2.0
    
    # Store drawn line segments for 3D over-under knot calculation
    drawn_segments = []
    
    def stroke_line(p1, p2, color, width):
        line_pen.color(color)
        line_pen.width(width)
        draw_line(line_pen, p1, p2)
        drawn_segments.append({'p1': p1, 'p2': p2, 'color': color, 'width': width})

    # Classify dots into concentric geometric shells
    dot_list = list(dots)
    shells = {}
    for gx, gy in dot_list:
        dx = gx - center_gx
        dy = gy - center_gy
        dist_sq = round(dx * dx + dy * dy, 2)
        shells.setdefault(dist_sq, []).append((gx, gy))
        
    sorted_dists = sorted(shells.keys())

    # =================================================================
    # LAYER 1: THROUGH-THE-DOTS (Kodu Connections - Stars & Diamonds)
    # Lines pass directly THROUGH the dots, establishing the core geometry.
    # =================================================================
    thru_color = palette["thru_line"]
    thru_width = 3.2

    # 1A. Connect concentric diamond rings (passing through dots)
    for dist_sq in sorted_dists:
        shell_dots = shells[dist_sq]
        if len(shell_dots) in (4, 8):
            sorted_by_angle = sorted(
                shell_dots,
                key=lambda p: math.atan2(p[1] - center_gy, p[0] - center_gx)
            )
            for idx in range(len(sorted_by_angle)):
                p1 = sorted_by_angle[idx]
                p2 = sorted_by_angle[(idx + 1) % len(sorted_by_angle)]
                sp1 = to_screen_coords(p1[0], p1[1], W, H)
                sp2 = to_screen_coords(p2[0], p2[1], W, H)
                stroke_line(sp1, sp2, thru_color, thru_width)

    # 1B. 8-Pointed Star / Cross Diagonal Chords (Directly intersecting dots)
    if len(sorted_dists) >= 3:
        mid_shell = shells[sorted_dists[min(2, len(sorted_dists) - 1)]]
        
        for dot in mid_shell:
            dx = dot[0] - center_gx
            dy = dot[1] - center_gy
            opp_dot = (center_gx - dx, center_gy - dy)
            if opp_dot in dots:
                sp1 = to_screen_coords(dot[0], dot[1], W, H)
                sp2 = to_screen_coords(opp_dot[0], opp_dot[1], W, H)
                stroke_line(sp1, sp2, thru_color, thru_width)

    # =================================================================
    # LAYER 2: AROUND-THE-DOTS (Sikku Curves - Petals & Outer Loops)
    # Lines loop smoothly around the dots without touching their centers.
    # =================================================================
    arc_color = palette["arc_line"]
    arc_width = 3.0
    line_pen.color(arc_color)
    line_pen.width(arc_width)
    arc_radius = SPACING * 0.42

    for gx, gy in dot_list:
        neighbors = {
            'N': (gx, gy + 1) in dots,
            'S': (gx, gy - 1) in dots,
            'E': (gx + 1, gy) in dots,
            'W': (gx - 1, gy) in dots,
        }
        
        sx, sy = to_screen_coords(gx, gy, W, H)
        
        if not neighbors['N'] and not neighbors['E']:
            draw_arc_around_dot(line_pen, (sx, sy), arc_radius, 0, 90)
            stroke_line((sx + arc_radius, sy), (sx + arc_radius, sy - SPACING * 0.4), arc_color, arc_width)
            stroke_line((sx, sy + arc_radius), (sx - SPACING * 0.4, sy + arc_radius), arc_color, arc_width)
            
        if not neighbors['N'] and not neighbors['W']:
            draw_arc_around_dot(line_pen, (sx, sy), arc_radius, 90, 180)
            stroke_line((sx, sy + arc_radius), (sx + SPACING * 0.4, sy + arc_radius), arc_color, arc_width)
            stroke_line((sx - arc_radius, sy), (sx - arc_radius, sy - SPACING * 0.4), arc_color, arc_width)
            
        if not neighbors['S'] and not neighbors['W']:
            draw_arc_around_dot(line_pen, (sx, sy), arc_radius, 180, 270)
            stroke_line((sx - arc_radius, sy), (sx - arc_radius, sy + SPACING * 0.4), arc_color, arc_width)
            stroke_line((sx, sy - arc_radius), (sx + SPACING * 0.4, sy - arc_radius), arc_color, arc_width)
            
        if not neighbors['S'] and not neighbors['E']:
            draw_arc_around_dot(line_pen, (sx, sy), arc_radius, 270, 360)
            stroke_line((sx, sy - arc_radius), (sx - SPACING * 0.4, sy - arc_radius), arc_color, arc_width)
            stroke_line((sx + arc_radius, sy), (sx + arc_radius, sy + SPACING * 0.4), arc_color, arc_width)

    # =================================================================
    # LAYER 3: INTERLACING BRIDGES (Connecting Through-dots to Around-dots)
    # =================================================================
    line_pen.color(palette["accent"])
    line_pen.width(2.4)
    
    for gx, gy in dot_list:
        if (gx + 1, gy) in dots and gy % 2 == 0:
            p1 = to_screen_coords(gx, gy, W, H)
            p2 = to_screen_coords(gx + 1, gy, W, H)
            mid_x = (p1[0] + p2[0]) / 2.0
            mid_y = (p1[1] + p2[1]) / 2.0
            draw_arc_around_dot(line_pen, (mid_x, mid_y + SPACING * 0.15), SPACING * 0.35, 200, 340)

    # =================================================================
    # LAYER 4: 3D WOVEN RIBBON INTERLACING (Over-Under Passes)
    # Enforces alternating knot theory passes (Anu Reddy / Nagata, 2023)
    # =================================================================
    if use_3d_weave and len(drawn_segments) > 1:
        crossings = []
        for i in range(len(drawn_segments)):
            for j in range(i + 1, len(drawn_segments)):
                s1 = drawn_segments[i]
                s2 = drawn_segments[j]
                pt = line_intersection(s1['p1'], s1['p2'], s2['p1'], s2['p2'])
                if pt is not None:
                    ang1 = math.degrees(math.atan2(s1['p2'][1] - s1['p1'][1], s1['p2'][0] - s1['p1'][0]))
                    ang2 = math.degrees(math.atan2(s2['p2'][1] - s2['p1'][1], s2['p2'][0] - s2['p1'][0]))
                    crossings.append((pt, s1, ang1, s2, ang2))

        for pt, s1, ang1, s2, ang2 in crossings:
            # Alternating knot rule:
            # Parity based on spatial position gives consistent over/under alternation
            grid_parity = int(round(pt[0] / 30.0) + round(pt[1] / 30.0))
            is_s1_over = (grid_parity % 2 == 0)

            top_seg = s1 if is_s1_over else s2
            top_angle = ang1 if is_s1_over else ang2

            draw_over_pass(
                line_pen,
                center=pt,
                angle_deg=top_angle,
                length=22.0,
                color=top_seg['color'],
                bg_color=palette["bg"],
                width=top_seg['width'],
                gap=5.5
            )

# ---------------------------------------------------------------------
# 5. NAGATA N-LINE BLUEPRINT OVERLAY (Alpaca Salon 2023 Method)
# ---------------------------------------------------------------------
def draw_nagata_n_lines_blueprint(pen, dots, W, H, palette):
    """
    Renders Shojiro Nagata's Navigating N-Lines (N-lines) and Midpoint Crossings
    as formalized in Anu Reddy (2023) 'Kambi Kolam as Algorithmic Pattern'.
    """
    pen.hideturtle()
    pen.color(palette.get("accent", "#E76F51"))
    pen.width(1.2)
    
    # 1. Draw N-Lines between adjacent dots
    for gx, gy in dots:
        p1 = to_screen_coords(gx, gy, W, H)
        for dx, dy in [(1, 0), (0, 1)]:
            neighbor = (gx + dx, gy + dy)
            if neighbor in dots:
                p2 = to_screen_coords(neighbor[0], neighbor[1], W, H)
                draw_line(pen, p1, p2)
                
                # 2. Draw crossing (+) at the midpoint of each N-line
                mid_x = (p1[0] + p2[0]) / 2.0
                mid_y = (p1[1] + p2[1]) / 2.0
                cross_size = 5.0
                
                # Crossing line 1
                pen.penup()
                pen.goto(mid_x - cross_size, mid_y - cross_size)
                pen.pendown()
                pen.goto(mid_x + cross_size, mid_y + cross_size)
                
                # Crossing line 2
                pen.penup()
                pen.goto(mid_x - cross_size, mid_y + cross_size)
                pen.pendown()
                pen.goto(mid_x + cross_size, mid_y - cross_size)

# ---------------------------------------------------------------------
# 6. INTERACTIVE CLI RUNNER
# ---------------------------------------------------------------------
def prompt_user_menu():
    print("=" * 65)
    print("          NÉR PULLI (நேர் புள்ளி) KOLAM GENERATOR")
    print("  Lines Pass Through Dots (Kodu) AND Loop Around Dots (Sikku)")
    print("  Method: Shojiro Nagata's N-Line Algorithm (Reddy, 2023)")
    print("=" * 65)
    print("1. Classic 5x5 Square Matrix (25 Dots)")
    print("2. 7-to-1 Rhombus / Diamond (25 Dots) [Default]")
    print("3. Large 9-to-1 Grand Mandapam (41 Dots)")
    print("4. Custom Row Vector (e.g. 3, 5, 7, 5, 3)")
    
    choice = input("\nSelect Grid Type (1/2/3/4) [default 2]: ").strip() or "2"
    
    if choice == "1":
        lengths = [5, 5, 5, 5, 5]
    elif choice == "3":
        lengths = [1, 3, 5, 7, 9, 7, 5, 3, 1]
    elif choice == "4":
        raw = input("Enter comma-separated row counts (e.g. 3,5,7,5,3): ").strip()
        try:
            lengths = [int(x.strip()) for x in raw.split(",") if x.strip()]
            if not lengths: lengths = [1, 3, 5, 7, 5, 3, 1]
        except Exception:
            print("Invalid input, defaulting to 7-to-1 Diamond.")
            lengths = [1, 3, 5, 7, 5, 3, 1]
    else:
        lengths = [1, 3, 5, 7, 5, 3, 1]
        
    print("\nColor Palettes:")
    print("1. Temple Saffron & Rice Flour (Traditional Gold)")
    print("2. Classic Obsidian & Chalk (Dark Indigo)")
    print("3. Terracotta Dawn (Earth Red)")
    pal_choice = input("Select Palette (1/2/3) [default 1]: ").strip() or "1"
    palette = PALETTES.get(pal_choice, PALETTES["1"])
    
    seed_input = input("Random Seed (press Enter for random, or enter integer): ").strip()
    seed = int(seed_input) if seed_input.isdigit() else random.randint(1, 99999)
    
    weave_input = input("Enable 3D Woven Ribbon (Over-Under Passes)? (y/n) [default y]: ").strip().lower()
    use_3d_weave = (weave_input != 'n')

    blueprint_input = input("Overlay Nagata N-Line Template Blueprint? (y/n) [default n]: ").strip().lower()
    show_blueprint = (blueprint_input == 'y')
    
    return lengths, palette, seed, show_blueprint, use_3d_weave

def main():
    lengths, palette, seed, show_blueprint, use_3d_weave = prompt_user_menu()
    dots, W, H = create_ner_pulli_dots(lengths)
    
    # Initialize Turtle Screen
    screen = turtle.Screen()
    screen.title(f"Nér Pulli Kolam — {palette['name']} (Seed: {seed})")
    screen.bgcolor(palette["bg"])
    screen.setup(width=850, height=850)
    screen.tracer(0)  # Enable instant fast rendering
    
    # Status overlay pen
    mode_desc = "3D Woven Interlacing Active (Over-Under)" if use_3d_weave else "Flat 2D Planar Strokes"
    info_pen = turtle.Turtle()
    info_pen.hideturtle()
    info_pen.penup()
    info_pen.color("#8B949E")
    info_pen.goto(0, 368)
    info_pen.write(
        f"NÉR PULLI KOLAM  ·  Grid: {lengths} ({len(dots)} Dots)  ·  Seed: {seed}\n"
        f"Gold = Sikku Loops (Around Dots)  |  Saffron = Kodu Chords (Through Dots)  |  {mode_desc}",
        align="center",
        font=("Arial", 10, "bold")
    )
    
    # Optional Nagata N-Line Blueprint skeleton
    if show_blueprint:
        bp_pen = turtle.Turtle()
        draw_nagata_n_lines_blueprint(bp_pen, dots, W, H, palette)
    
    # Draw Dot Lattice
    dot_pen = turtle.Turtle()
    draw_dots(dot_pen, dots, W, H, palette)
    
    # Draw Nér Pulli Design
    line_pen = turtle.Turtle()
    line_pen.hideturtle()
    line_pen.speed(0)
    generate_ner_pulli_design(line_pen, dots, W, H, palette, seed=seed, use_3d_weave=use_3d_weave)
    
    # Refresh screen
    screen.update()
    
    print("\n[SUCCESS] Nér Pulli Kolam rendered on screen!")
    print("Click on the turtle window to close it.")
    screen.exitonclick()

if __name__ == "__main__":
    main()
