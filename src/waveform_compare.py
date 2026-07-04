"""
Compares threshold current and charge across different stimulation
waveforms, for the same rheobase/chronaxie tissue parameters.

Also validates the leaky-integrator model against the algebraic
Weiss/Lapicque formula for the rectangular case, where both should
approximately agree, a useful sanity check that the simulation is
behaving correctly before trusting it for waveforms with no closed
form.
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from waveforms import rectangular, biphasic_symmetric, biphasic_asymmetric, biphasic_anodic_first
from leaky_integrator import find_threshold_amplitude, simulate_membrane, tau_m_from_chronaxie
from stim_model import threshold_current

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def save(fig, name):
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved: {path}")
    plt.close(fig)


def validate_against_algebraic_formula(rheobase_mA, chronaxie_us, duration_us):
    """
    Sanity check: for a rectangular pulse, compares the leaky-integrator
    simulation's threshold current against the direct algebraic
    Weiss/Lapicque formula. They should be close (same underlying
    phenomenon, different classical approximations).
    """
    algebraic = threshold_current(duration_us, rheobase_mA, chronaxie_us)
    simulated = find_threshold_amplitude(
        rectangular, rheobase_mA, chronaxie_us,
        duration_total=duration_us * 1.2, duration=duration_us
    )
    print(f"Validation (rectangular, {duration_us} us pulse):")
    print(f"  Algebraic (Weiss/Lapicque):  {algebraic:.4f} mA")
    print(f"  Simulated (RC model):        {simulated:.4f} mA")
    print(f"  Difference:                  {abs(algebraic - simulated) / algebraic * 100:.1f}%\n")


def compare_waveforms(rheobase_mA, chronaxie_us, pulse_width_us):
    """
    Computes threshold current and cathodic-phase charge for each
    waveform type, using the same pulse width for a fair comparison.
    """
    configs = {
        "Rectangular\n(not charge-balanced)": (
            rectangular, dict(duration=pulse_width_us), pulse_width_us * 1.2
        ),
        "Symmetric biphasic\n(charge-balanced)": (
            biphasic_symmetric, dict(phase_duration=pulse_width_us), pulse_width_us * 2.4
        ),
        "Asymmetric biphasic\n(charge-balanced, 4x ratio)": (
            biphasic_asymmetric, dict(cathodic_duration=pulse_width_us, anodic_ratio=4.0), pulse_width_us * 5.5
        ),
        "Anodic-first biphasic\n(reversed phase order)": (
            biphasic_anodic_first, dict(phase_duration=pulse_width_us), pulse_width_us * 2.4
        ),
    }

    results = {}
    for name, (func, kwargs, sim_duration) in configs.items():
        amplitude = find_threshold_amplitude(
            func, rheobase_mA, chronaxie_us, duration_total=sim_duration, **kwargs
        )
        charge_nC = amplitude * pulse_width_us  # cathodic phase charge only
        results[name] = {"amplitude_mA": amplitude, "charge_nC": charge_nC,
                          "func": func, "kwargs": kwargs, "sim_duration": sim_duration}
    return results


def plot_waveform_shapes(pulse_width_us):
    """
    Shows what each waveform actually looks like, side by side, so the
    shapes are visually clear before looking at the threshold results.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), sharey=True)

    t1 = np.linspace(-pulse_width_us * 0.3, pulse_width_us * 1.3, 500)
    axes[0].plot(t1, rectangular(t1, pulse_width_us), color="tab:blue")
    axes[0].set_title("Rectangular")

    t2 = np.linspace(-pulse_width_us * 0.3, pulse_width_us * 2.6, 500)
    axes[1].plot(t2, biphasic_symmetric(t2, pulse_width_us), color="tab:orange")
    axes[1].set_title("Symmetric biphasic")

    t3 = np.linspace(-pulse_width_us * 0.3, pulse_width_us * 5.5, 500)
    axes[2].plot(t3, biphasic_asymmetric(t3, pulse_width_us, anodic_ratio=4.0), color="tab:green")
    axes[2].set_title("Asymmetric biphasic")

    for ax in axes:
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.set_xlabel("Time (us)")
    axes[0].set_ylabel("Normalized current")

    fig.suptitle("Stimulation Waveform Shapes")
    fig.tight_layout()
    save(fig, "04_waveform_shapes.png")


def plot_comparison(results):
    """
    Bar chart comparing threshold current across the three waveforms -
    the key result showing charge-balancing's cost in current efficiency.
    """
    names = list(results.keys())
    amplitudes = [results[n]["amplitude_mA"] for n in names]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(names, amplitudes, color=["tab:blue", "tab:orange", "tab:green"])
    ax.set_ylabel("Threshold current amplitude (mA)")
    ax.set_title("Threshold Current by Waveform Shape\n(same cathodic pulse width, same tissue parameters)")
    for bar, amp in zip(bars, amplitudes):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{amp:.3f}",
                 ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    save(fig, "05_waveform_comparison.png")


if __name__ == "__main__":
    RHEOBASE_MA = 0.5
    CHRONAXIE_US = 150
    PULSE_WIDTH_US = 200

    validate_against_algebraic_formula(RHEOBASE_MA, CHRONAXIE_US, PULSE_WIDTH_US)

    plot_waveform_shapes(PULSE_WIDTH_US)

    results = compare_waveforms(RHEOBASE_MA, CHRONAXIE_US, PULSE_WIDTH_US)
    print("--- Waveform Comparison ---")
    for name, r in results.items():
        clean_name = name.replace("\n", " ")
        print(f"{clean_name}:")
        print(f"  Threshold current: {r['amplitude_mA']:.4f} mA")
        print(f"  Cathodic charge:   {r['charge_nC']:.4f} nC\n")

    plot_comparison(results)
