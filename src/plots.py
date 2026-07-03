"""
Generates the two standard plots used to visualize stimulation safety:

1. Strength-duration curve - current needed to reach threshold, across
   a range of pulse durations.
2. Shannon safety plot - charge density vs. charge per phase, on a
   log-log scale, with the safety boundary line drawn in.
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from stim_model import threshold_current, threshold_charge, charge_density

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def save(fig, name):
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved: {path}")
    plt.close(fig)


def plot_strength_duration(rheobase_mA: float, chronaxie_us: float, marker_duration_us: float = None):
    """
    Plots current threshold vs. pulse duration. Short pulses need more
    current; long pulses approach the rheobase (the floor). The
    chronaxie point (where current = 2x rheobase) is marked.
    """
    durations = np.linspace(chronaxie_us * 0.1, chronaxie_us * 10, 500)
    currents = [threshold_current(d, rheobase_mA, chronaxie_us) for d in durations]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(durations, currents, color="tab:blue", label="Strength-duration curve")
    ax.axhline(rheobase_mA, color="gray", linestyle="--", label=f"Rheobase = {rheobase_mA} mA")
    ax.axvline(chronaxie_us, color="gray", linestyle=":", label=f"Chronaxie = {chronaxie_us} us")
    ax.plot(chronaxie_us, 2 * rheobase_mA, "ko", label="Chronaxie point (2x rheobase)")

    if marker_duration_us is not None:
        marker_current = threshold_current(marker_duration_us, rheobase_mA, chronaxie_us)
        ax.plot(marker_duration_us, marker_current, "r*", markersize=15,
                 label=f"Your setup ({marker_duration_us} us)")

    ax.set_xlabel("Pulse duration (us)")
    ax.set_ylabel("Threshold current (mA)")
    ax.set_title("Strength-Duration Curve (Weiss/Lapicque)")
    ax.legend()
    save(fig, "01_strength_duration.png")


def plot_shannon(area_cm2: float, k_limit: float = 1.5, marker_charge_nC: float = None):
    """
    Plots the Shannon safety boundary: charge density (D) vs. charge
    per phase (Q) on log-log axes, with the k_limit boundary line
    drawn in. Points BELOW the line are in the safe region.
    """
    Q_uC = np.logspace(-2, 3, 500)  # charge per phase, uC, wide range
    D = 10 ** (k_limit - np.log10(Q_uC))  # boundary line: log(D) = k - log(Q)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(Q_uC, D, color="red", linestyle="--", label=f"Safety limit (k={k_limit})")
    ax.fill_between(Q_uC, D, 1e-3, alpha=0.1, color="green", label="Safe region")

    if marker_charge_nC is not None:
        Q_marker_uC = marker_charge_nC / 1000.0
        D_marker = charge_density(marker_charge_nC, area_cm2)
        ax.loglog(Q_marker_uC, D_marker, "ko", markersize=10, label="Your setup")

    ax.set_xlabel("Charge per phase, Q (uC)")
    ax.set_ylabel("Charge density, D (uC/cm^2)")
    ax.set_title("Shannon Safety Plot")
    ax.legend()
    save(fig, "02_shannon_safety.png")
