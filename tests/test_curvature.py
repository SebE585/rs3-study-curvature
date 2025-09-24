import numpy as np
import math
from rs3_study_curvature.etl.compute_curvature import radius3


def test_radius_circle():
    r = 100.0
    p1 = np.array([r, 0.0])
    p2 = np.array([0.0, r])
    p3 = np.array([-r, 0.0])
    R = radius3(p1, p2, p3)
    assert math.isfinite(R) and abs(R - r) < 1e-6
