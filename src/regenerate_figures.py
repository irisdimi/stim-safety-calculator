"""
Regenerates ALL project figures with a consistent, polished style.
Run this once to produce all five figures in the figures/ folder.
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(__file__))

from plot_style import apply_style, COLORS
from stim_model import threshold_current, threshold_charge, charge_density, shannon_k
from waveforms import rectangular, biphasic_symmetric, biphasic_asymmetric, biphasic_anodic_first
from leaky_integrator import find_threshold_amplitude

apply_style()

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Example configuration (shared across figures)
RHEOBASE_MA = 0.5
CHRONAXIE_US = 150
DURATION_US = 200
AREA_CM2 = 0.01
K_LIMIT = 1.5


def save(fig, name):
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    print(f"Saved: {name}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# FIGURE 1: Strength-duration curve
# ---------------------------------------------------------------------------
def fig_strength_duration():
    durations = np.linspace(CHRONAXIE_US * 0.1, CHRONAXIE_US * 10, 500)
    currents = [threshold_current(d, RHEOBASE_MA, CHRONAXIE_US) for d in durations]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(durations, currents, color=COLORS["primary"], linewidth=2.5, zorder=3)

    # rheobase asymptote
    ax.axhline(RHEOBASE_MA, color=COLORS["neutral"], linestyle="--", linewidth=1.3)
    ax.annotate(f"Rheobase = {RHEOBASE_MA} mA",
                xy=(durations[-1] * 0.98, RHEOBASE_MA),
                xytext=(durations[-1] * 0.60, RHEOBASE_MA + 0.35),
                fontsize=9.5, color=COLORS["neutral"], fontweight="medium",
                arrowprops=dict(arrowstyle="->", color=COLORS["neutral"], lw=1.1))

    # chronaxie point - label placed up and to the right, clear of the curve
    chronaxie_current = 2 * RHEOBASE_MA
    ax.plot(CHRONAXIE_US, chronaxie_current, "o", color=COLORS["danger"],
            markersize=9, zorder=5)
    ax.annotate(f"Chronaxie\n({CHRONAXIE_US} µs, 2× rheobase)",
                xy=(CHRONAXIE_US, chronaxie_current),
                xytext=(CHRONAXIE_US + 230, chronaxie_current + 1.4),
                fontsize=9.5, color=COLORS["danger"], fontweight="medium",
                ha="left",
                arrowprops=dict(arrowstyle="->", color=COLORS["danger"], lw=1.2))

    # operating point - label placed well above and to the right, separate area
    op_current = threshold_current(DURATION_US, RHEOBASE_MA, CHRONAXIE_US)
    ax.plot(DURATION_US, op_current, "*", color=COLORS["secondary"],
            markersize=18, zorder=6, markeredgecolor="white", markeredgewidth=0.8)
    ax.annotate(f"Operating point\n({DURATION_US} µs, {op_current:.3f} mA)",
                xy=(DURATION_US, op_current),
                xytext=(DURATION_US + 430, op_current + 2.6),
                fontsize=9.5, color=COLORS["secondary"], fontweight="bold",
                ha="left",
                arrowprops=dict(arrowstyle="->", color=COLORS["secondary"], lw=1.2))

    ax.set_xlabel("Pulse duration (µs)")
    ax.set_ylabel("Threshold current (mA)")
    ax.set_title("Strength–Duration Curve (Weiss/Lapicque)")
    ax.set_xlim(0, durations[-1])
    ax.set_ylim(0, max(currents) * 1.05)
    save(fig, "01_strength_duration.png")


# ---------------------------------------------------------------------------
# FIGURE 2: Shannon safety plot
# ---------------------------------------------------------------------------
def fig_shannon():
    Q_uC = np.logspace(-2, 3, 500)
    D_limit = 10 ** (K_LIMIT - np.log10(Q_uC))
    D_hist = 10 ** (1.85 - np.log10(Q_uC))

    fig, ax = plt.subplots(figsize=(7.5, 5))

    # safe region fill (below conservative line)
    ax.fill_between(Q_uC, D_limit, 1e-4, alpha=0.10, color=COLORS["safe_fill"], zorder=1)

    ax.loglog(Q_uC, D_limit, color=COLORS["danger"], linestyle="--", linewidth=2,
              label=f"Conservative limit (k = {K_LIMIT})", zorder=3)
    ax.loglog(Q_uC, D_hist, color=COLORS["neutral"], linestyle=":", linewidth=1.8,
              label="Historical Shannon limit (k = 1.85)", zorder=3)

    # operating point
    Q_th = threshold_charge(DURATION_US, RHEOBASE_MA, CHRONAXIE_US)
    Q_marker_uC = Q_th / 1000.0
    D_marker = charge_density(Q_th, AREA_CM2)
    ax.loglog(Q_marker_uC, D_marker, "*", color=COLORS["secondary"], markersize=18,
              markeredgecolor="white", markeredgewidth=0.8, zorder=6,
              label="Example configuration")

    k_val = shannon_k(Q_th, AREA_CM2)
    ax.annotate(f"Example configuration\nk = {k_val:.3f} (safe)",
                xy=(Q_marker_uC, D_marker),
                xytext=(Q_marker_uC * 0.12, D_marker * 0.12),
                fontsize=9.5, color=COLORS["secondary"], fontweight="bold",
                ha="left",
                arrowprops=dict(arrowstyle="->", color=COLORS["secondary"], lw=1.2))

    # "safe region" label
    ax.text(0.62, 0.08, "Safe region", transform=ax.transAxes,
            fontsize=11, color=COLORS["accent"], fontweight="bold", alpha=0.8)

    ax.set_xlabel("Charge per phase, Q (µC)")
    ax.set_ylabel("Charge density, D (µC/cm²)")
    ax.set_title("Shannon Safety Plot")
    ax.legend(loc="upper right")
    save(fig, "02_shannon_safety.png")


# ---------------------------------------------------------------------------
# FIGURE 3: Area sensitivity sweep
# ---------------------------------------------------------------------------
def fig_area_sweep():
    Q_th = threshold_charge(DURATION_US, RHEOBASE_MA, CHRONAXIE_US)
    areas = np.logspace(-3, 0, 300)
    k_values = [shannon_k(Q_th, a) for a in areas]

    fig, ax = plt.subplots(figsize=(7.5, 5))

    # shade safe / unsafe zones
    ax.axhspan(-1, K_LIMIT, alpha=0.08, color=COLORS["safe_fill"], zorder=1)
    ax.axhspan(K_LIMIT, 3, alpha=0.06, color=COLORS["danger"], zorder=1)

    ax.semilogx(areas, k_values, color=COLORS["primary"], linewidth=2.5, zorder=4,
                label="Shannon k-value")
    ax.axhline(K_LIMIT, color=COLORS["danger"], linestyle="--", linewidth=1.6,
               label=f"Conservative limit (k = {K_LIMIT})", zorder=3)
    ax.axhline(1.85, color=COLORS["neutral"], linestyle=":", linewidth=1.6,
               label="Historical limit (k = 1.85)", zorder=3)

    # example electrode marker
    k_example = shannon_k(Q_th, AREA_CM2)
    ax.plot(AREA_CM2, k_example, "*", color=COLORS["secondary"], markersize=18,
            markeredgecolor="white", markeredgewidth=0.8, zorder=6,
            label=f"Example electrode ({AREA_CM2} cm²)")

    ax.text(0.0012, K_LIMIT + 0.15, "Unsafe", color=COLORS["danger"],
            fontweight="bold", fontsize=10, alpha=0.8)
    ax.text(0.0012, K_LIMIT - 0.35, "Safe", color=COLORS["accent"],
            fontweight="bold", fontsize=10, alpha=0.8)

    ax.set_xlabel("Electrode area (cm²)")
    ax.set_ylabel("Shannon k-value")
    ax.set_title("Safety Margin vs. Electrode Area\n(fixed threshold charge = 175 nC)")
    ax.set_ylim(-1, 3)
    ax.legend(loc="upper right")
    save(fig, "03_area_sweep.png")


# ---------------------------------------------------------------------------
# FIGURE 4: Waveform shapes
# ---------------------------------------------------------------------------
def fig_waveform_shapes():
    pw = DURATION_US
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.6), sharey=True)

    specs = [
        ("Rectangular", rectangular, dict(duration=pw), (-pw * 0.3, pw * 1.3), COLORS["primary"]),
        ("Symmetric biphasic", biphasic_symmetric, dict(phase_duration=pw), (-pw * 0.3, pw * 2.6), COLORS["secondary"]),
        ("Asymmetric biphasic", lambda t, **k: biphasic_asymmetric(t, pw, 4.0), dict(), (-pw * 0.3, pw * 5.5), COLORS["accent"]),
        ("Anodic-first biphasic", biphasic_anodic_first, dict(phase_duration=pw), (-pw * 0.3, pw * 2.6), COLORS["danger"]),
    ]

    for ax, (title, func, kwargs, xlim, color) in zip(axes, specs):
        t = np.linspace(xlim[0], xlim[1], 600)
        y = func(t, **kwargs)
        ax.fill_between(t, y, 0, color=color, alpha=0.25, zorder=2)
        ax.plot(t, y, color=color, linewidth=2, zorder=3)
        ax.axhline(0, color="#333333", linewidth=0.8, zorder=1)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Time (µs)")
        ax.set_ylim(-1.25, 1.25)

    axes[0].set_ylabel("Normalized current")
    fig.suptitle("Stimulation Waveform Shapes", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "04_waveform_shapes.png")


# ---------------------------------------------------------------------------
# FIGURE 5: Waveform threshold comparison
# ---------------------------------------------------------------------------
def fig_waveform_comparison():
    pw = DURATION_US
    configs = {
        "Rectangular": (rectangular, dict(duration=pw), pw * 1.2, COLORS["primary"]),
        "Symmetric\nbiphasic": (biphasic_symmetric, dict(phase_duration=pw), pw * 2.4, COLORS["secondary"]),
        "Asymmetric\nbiphasic": (lambda t, **k: biphasic_asymmetric(t, pw, 4.0), dict(), pw * 5.5, COLORS["accent"]),
        "Anodic-first\nbiphasic": (biphasic_anodic_first, dict(phase_duration=pw), pw * 2.4, COLORS["danger"]),
    }

    names, amps, colors = [], [], []
    for name, (func, kwargs, sim_dur, color) in configs.items():
        amp = find_threshold_amplitude(func, RHEOBASE_MA, CHRONAXIE_US,
                                       duration_total=sim_dur, **kwargs)
        names.append(name)
        amps.append(amp)
        colors.append(color)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, amps, color=colors, width=0.62, zorder=3,
                  edgecolor="white", linewidth=1.5)

    baseline = amps[0]
    for bar, amp in zip(bars, amps):
        pct = (amp / baseline - 1) * 100
        label = f"{amp:.3f} mA"
        if abs(pct) > 1:
            label += f"\n(+{pct:.0f}%)"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, label,
                ha="center", va="bottom", fontsize=9.5, fontweight="medium")

    ax.set_ylabel("Threshold current amplitude (mA)")
    ax.set_title("Threshold Current by Waveform Shape\n(same cathodic pulse width & tissue parameters)")
    ax.set_ylim(0, max(amps) * 1.2)
    save(fig, "05_waveform_comparison.png")


if __name__ == "__main__":
    fig_strength_duration()
    fig_shannon()
    fig_area_sweep()
    fig_waveform_shapes()
    fig_waveform_comparison()
    print("\nAll figures regenerated.")
