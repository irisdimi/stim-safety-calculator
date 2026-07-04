"""
Interactive command-line version: prompts you for parameters, runs the
evaluation, prints results, and generates both plots marked with your
specific setup.

Run this instead of main.py to type in your own numbers
each time rather than editing example values in code.
"""

from stim_model import evaluate_stimulation
from plots import plot_strength_duration, plot_shannon


def ask_float(prompt: str, default: float) -> float:
    raw = input(f"{prompt} [default: {default}]: ").strip()
    return float(raw) if raw else default


def main():
    print("=== Neural Stimulation Safety Calculator ===\n")
    print("Enter your stimulation parameters (press Enter to use the default shown).\n")

    duration_us = ask_float("Pulse duration (us)", 200)
    rheobase_mA = ask_float("Rheobase current (mA)", 0.5)
    chronaxie_us = ask_float("Chronaxie (us)", 150)
    area_cm2 = ask_float("Electrode area (cm^2)", 0.01)
    k_limit = ask_float("Safety limit k (1.5 = conservative, 1.85 = Shannon limit)", 1.5)

    results = evaluate_stimulation(duration_us, rheobase_mA, chronaxie_us, area_cm2, k_limit)

    print("\n--- Results ---")
    print(f"Threshold current:    {results['threshold_current_mA']:.4f} mA")
    print(f"Threshold charge:     {results['threshold_charge_nC']:.4f} nC")
    print(f"Charge density:       {results['charge_density_uC_cm2']:.4f} uC/cm^2")
    print(f"Shannon k-value:      {results['shannon_k']:.4f}  (limit: {k_limit})")
    verdict = "SAFE" if results["is_safe"] else "UNSAFE - exceeds safety limit"
    print(f"Verdict:              {verdict}")

    print("\n--- Generating plots ---")
    plot_strength_duration(rheobase_mA, chronaxie_us, marker_duration_us=duration_us)
    plot_shannon(area_cm2, k_limit, marker_charge_nC=results["threshold_charge_nC"])
    print("\nDone. Check the figures/ folder.")


if __name__ == "__main__":
    main()
