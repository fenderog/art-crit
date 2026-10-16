"""Shared layout constants (metres, +X right, +Y away from camera, +Z up)."""
from mathutils import Vector

COUNTER_TOP = 1.0
COUNTER_FRONT_Y = -0.95        # front face of the counter
COUNTER_BACK_Y = -0.20
FLOOR_Z = 0.06                 # top of the wooden floor inside the booth

OCT_X, OCT_Y = 0.0, 0.30       # octopus axis

STOVE_TOP = 0.95
NOODLE_POT = Vector((-0.78, 0.18, STOVE_TOP))   # base centre
NOODLE_POT_R, NOODLE_POT_H = 0.21, 0.30
STOCK_POT = Vector((-1.18, 0.64, STOVE_TOP))
STOCK_POT_R, STOCK_POT_H = 0.22, 0.42

BOARD = Vector((0.98, -0.42, COUNTER_TOP))      # cutting board centre (on counter)
HELD_BOWL = Vector((0.66, -0.52, 1.62))         # base centre of the bowl presented by the octopus

# ---- handled utensils (world space) -------------------------------------------------------------
from mathutils import Matrix, Euler
from math import radians

TEBO_C = NOODLE_POT + Vector((0, 0, 0.40))                     # centre of basket rim
TEBO_DIR = Vector((0.35, -0.15, 0.92)).normalized()
TEBO_R = 0.108
TEBO_S = TEBO_C + Vector((TEBO_R, 0, 0.012))                    # handle start (basket rim)
TEBO_LEN = 0.60

LADLE_R = 0.095
LADLE_C = Vector((-1.12, 0.60, 1.53))                          # ladle bowl centre
LADLE_DIR = Vector((0.93, -0.12, 0.30)).normalized()
LADLE_S = LADLE_C + LADLE_DIR * LADLE_R
LADLE_LEN = 0.56

KNIFE_O = BOARD + Vector((-0.10, 0.0, 0.078))                   # blade centre / pivot
KNIFE_M = Matrix.Translation(KNIFE_O) @ Euler((0, radians(-20), 0), 'XYZ').to_matrix().to_4x4()
KNIFE_H0 = KNIFE_M @ Vector((0.10, 0, 0.060))                   # handle start
KNIFE_H1 = KNIFE_M @ Vector((0.25, 0, 0.060))                   # handle end
