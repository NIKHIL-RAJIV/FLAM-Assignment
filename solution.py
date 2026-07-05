import numpy as np
import pandas as pd
from scipy.optimize import least_squares

df = pd.read_csv("xy_data.csv")

new_columns = []
for c in df.columns:
    new_columns.append(c.strip().lower())
df.columns = new_columns

x = df["x"].to_numpy(dtype=float)
y = df["y"].to_numpy(dtype=float)

if "t" in df.columns:
    t = df["t"].to_numpy(dtype=float)
else:
    t = None


def residuals_rot(p):
    theta, M, X = p
    dx = x - X
    dy = y - 42.0
    u = dx * np.cos(theta) + dy * np.sin(theta)
    v = -dx * np.sin(theta) + dy * np.cos(theta)
    return v - np.exp(M * u) * np.sin(0.3 * u)


def residuals_direct(p):
    theta, M, X = p
    e = np.exp(M * t) * np.sin(0.3 * t)
    xp = t * np.cos(theta) - e * np.sin(theta) + X
    yp = 42.0 + t * np.sin(theta) + e * np.cos(theta)
    return np.concatenate([xp - x, yp - y])


if t is not None:
    resid = residuals_direct
else:
    resid = residuals_rot

theta_min = 0.0
theta_max = np.deg2rad(50.0)
M_min = -0.05
M_max = 0.05
X_min = 0.0
X_max = 100.0

lower_bounds = [theta_min, M_min, X_min]
upper_bounds = [theta_max, M_max, X_max]

best = None
for th0 in np.deg2rad(np.arange(2, 50, 4)):
    for X0 in range(5, 100, 8):
        for M0 in (-0.03, 0.0, 0.03):
            try:
                r = least_squares(resid, [th0, M0, X0], bounds=(lower_bounds, upper_bounds))
            except Exception:
                continue
            if best is None:
                best = r
            elif r.cost < best.cost:
                best = r

theta = best.x[0]
M = best.x[1]
X = best.x[2]

n = len(x)
rms = np.sqrt(2 * best.cost / n)

print("=" * 40)
print(f"theta = {np.rad2deg(theta):.6f} deg  ({theta:.6f} rad)")
print(f"M     = {M:.6f}")
print(f"X     = {X:.6f}")
print(f"residual cost = {best.cost:.3e}   RMS = {rms:.3e}")
print("=" * 40)
