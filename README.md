# 🌸 Kolamify AI - Autonomous Kolam Pattern Analysis & Recreation

> **Smart India Hackathon (SIH) Project**  
> **Theme:** Heritage & Culture | Computer Vision & Generative Algorithms  
> **Problem Statement:** *Detect symmetry and pattern rules from sample Kolam designs and generate new designs following those rules.*

---

## 📌 Project Overview
Kolam is a traditional geometric line drawing practiced across South India, where continuous looping lines (*Sikku* / *Kambi*) weave gracefully around a grid of dots (*Pulli*) without touching or crossing them. 

This project bridges **Computer Vision (OpenCV)** and **Generative Graph / Truchet Knot Theory** into an autonomous pipeline:
1. **Perception (OpenCV):** Automatically detects dot grids (*Pulli*), clusters row counts, classifies grid shapes (Square, Diamond, Custom), and scores reflection / rotational symmetries.
2. **Synthesis (Generative Engine):** Uses tile-knot grammars with enforced bilateral mirror symmetry ($D_2$) and rotational symmetry ($C_4$) to synthesize brand-new, mathematically compliant, continuous Kolam patterns.
3. **Cultural & Graph Theory Metric:** Analyzes line paths to detect **Brahma Mudi** (single unbroken Eulerian loops) vs interlocking multi-loops.

---

## 🚀 Key Features

* **Dual-Mode Dot Detector (`cv_detector.py`):**
  * Robustly extracts dots from traditional dark-floor chalk/rice-powder Kolams and paper sketches using HSV thresholding and adaptive contour filtering.
  * Measures spatial row lengths (e.g., `[1, 3, 5, 7, 5, 3, 1]` for diamond grids, `[5, 5, 5, 5, 5]` for square grids).
* **Symmetry Scoring Engine:**
  * Quantifies horizontal reflection, vertical reflection, and $90^\circ$ rotational symmetry using normalized cross-correlation and dihedral group ($D_2 / C_4$) checks.
* **Truchet-Knot Generative Engine (`kolam_engine.py`):**
  * Implements Paulus Gerdes' Mirror-Curve and Truchet knot algorithms with guaranteed coordinate midpoint alignment.
  * Enforces reflective symmetry folding across fundamental quadrants ($5^{(W \cdot H / 4)}$ design spaces).
* **Brahma Mudi Loop Analyzer:**
  * Performs topological cycle analysis on edge midpoints to check whether the resulting pattern is a single unbroken Eulerian loop (*Brahma Mudi*) or interlocking links.
* **Interactive 3D Accordion Showcase:**
  * Uses GSAP 3 with hardware-accelerated 3D perspective (`perspective: 1400px`, `rotateY: ±8°`) and parallax drift.
  * Responsive hover/click expansion to 52% gallery width with real-time Eulerian cycle badge indicators.
* **Real-Time Vector Stroke Animator:**
  * Simulates the sacred hand gesture of dropping rice flour continuously using dynamic SVG path interpolation.
* **Traditional Color Palettes:**
  * *Traditional Rice Powder*, *Temple Saffron & Gold*, *Midnight Indigo*, and *Terracotta Dawn*.

---

## 🛠️ Architecture Pipeline

```text
┌─────────────────────────┐
│   Source Kolam Image    │ (Photo / Upload / Preset Benchmark)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       cv_detector       │ • Multi-channel Dot Extraction & Noise Suppression
│     (Computer Vision)   │ • Convex Hull Classification (Square vs Diamond)
└────────────┬────────────┘ • Symmetry Correlation (Bilateral D2 / Rotational C4)
             │
             ▼ Extracted Rule Vector:
             │ { grid_type: "Diamond", rows: [1, 3, 5, 7, 5, 3, 1], symmetry: "mirror" }
             │
             ▼
┌─────────────────────────┐
│      kolam_engine       │ • Curve-Dominant Truchet Knot Tile Allocation
│  (Algorithmic Synthesis)│ • Bilateral / Rotational Quadrant Folding
└────────────┬────────────┘ • Brahma Mudi (Eulerian Cycle) Graph Analysis
             │
             ▼
┌─────────────────────────┐
│    Interactive Studio   │ • 3D Perspective Accordion Gallery (GSAP 3)
│   (Streamlit + Canvas)  │ • Vector Stroke-Drawing Animator (SVG)
└─────────────────────────┘ • Instant High-Res PNG / SVG Export
```

---

## 💻 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/VRAJ-710/Kolam_gen.git
cd Kolam_gen
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
Verify that the computer vision and generation engines pass all tests:
```bash
python test_pipeline.py
```

### 4. Launch the Web Studio
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```text
Kolam_gen/
├── app.py              # Streamlit Web Application (High-Performance Pitch Studio)
├── cv_detector.py      # OpenCV Computer Vision Module (Dot grid & Symmetry extraction)
├── kolam_engine.py     # Generative Engine (Knot Theory, Truchet Tiles, SVG & 3D Accordion)
├── test_pipeline.py    # Automated Verification Suite (CV & Engine Unit Tests)
├── requirements.txt    # Python Dependencies (Cloud-Optimized)
├── packages.txt        # Linux System Dependencies (libgl1, libglib)
├── samples/            # Curated Benchmark Kolam Samples
│   ├── sample_diamond_5.png   # 5-to-1 Diamond Grid (13 dots)
│   ├── sample_diamond_7.png   # 7-to-1 Diamond Grid (25 dots)
│   ├── sample_diamond_9.png   # 9-to-1 Diamond Grid (41 dots)
│   └── sample_square_5.png    # 5x5 Square Matrix (25 dots)
└── README.md           # Technical Documentation & Architecture Specification
```

---

## 📚 Academic Foundations & References

The mathematical models and algorithmic rules implemented in this project are grounded in published ethnomathematics, knot theory, and computational craft research:

1. **The 5 Axiomatic Rules of Pulli / Sikku Kolam:**
   - **Marcia Ascher (2002)**, *"The Kolam Tradition: A tradition of figure-drawing in southern India expresses mathematical ideas and has attracted the attention of computer science"*, *American Scientist*, Vol. 90, No. 1, pp. 56–63.
   - Formulates the 5 canonical structural constraints: *(1) Obstacle Rule, (2) Continuity Rule (Eulerian Circuit), (3) Completeness Rule, (4) Smoothness Rule, (5) Diagonal Rule*.

2. **Data Physicalization & Parametric Kolam Grammars:**
   - **Shri Harini Ramesh & Fateme Rajabiyazdi (University of Calgary, Canada)**, *"Pulli Kolam: A Traditional South Indian Craft Practice for Representing Data"*.
   - Explores parametric mappings of Pulli Kolam across dot pressure/size, multi-pattern generation over identical lattices, line styles (single vs. double *Kambi*), and natural pigment palettes (turmeric, kumkum, rice flour).

3. **Mirror-Curve Algorithms & Lunda Designs:**
   - **Paulus Gerdes (1990)**, *"Lunda Geometry: Designs, Polyominoes, Patterns, Symmetries"*, Universidade Pedagógica, Maputo.
   - Establishes the matrix-based mirror-curve tracing algorithm governing Eulerian loop closures across orthogonal dot matrices.

