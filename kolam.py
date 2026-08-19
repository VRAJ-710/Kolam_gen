import turtle          # turtle module import kar rahe hain - yehi humara drawing engine hai, pen jaisa kaam karta hai screen pe
import math             # math module chahiye kyunki humein angle calculate karne honge (atan2, degrees waghera) arc draw karne ke liye
import random            # random module se hi kolam har baar different aayega - random.choice() se pattern randomly select hoga

# ---------------------------------------------------------------------
# 1. SETTINGS
# ---------------------------------------------------------------------
# Yeh section basically constants define kar raha hai jo pura code mein use honge
SPACING = 60                       # do dots ke beech ka distance (pixels mein) - isko badhaoge to kolam bada aur spread out banega
RADIUS = SPACING / 2               # har arc (curve) isi radius se banega - SPACING ka half isliye kyunki edge midpoint tak ka distance hi radius hai


# ---------------------------------------------------------------------
# 2. USER INPUT HANDLING
# ---------------------------------------------------------------------
# Is section ka kaam hai user se poochna ki kaisa dot pattern chahiye (shape of kolam grid)
def get_dot_pattern():
    print("\n" + "="*40)     # bas ek separator line print ho rahi hai, "=" 40 baar - console mein header jaisa dikhane ke liye
    print("        SIKKU KOLAM SHAPE GENERATOR")   # title print
    print("="*40)            # neeche bhi wahi separator
    print("1. Square Grid (e.g., 5x5)")             # option 1 - simple NxN square grid
    print("2. Diamond / Rhombus (e.g., 1-3-5-3-1)")  # option 2 - diamond shape, default hai isliye zyada common
    print("3. Custom row lengths (e.g., 3,5,7,5,3)")  # option 3 - user apni marzi se row lengths de sakta hai
    
    choice = input("\nSelect shape type (1/2/3) [default 2]: ").strip()   # user ka input le rahe, .strip() se extra spaces hat jayenge
    if not choice:                # agar user ne kuch enter nahi kiya (khali Enter dabaya)
        choice = '2'              # to default choice '2' set kar do (diamond shape)

    if choice == '1':             # agar user ne square grid choose kiya
        try:
            n = int(input("Enter size of square (e.g. 5): ") or 5)   # size input lo, agar khali chhoda to 5 default use hoga
        except ValueError:         # agar user ne number ki jagah kuch aur type kar diya (jaise letters)
            n = 5                  # to bhi fallback 5 hi rakho, crash nahi hone dena
        return [n] * n             # square grid ka matlab hai har row ki length same 'n' - list mein n baar n repeat kiya
        
    elif choice == '3':           # custom row lengths wala option
        val = input("Enter comma-separated row lengths (e.g. 3,5,5,5,3): ")   # comma separated values input le rahe
        try:
            return [int(x.strip()) for x in val.split(',')]   # string ko comma pe split karke har part ko int mein convert kar rahe (list comprehension)
        except ValueError:          # agar input galat format mein diya (jaise letters ya extra commas)
            print("Invalid input, defaulting to 3,5,7,5,3")   # user ko batao ki invalid tha
            return [3, 5, 7, 5, 3]   # aur ek default diamond-jaisa pattern return kar do
            
    else: # default to Diamond      # agar choice '2' hai ya kuch aur invalid, dono case mein diamond banega (default path)
        try:
            n = int(input("Enter max width of diamond (odd number, e.g. 5): ") or 5)   # diamond ki max width lo, default 5
            if n % 2 == 0:            # agar n even number nikla
                n += 1                 # to usko odd bana do (+1 kar diya) - Comment: Ensure odd number for a clean center point
        except ValueError:
            n = 5                     # yaha bhi agar galat input hai to fallback n=5

        half = list(range(1, n, 2))   # 1 se n tak odd numbers ki list bana rahe hain (1,3,5,... jab tak n se chhota rahe) - yeh diamond ka upar wala half hai
        return half + [n] + half[::-1]   # pura diamond banega: half (badhta hua) + n (sabse chaudi row beech mein) + half ulta (ghatna hua)


def create_dots(lengths):
    """Takes a list of row lengths and centers them into a coordinate set."""
    # Is function ka kaam hai row-lengths ki list lekar actual (x,y) dot coordinates banana, aur unhe center mein align karna
    dots = set()              # set() use kiya kyunki dots mein duplicate nahi hone chahiye, aur lookup bhi fast hota hai set mein
    W = max(lengths)          # sabse lambi row ki length hi total width W hogi (grid ki width)
    H = len(lengths)          # total kitni rows hain wahi H hai (grid ki height)
    
    for y, length in enumerate(reversed(lengths)):   # reversed() isliye kyunki hum neeche se upar (bottom to top) coordinates chahte, enumerate se y index milega
        offset = (W - length) // 2         # har row ko center karne ke liye offset calculate - agar row chhoti hai to usko beech mein laane ke liye shift
        for x in range(length):            # us row mein jitne bhi dots hain unko loop kar rahe
            dots.add((offset + x, y))      # actual dot coordinate add kar rahe set mein (offset add karke centering ho gayi)
            
    return dots, W, H          # teeno cheez return - dots ka set, aur grid ki width/height


# ---------------------------------------------------------------------
# 3. GEOMETRY HELPERS
# ---------------------------------------------------------------------
# Yeh functions grid coordinates ko actual screen pixel coordinates mein convert karte hain aur drawing helper hain
def grid_point(x, y, W, H):
    """Screen (x, y) coordinates, automatically centering the bounding box."""
    # Grid ka (x,y) point diya hai (jo dot-units mein hai), isko turtle screen ke pixel coordinates mein convert karna hai
    offset_x = (W - 1) * SPACING / 2   # poore grid ko horizontally center karne ke liye offset - taaki (0,0) screen center ke around aaye
    offset_y = (H - 1) * SPACING / 2   # same but vertically center karne ke liye
    return (x * SPACING - offset_x, y * SPACING - offset_y)   # x,y ko pixel scale mein convert karke offset subtract kiya - centered pixel coordinate mil gaya


def draw_arc(pen, center, start, extent, clockwise, radius=RADIUS):
    """Draws a continuous arc around a specific point."""
    # Yeh function ek curve (arc) banata hai kisi center point ke around, given radius aur extent (kitne degree ka arc) ke sath
    pen.penup()             # pen upar utha do taaki move karte waqt line na bane
    pen.goto(start)          # turtle ko arc ke starting point pe le jao
    pen.pendown()            # ab pen neeche rakho taaki ab se draw ho jaha bhi turtle move kare

    cx, cy = center           # center point ke x,y coordinates alag kar liye
    px, py = start             # starting point ke x,y coordinates alag kar liye
    angle_to_center = math.degrees(math.atan2(cy - py, cx - px))   # start point se center tak ka angle nikal rahe (radians se degrees mein convert karke) - atan2 se correct quadrant ka angle milta hai

    if clockwise:                          # agar clockwise arc banana hai
        pen.setheading(angle_to_center + 90)   # turtle ki heading (direction) set kar rahe - clockwise ke liye center-angle + 90 lagana padta hai taaki tangent direction sahi mile
        pen.circle(-radius, extent)             # turtle.circle() negative radius se clockwise arc banata hai, extent degree tak
    else:                                    # counter-clockwise (anti-clockwise) arc ke liye
        pen.setheading(angle_to_center - 90)    # heading set - is baar minus 90 (opposite tangent direction)
        pen.circle(radius, extent)               # positive radius se turtle.circle() anti-clockwise arc banata hai


def draw_line(pen, start, end):
    """Draws a straight segment connecting two edge midpoints."""
    # Simple straight line draw karne wala helper - do points ke beech
    pen.penup()          # pen uthao, move karna hai bina draw kiye
    pen.goto(start)        # start point pe pahucho
    pen.pendown()          # ab pen neeche - draw mode on
    pen.goto(end)           # end point tak seedha line kheech do (turtle.goto seedhi line banata hai)


# ---------------------------------------------------------------------
# 4. DRAWING ROUTINES
# ---------------------------------------------------------------------
# Yeh section actual visual output banata hai - dots aur kolam ki lines dono
def draw_dots(pen, dots, W, H):
    # Sirf saare dots (bindiyan) draw karne ka kaam - grid pe jaha jaha dot hai wahan white dot bana do
    pen.color("#FFFFFF")           # pen ka color white set kar diya (dots ke liye)
    for x, y in dots:               # har dot coordinate pe loop chala rahe (set se unpack ho raha x,y)
        pen.penup()                  # move karte waqt draw na ho isliye pen up
        pen.goto(grid_point(x, y, W, H))   # grid coordinate ko pixel coordinate mein convert karke wahan pahucho
        pen.dot(6)                    # ek chhota solid dot bana do 6 pixel diameter ka


def draw_cells_and_boundaries(pen, dots, W, H):
    """Unified engine handling curves, straight crosses, inclined lines, and boundary turns."""
    # Yeh sabse important aur bada function hai - yahi decide karta hai ki har "cell" (chaar dots ke beech ka square)
    # mein kaunsa design element banega: curve, cross, ya diagonal line
    num_cells_x = W + 1        # grid mein dots W hain, to unke beech ke "cells" (gaps) hamesha ek zyada honge -> W+1
    num_cells_y = H + 1        # same logic vertically
    
    # Randomly select between Arc A/B, Perpendicular Cross C, or Inclined Lines D/E
    orientation_matrix = [
        [random.choice(["A", "B", "C", "D", "E"]) for _ in range(num_cells_y)]   # har cell ke liye random ek type choose kar rahe: A/B (curves), C (cross), D/E (diagonal)
        for _ in range(num_cells_x)
    ]   # is tarah ek 2D matrix ban gaya jisme har (cell_x, cell_y) ke liye ek orientation type stored hai

    def get_orientation(cx, cy):
        """Enforces mirror symmetry across the shape."""
        # Kolam mein symmetry bahut zaroori hoti hai (real kolams hamesha symmetric hote hain), isliye
        # yeh function ensure karta hai ki grid ka mirror-image wala cell bhi matching pattern le
        mx = num_cells_x - 1 - cx    # current cell ka horizontal mirror-index nikal rahe (jaise last cell se distance)
        my = num_cells_y - 1 - cy    # vertical mirror-index

        rx, flipped_h = (cx, False) if cx <= mx else (mx, True)   # agar cx apne mirror se chhota/equal hai to wahi use karo, warna mirror index use karo aur flipped flag True kar do
        ry, flipped_v = (cy, False) if cy <= my else (my, True)   # same logic vertically

        ori = orientation_matrix[rx][ry]   # reduced (canonical/original half) index se hi orientation utha rahe - taaki dono symmetric halves same base pattern se aaye
        
        # Mirroring swaps A <-> B and D <-> E. Straight cross 'C' is self-symmetric.
        if flipped_h != flipped_v:      # agar sirf ek axis (horizontal YA vertical, dono nahi) pe flip hua hai
            if ori == "A": ori = "B"      # to A curve mirror hoke B ban jata hai (kyunki A aur B ek dusre ke mirror-image hain)
            elif ori == "B": ori = "A"     # B se A
            elif ori == "D": ori = "E"      # diagonal D mirror hoke E ban jata hai
            elif ori == "E": ori = "D"       # E se D
            # C (cross) ko touch nahi kiya kyunki cross khud symmetric hota hai, usko flip karne se farak nahi padta
        return ori         # final (correctly mirrored) orientation return kar diya is specific cell ke liye

    # Iterate over all cells (including padded outer boundary)
    for i in range(-1, W):        # i, -1 se W-1 tak jaayega - extra "-1" isliye taaki boundary ke bahar wale "padding" cells bhi cover ho jaye (edge dots ke around curves banane ke liye)
        for j in range(-1, H):     # same logic vertically
            
            # The 4 corners of the current cell
            cell_dots = {
                'bl': (i, j),          # bottom-left corner ka dot coordinate
                'br': (i + 1, j),       # bottom-right
                'tl': (i, j + 1),        # top-left
                'tr': (i + 1, j + 1)      # top-right
            }   # har cell ke chaar corners define kar diye dictionary mein (bl=bottom-left, br=bottom-right, tl=top-left, tr=top-right)

            existing_dots = {k: v for k, v in cell_dots.items() if v in dots}   # in chaar corners mein se sirf wahi rakho jo actually grid mein exist karte hain (kyunki diamond/custom shape mein saare corners nahi honge)
            count = len(existing_dots)     # kitne corners actually maujood hain (0 se 4 tak) - yeh decide karega kaisa design banega

            if count == 0:            # agar is cell mein ek bhi dot nahi hai
                continue                # to yeh cell completely khali hai, kuch draw hi nahi karna - skip kar do (loop ka agla iteration)

            # Edge midpoints
            mid_bottom = grid_point(i + 0.5, j, W, H)       # cell ke bottom edge ka beech ka point (pixel coordinate mein)
            mid_top    = grid_point(i + 0.5, j + 1, W, H)    # top edge ka midpoint
            mid_left   = grid_point(i, j + 0.5, W, H)         # left edge ka midpoint
            mid_right  = grid_point(i + 1, j + 0.5, W, H)      # right edge ka midpoint
            # yeh chaaro midpoints hi actual line/curve ke start-end points hote hain - kolam ki lines dots ko chhoti nahi, unke beech se guzarti hain

            if count == 4:      # agar chaaro corners (dots) present hain to yeh ek "full/interior" cell hai
                # Fully enclosed interior cell -> Arc A/B, Cross C, or Inclined D/E
                cell_x, cell_y = i + 1, j + 1        # is cell ka canonical index nikal rahe (mirror-matrix lookup ke liye consistent indexing)
                ori = get_orientation(cell_x, cell_y)  # is cell ke liye symmetric orientation nikal liya upar wale function se

                if ori == "C":                 # agar orientation "C" hai (straight cross)
                    # Perpendicular straight lines (0° and 90°)
                    draw_line(pen, mid_left, mid_right)   # ek horizontal straight line left se right
                    draw_line(pen, mid_bottom, mid_top)    # ek vertical straight line bottom se top - dono milke ek "+" cross banate hain

                elif ori in ("D", "E"):          # agar orientation D ya E hai (45 degree diagonal lines)
                    # 45-degree inclined straight lines
                    if ori == "D":                  # D type - ek diagonal direction
                        draw_line(pen, mid_left, mid_top)      # 45° incline    # left-mid se top-mid tak line (ek diagonal)
                        draw_line(pen, mid_right, mid_bottom)  # 45° incline    # right-mid se bottom-mid tak (dusri parallel diagonal)
                    else: # "E"                       # E type - opposite diagonal direction
                        draw_line(pen, mid_top, mid_right)     # -45° incline   # top-mid se right-mid
                        draw_line(pen, mid_bottom, mid_left)   # -45° incline   # bottom-mid se left-mid

                else:                             # baaki bacha "A" ya "B" - yeh curve wale orientations hain
                    # Quarter-circle curves (A or B)
                    arcs_to_draw = ['tl', 'br'] if ori == 'A' else ['tr', 'bl']   # A type mein top-left aur bottom-right corner ke around curve banega, B mein top-right aur bottom-left ke around
                    for arc in arcs_to_draw:                # dono corners ke liye loop
                        dot_pos = cell_dots[arc]              # us corner ka grid coordinate nikal liya
                        center = grid_point(dot_pos[0], dot_pos[1], W, H)   # us corner ko pixel coordinate mein convert kiya - yehi arc ka center banega
                        if arc == 'br':                         # bottom-right corner ke around arc
                            draw_arc(pen, center, mid_right, 90, clockwise=False)   # mid_right se start hoke 90 degree ka anti-clockwise arc, center=bottom-right dot - yeh khud-b-khud mid_bottom pe khatam hota hai (geometry ki wajah se)
                        elif arc == 'tl':                          # top-left corner ke around
                            draw_arc(pen, center, mid_left, 90, clockwise=False)    # mid_left se start hoke arc, mid_top pe end hota hai
                        elif arc == 'bl':                           # bottom-left corner ke around
                            draw_arc(pen, center, mid_bottom, 90, clockwise=False)   # mid_bottom se start, mid_left pe end
                        elif arc == 'tr':                            # top-right corner ke around
                            draw_arc(pen, center, mid_top, 90, clockwise=False)      # mid_top se start, mid_right pe end

            else:
                # Boundary cell -> wrap curved lines around exposed dots
                # Yeh wo case hai jaha cell mein saare 4 corners nahi hain (kam hain, jaise diamond ke edges pe) -
                # to sirf jo corners exist karte hain unke around chhota curve bana do taaki line continuous rahe boundary pe bhi
                arcs_to_draw = list(existing_dots.keys())   # jo bhi corners actually maujood hain unki list bana li
                for arc in arcs_to_draw:                      # har existing corner ke liye
                    dot_pos = cell_dots[arc]                    # uska coordinate nikala
                    center = grid_point(dot_pos[0], dot_pos[1], W, H)   # pixel coordinate mein convert kiya, arc ka center banega
                    
                    if arc == 'bl':                               # bottom-left corner present hai
                        draw_arc(pen, center, mid_bottom, 90, clockwise=False)   # mid_bottom se start hoke curve
                    elif arc == 'br':                               # bottom-right
                        draw_arc(pen, center, mid_right, 90, clockwise=False)     # mid_right se start
                    elif arc == 'tr':                                # top-right
                        draw_arc(pen, center, mid_top, 90, clockwise=False)        # mid_top se start
                    elif arc == 'tl':                                 # top-left
                        draw_arc(pen, center, mid_left, 90, clockwise=False)        # mid_left se start
                    # in sab cases mein bhi wahi 90-degree anti-clockwise arc logic use ho raha hai, bas different corner/start point ke sath


# ---------------------------------------------------------------------
# 5. MAIN PROGRAM
# ---------------------------------------------------------------------
# Yeh function pura program ko run karta hai - saare pieces ko jodta hai ek sequence mein
def main():
    # 1. Ask user for shape
    lengths = get_dot_pattern()         # user se poochke row-lengths ki list le li (jo bhi shape choose ki ho)
    dots, W, H = create_dots(lengths)     # us list se actual dot coordinates aur grid dimensions bana liye
    
    # 2. Setup screen
    screen = turtle.Screen()             # turtle ki drawing window (screen object) bana rahe
    screen.bgcolor("#1a1a2e")             # background color dark navy-blue jaisa set kiya - kolam traditionally floor pe banta hai isliye dark bg achha lagta hai
    screen.title("Sikku Kolam Generator (Curves, Crosses & 45° Inclined Lines)")   # window ka title set kiya
    screen.tracer(0)                        # animation off kar di (tracer 0) - taaki drawing instant ho, ek ek step slowly na dikhe (fast render ke liye)

    # 3. Draw dots
    dot_pen = turtle.Turtle()              # dots draw karne ke liye ek separate turtle (pen) object banaya
    dot_pen.hideturtle()                     # turtle ka arrow-icon hide kar diya, sirf drawing dikhni chahiye pen ka shape nahi
    draw_dots(dot_pen, dots, W, H)             # saare dots draw karne wala function call kar diya

    # 4. Draw continuous kolam lines
    line_pen = turtle.Turtle()             # lines/curves banane ke liye ek aur alag turtle object (dot_pen se alag isliye taaki color/settings clash na ho)
    line_pen.hideturtle()                    # is turtle ka bhi icon hide kar diya
    line_pen.color("#f4d35e")                 # line ka color golden-yellow set kiya - traditional kolam chalk/rice-powder jaisa look dene ke liye
    line_pen.width(3)                          # line ki thickness 3 pixels rakhi - clean visible lines ke liye
    line_pen.speed(0)                           # speed 0 ka matlab hai fastest possible speed (turtle mein 0 = no animation delay)

    draw_cells_and_boundaries(line_pen, dots, W, H)   # asli kolam design banane wala main function call kar diya - yehi saara pattern generate karta hai

    # 5. Render
    screen.update()          # tracer 0 kiya tha isliye manually update() call karna padta hai taaki jo bhi draw hua wo ek saath screen pe show ho jaye
    screen.exitonclick()      # window tab tak khuli rahegi jab tak user usme click nahi karta, click karte hi window close ho jayegi


if __name__ == "__main__":     # yeh standard Python check hai - ensure karta hai ki main() sirf tab chale jab yeh file directly run ho, kisi aur file se import hone pe automatically na chale
    main()                       # aur agar directly run ho raha hai to main() function call kar do - yahi se pura program start hota hai


# =======================================================================
# FINAL LOGIC / WORKFLOW SUMMARY (Hinglish)
# =======================================================================
#
# Poora code ek "Truchet tile" jaisi concept pe based hai - simple bhasha mein
# samjho: grid ke har chhote square (cell) mein hum ek fixed set ke curve/line
# patterns mein se koi ek randomly daal dete hain, aur jab yeh sab cells ek
# saath dekhi jaati hain to overall ek continuous, symmetric kolam design
# ban jaata hai. Neeche step-by-step flow hai:
#
# 1) get_dot_pattern() -> user se poochta hai kaisi shape chahiye (square,
#    diamond, ya custom rows), aur row-lengths ki list return karta hai.
#
# 2) create_dots() -> us list ko actual (x,y) dot coordinates mein convert
#    karta hai, aur sabko center mein align kar deta hai (offset ki wajah se).
#
# 3) grid_point() -> yeh conversion function hai jo grid-unit coordinates
#    (jaise 0,1,2...) ko actual screen pixel positions mein badalta hai, aur
#    hamesha poore design ko screen ke center mein rakhta hai.
#
# 4) draw_cells_and_boundaries() -> yeh sabse core logic hai:
#    - Poori grid ko "cells" mein todta hai (har cell 4 dots ke beech ka gap).
#    - Har cell ke liye ek random orientation choose karta hai (A, B, C, D, E)
#      jisme se A/B curves hain, C straight cross hai, aur D/E diagonal
#      45-degree lines hain.
#    - get_orientation() ek symmetry-enforcer hai - yeh ensure karta hai ki
#      grid ka left-right aur top-bottom mirror hamesha match kare (kyunki
#      asli kolams symmetric hi hote hain, random chaos nahi).
#    - Agar cell "full" hai (saare 4 corners maujood) to uske hisaab se curve/
#      cross/diagonal draw hota hai edge-midpoints ke beech.
#    - Agar cell "boundary" hai (kam corners hain, jaise diamond ke edges pe)
#      to sirf jo corners exist karte hain unke around chhota curve wrap kar
#      diya jaata hai, taaki line kahin bhi achanak toot na jaye.
#
# 5) draw_arc() aur draw_line() -> yeh dono low-level helpers hain jo actual
#    turtle pen ko move karke curve ya straight line draw karte hain.
#
# 6) main() -> sabko ek sequence mein chalata hai: pehle shape poochta hai,
#    fir dots banate hai, fir turtle screen setup karta hai, dots draw karta
#    hai, aur last mein poora kolam pattern draw karke screen ko update kar
#    deta hai.
#
# End result: har baar jab yeh script run hoga, random.choice() ki wajah se
# ek naya, unique, lekin hamesha symmetric kolam design ban jayega - bilkul
# waise hi jaise traditional sikku kolam banti hai, dots ke around ek hi
# continuous ghumti hui line se.
# =======================================================================
