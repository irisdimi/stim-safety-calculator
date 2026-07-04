"""
Generates a static cochlear tonotopic map figure for the report, using
the Greenwood place-frequency function to assign a characteristic
frequency to each electrode contact along a spiral cochlea model.

Greenwood function (human constants):
    f = A * (10^(a*x) - k)
with A = 165.4, a = 2.1, k = 0.88, and x the fractional distance from
the apex (x=0) to the base (x=1).
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from plot_style import apply_style

apply_style()

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Greenwood constants (human)
A, a_const, k = 165.4, 2.1, 0.88


def greenwood(x):
    """Characteristic frequency (Hz) at fractional distance x from apex."""
    return A * (10 ** (a_const * x) - k)


def spiral_point(t, turns=2.6, r_max=1.0, r_min=0.14):
    """Point on a spiral. t=0 at base (outer), t=1 at apex (centre)."""
    theta = t * turns * 2 * np.pi
    r = r_max - (r_max - r_min) * t
    return r * np.cos(theta - np.pi / 2), r * np.sin(theta - np.pi / 2)


def make_figure(n_electrodes=12, insertion_depth=0.8):
    fig, ax = plt.subplots(figsize=(7.5, 6))

    # draw the cochlear spiral as a thick grey ribbon
    ts = np.linspace(0, 1, 400)
    xs, ys = zip(*[spiral_point(t) for t in ts])
    ax.plot(xs, ys, color="#B4B2A9", linewidth=13, solid_capstyle="round",
            alpha=0.45, zorder=1)

    # colour map: low freq (apex) blue -> mid orange -> high freq (base) magenta
    def freq_color(f):
        logf = np.log10(max(f, 100))
        t = np.clip((logf - 2) / (np.log10(20000) - 2), 0, 1)
        if t > 0.5:
            u = (t - 0.5) * 2
            c1, c2 = np.array([232, 135, 30]), np.array([193, 67, 109])
        else:
            u = t * 2
            c1, c2 = np.array([42, 111, 151]), np.array([232, 135, 30])
        return tuple((c1 + (c2 - c1) * u) / 255)

    # place electrode contacts
    for i in range(n_electrodes):
        frac = i / (n_electrodes - 1) if n_electrodes > 1 else 0
        t = frac * insertion_depth
        x, y = spiral_point(t)
        x_gw = 1 - t
        freq = greenwood(x_gw)
        ax.plot(x, y, "o", markersize=13, color=freq_color(freq),
                markeredgecolor="white", markeredgewidth=1.4, zorder=4)

    # label base and apex
    xb, yb = spiral_point(0)
    ax.annotate("Base\n(high freq)", xy=(xb, yb), xytext=(xb + 0.15, yb + 0.1),
                fontsize=10, color="#5F5E5A", fontweight="medium")
    xa, ya = spiral_point(1)
    ax.annotate("Apex\n(low freq)", xy=(xa, ya), xytext=(xa + 0.12, ya - 0.02),
                fontsize=10, color="#5F5E5A", fontweight="medium")

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Cochlear Tonotopic Map with Electrode Array\n"
                 f"({n_electrodes} contacts, {int(insertion_depth*100)}% insertion depth)",
                 fontsize=13, fontweight="bold")

    # colourbar-style frequency legend
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import LinearSegmentedColormap, LogNorm
    cmap = LinearSegmentedColormap.from_list(
        "tono", [(42/255, 111/255, 151/255), (232/255, 135/255, 30/255), (193/255, 67/255, 109/255)])
    sm = ScalarMappable(norm=LogNorm(vmin=greenwood(0.05), vmax=greenwood(1.0)), cmap=cmap)
    cbar = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("Characteristic frequency (Hz)", fontsize=10)

    path = os.path.join(FIGURES_DIR, "06_tonotopic_map.png")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved: {path}")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(n_electrodes=12, insertion_depth=0.8)
