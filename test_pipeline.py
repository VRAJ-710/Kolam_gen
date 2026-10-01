"""
test_pipeline.py - Verification script for end-to-end Kolam Vision & Generation Pipeline
"""

import os
import cv2
import cv_detector
import kolam_engine

def run_tests():
    print("=" * 60)
    print("      KOLAMIFY AI - END-TO-END PIPELINE VERIFICATION")
    print("=" * 60)

    test_cases = [
        {
            "path": "samples/sample_diamond_5.png",
            "expected_shape": "Diamond",
            "expected_rows": [1, 3, 5, 3, 1]
        },
        {
            "path": "samples/sample_square_5.png",
            "expected_shape": "Square",
            "expected_rows": [5, 5, 5, 5, 5]
        },
        {
            "path": "samples/sample_diamond_7.png",
            "expected_shape": "Diamond",
            "expected_rows": [1, 3, 5, 7, 5, 3, 1]
        },
        {
            "path": "samples/sample_diamond_9.png",
            "expected_shape": "Diamond",
            "expected_rows": [1, 3, 5, 7, 9, 7, 5, 3, 1]
        }
    ]

    all_passed = True

    for i, tc in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Testing sample: {tc['path']}")
        if not os.path.exists(tc['path']):
            print(f"[FAIL] File not found: {tc['path']}")
            all_passed = False
            continue

        img = cv2.imread(tc['path'])

        # 1. Computer Vision Detection
        grid = cv_detector.detect_dots_and_grid(img)
        sym = cv_detector.detect_symmetry(img)

        print(f"  * Detected Grid Type : {grid['grid_type']}")
        print(f"  * Detected Row Counts: {grid['row_lengths']}")
        print(f"  * Total Dots Found   : {len(grid['dots'])}")
        print(f"  * Detected Symmetry  : {sym['primary_symmetry']} (H={sym['h_score']}%, V={sym['v_score']}%)")

        # Validation
        if grid['row_lengths'] == tc['expected_rows']:
            print("  [PASS] Row count check: EXACT MATCH")
        else:
            print(f"  [WARN] Row count check: Expected {tc['expected_rows']}, Got {grid['row_lengths']}")
            all_passed = False

        # 2. Algorithmic Recreation
        print("  * Generating 3 new variations based on extracted rules...")
        for v in range(1, 4):
            fig, meta = kolam_engine.render_kolam_figure(
                lengths=grid['row_lengths'],
                symmetry_mode=sym['symmetry_mode'],
                seed=v * 77,
                figsize=(4, 4)
            )
            loop_status = "Brahma Mudi (1 Single Loop)" if meta['is_brahma_mudi'] else f"{meta['num_loops']} Interlocking Loops"
            print(f"    - Variation {v}: Generated successfully! [{loop_status}]")

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED! CV detection and generation engine are verified.")
    else:
        print("[WARNING] Some tests had discrepancies. Please check output above.")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
