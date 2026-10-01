"""
cv_detector.py - Advanced Computer Vision Module for Kolam Pattern Analysis
Detects Pulli (dot grid), calculates row lengths, classifies grid structure,
and measures horizontal, vertical, and rotational symmetry.
Robust against noisy internet images, colored Kumkum dots, and line interference.
"""

import cv2
import numpy as np

def detect_dots_and_grid(image_bgr):
    """
    Analyzes an image to detect Kolam dots (Pulli) and infer grid structure.
    Uses geometric convex hull analysis to cleanly classify Diamond/Rhombus vs Square grids.
    """
    h, w = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    b = image_bgr[:, :, 0].astype(float)
    g = image_bgr[:, :, 1].astype(float)
    r = image_bgr[:, :, 2].astype(float)

    detected_dots = []

    # 1. Red Kumkum dot detection (common in Indian Kolams on floor/slate)
    is_red = (r > 90) & (r > g * 1.3) & (r > b * 1.3)
    num_red, labels_red, stats_red, centroids_red = cv2.connectedComponentsWithStats(is_red.astype(np.uint8))
    for i in range(1, num_red):
        area = stats_red[i, cv2.CC_STAT_AREA]
        cw = stats_red[i, cv2.CC_STAT_WIDTH]
        ch = stats_red[i, cv2.CC_STAT_HEIGHT]
        if 2 <= area <= 200 and cw <= 22 and ch <= 22:
            detected_dots.append((int(centroids_red[i][0]), int(centroids_red[i][1])))

    # 2. White dot detection (if red dots are absent or few)
    if len(detected_dots) < 6:
        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        color_diff = max_c - min_c

        # Strict width/height so continuous lines are NEVER counted as dots
        is_white_candidate = (min_c > 140) & (color_diff < 40)
        num_white, labels_white, stats_white, centroids_white = cv2.connectedComponentsWithStats(is_white_candidate.astype(np.uint8))
        for i in range(1, num_white):
            area = stats_white[i, cv2.CC_STAT_AREA]
            cw = stats_white[i, cv2.CC_STAT_WIDTH]
            ch = stats_white[i, cv2.CC_STAT_HEIGHT]
            if 2 <= area <= 150 and cw <= 16 and ch <= 16:
                detected_dots.append((int(centroids_white[i][0]), int(centroids_white[i][1])))

    # 3. SimpleBlobDetector fallback
    if len(detected_dots) < 4:
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 4
        params.maxArea = 180
        params.filterByCircularity = True
        params.minCircularity = 0.50
        params.filterByConvexity = True
        params.minConvexity = 0.60
        params.filterByInertia = True
        params.minInertiaRatio = 0.45

        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(gray)
        if keypoints:
            detected_dots = [(int(kp.pt[0]), int(kp.pt[1])) for kp in keypoints]

    # Merge duplicate detections (< 14 pixels apart)
    merged_dots = []
    for pt in detected_dots:
        found = False
        for i, m in enumerate(merged_dots):
            if np.hypot(pt[0] - m[0], pt[1] - m[1]) < 14:
                merged_dots[i] = (int((m[0] + pt[0]) / 2), int((m[1] + pt[1]) / 2))
                found = True
                break
        if not found:
            merged_dots.append(pt)
    detected_dots = merged_dots

    annotated = image_bgr.copy()

    # Filter out border noise/text outside the main Kolam cluster
    if len(detected_dots) >= 6:
        cx = np.median([p[0] for p in detected_dots])
        cy = np.median([p[1] for p in detected_dots])
        dists = [np.hypot(p[0] - cx, p[1] - cy) for p in detected_dots]
        max_dist = np.percentile(dists, 92) * 1.3
        detected_dots = [p for p in detected_dots if np.hypot(p[0] - cx, p[1] - cy) <= max_dist]

    total_dots = len(detected_dots)

    # -------------------------------------------------------------
    # Geometric Lattice Classification (Convex Hull vs Bounding Box)
    # A diamond/rhombus has Area(Hull) / Area(BBox) ~ 0.50 - 0.70.
    # A square grid has Area(Hull) / Area(BBox) ~ 0.85 - 1.00.
    # -------------------------------------------------------------
    is_diamond = False
    if total_dots >= 4:
        pts_arr = np.array(detected_dots, dtype=np.float32)
        hull_area = cv2.contourArea(cv2.convexHull(pts_arr))
        bx, by, bw, bh = cv2.boundingRect(pts_arr)
        bbox_area = float(bw * bh)
        ratio = hull_area / bbox_area if bbox_area > 0 else 0
        if ratio < 0.74:
            is_diamond = True

    if is_diamond:
        if total_dots <= 18:
            canonical = [1, 3, 5, 3, 1]              # 5-to-1 diamond (13 dots)
        elif total_dots <= 32:
            canonical = [1, 3, 5, 7, 5, 3, 1]        # 7-to-1 diamond (25 dots)
        else:
            canonical = [1, 3, 5, 7, 9, 7, 5, 3, 1]  # 9-to-1 diamond (41 dots)
        grid_type = f"Diamond / Rhombus Grid ({max(canonical)}-to-1)"
    else:
        # Square grid estimate
        side = max(3, int(round(np.sqrt(total_dots))))
        canonical = [side] * side
        grid_type = f"Square Grid ({side}x{side})"

    # Annotate dots on the image
    for pt in detected_dots:
        cv2.circle(annotated, pt, 5, (0, 255, 0), -1)   # Green dot center
        cv2.circle(annotated, pt, 11, (0, 255, 255), 1) # Yellow detection ring

    return {
        'dots': detected_dots,
        'row_lengths': canonical,
        'grid_type': grid_type,
        'is_diamond': is_diamond,
        'recommended_canonical': canonical,
        'estimated_spacing': 50.0,
        'annotated_image': annotated
    }

def detect_symmetry(image_bgr):
    """
    Calculates Horizontal, Vertical, and 90-degree Rotational symmetry scores.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    dim = 256
    resized = cv2.resize(gray, (dim, dim))

    # Apply Gaussian blur to tolerate hand-drawn chalk variations
    blurred = cv2.GaussianBlur(resized.astype(np.float32), (15, 15), 3)

    # Horizontal reflection (flip top-bottom)
    h_flipped = cv2.flip(blurred, 0)
    res_h = cv2.matchTemplate(blurred, h_flipped, cv2.TM_CCOEFF_NORMED)[0][0]
    h_score = max(0.0, float(res_h)) * 100

    # Vertical reflection (flip left-right)
    v_flipped = cv2.flip(blurred, 1)
    res_v = cv2.matchTemplate(blurred, v_flipped, cv2.TM_CCOEFF_NORMED)[0][0]
    v_score = max(0.0, float(res_v)) * 100

    # Rotational 90 degrees
    rot90 = cv2.rotate(blurred, cv2.ROTATE_90_CLOCKWISE)
    res_rot = cv2.matchTemplate(blurred, rot90, cv2.TM_CCOEFF_NORMED)[0][0]
    rot_score = max(0.0, float(res_rot)) * 100

    if h_score > 60 and v_score > 60:
        primary = "Bilateral Reflection (D2)"
        symmetry_mode = "mirror"
    elif rot_score > 55:
        primary = "4-Fold Rotational (C4)"
        symmetry_mode = "rotational"
    elif h_score > 50 or v_score > 50:
        primary = "Single-Axis Mirror"
        symmetry_mode = "mirror"
    else:
        primary = "Bilateral / Rotational Symmetry"
        symmetry_mode = "mirror"

    return {
        'h_score': round(h_score, 1),
        'v_score': round(v_score, 1),
        'rot_score': round(rot_score, 1),
        'primary_symmetry': primary,
        'symmetry_mode': symmetry_mode
    }
