"""
Runs the calculator with example parameters (a rough cochlear implant
electrode setup). Useful for a quick check that everything works.
"""

from stim_model import evaluate_stimulation
from plots import plot_strength_duration, plot_shannon

# Example parameters - a rough cochlear implant electrode setup.
# Edit these directly, or use interactive.py to type them in each run.
DURATION_US = 200      # pulse duration
RHEOBASE_MA = 0.5       # rheobase current
CHRONAXIE_US = 150      # chronaxie
AREA_CM2 = 0.01         # electrode area
K_LIMIT = 1.5           # safety limit (1.5 = conservative, 1.85 = Shannon limit)


def run():
    results = evaluate_stimulation(DURATION_US, RHEOBASE_MA, CHRONAXIE_US, AREA_CM2, K_LIMIT)

    print("--- Neural Stimulation Safety Calculator ---")
    print(f"Pulse duration:       {DURATION_US} us")
    print(f"Rheobase:             {RHEOBASE_MA} mA")
    print(f"Chronaxie:            {CHRONAXIE_US} us")
    print(f"Electrode area:       {AREA_CM2} cm^2")
    print()
    print(f"Threshold current:    {results['threshold_current_mA']:.4f} mA")
    print(f"Threshold charge:     {results['threshold_charge_nC']:.4f} nC")
    print(f"Charge density:       {results['charge_density_uC_cm2']:.4f} uC/cm^2")
    print(f"Shannon k-value:      {results['shannon_k']:.4f}  (limit: {K_LIMIT})")
    verdict = "SAFE" if results["is_safe"] else "UNSAFE - exceeds safety limit"
    print(f"Verdict:              {verdict}")

    plot_strength_duration(RHEOBASE_MA, CHRONAXIE_US, marker_duration_us=DURATION_US)
    plot_shannon(AREA_CM2, K_LIMIT, marker_charge_nC=results["threshold_charge_nC"])


if __name__ == "__main__":
    run()
