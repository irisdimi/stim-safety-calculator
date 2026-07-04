"""
Core equations for neural stimulation safety analysis.

Two models, working together:

1. STRENGTH-DURATION CURVE (Weiss/Lapicque)
   Tells you the minimum current needed to trigger a neural response,
   given how long your stimulation pulse lasts.

       I_th(d) = I_rh * (1 + chronaxie / d)

   where:
     I_rh       = rheobase current (minimum current for an infinitely
                  long pulse - the "floor")
     chronaxie  = pulse duration at which threshold current = 2 * I_rh
                  (a measure of how "excitable" the tissue is)
     d          = pulse duration

2. SHANNON SAFETY MODEL (1992)
   Tells you the maximum safe charge you can deliver through an
   electrode before risking tissue damage, based on charge density
   (charge per unit electrode area).

       log10(D) = k - log10(Q)

   where:
     D = charge density (uC/cm^2) = Q / electrode_area
     Q = charge per phase (uC)
     k = empirical safety constant. k ~ 1.85 is the historical
         "Shannon limit" derived from animal studies; k ~ 1.5 is
         often used clinically for a safety margin. ADJUST THESE
         to match your lecture notes if they use different constants.


"""

import math


def threshold_current(duration_us: float, rheobase_mA: float, chronaxie_us: float) -> float:
    """
    Minimum current (mA) needed to trigger a response for a pulse of
    a given duration, using the Weiss/Lapicque strength-duration model.
    """
    return rheobase_mA * (1 + chronaxie_us / duration_us)


def threshold_charge(duration_us: float, rheobase_mA: float, chronaxie_us: float) -> float:
    """
    Minimum charge per phase (nC) needed at threshold, for a pulse of
    a given duration. Charge = current * time.

    Q_th(d) = I_th(d) * d = I_rh * (d + chronaxie)

    Units: mA * us = nC (nanocoulombs), since 1 mA * 1 us = 1 nC.
    """
    return rheobase_mA * (duration_us + chronaxie_us)


def charge_density(charge_nC: float, area_cm2: float) -> float:
    """
    Charge density (uC/cm^2) = charge / electrode area.
    Converts nC -> uC (divide by 1000) as part of the calculation.
    """
    charge_uC = charge_nC / 1000.0
    return charge_uC / area_cm2


def shannon_k(charge_nC: float, area_cm2: float) -> float:
    """
    Computes the Shannon k-value for a given charge and electrode area:

        k = log10(D) + log10(Q)

    where D is charge density (uC/cm^2) and Q is charge per phase (uC).
    Compare this against a safety limit (e.g. k_limit=1.5 or 1.85) -
    LOWER k means SAFER (below the boundary line on a log-log plot).
    """
    charge_uC = charge_nC / 1000.0
    D = charge_density(charge_nC, area_cm2)
    if charge_uC <= 0 or D <= 0:
        raise ValueError("Charge and charge density must be positive.")
    return math.log10(D) + math.log10(charge_uC)


def is_safe(charge_nC: float, area_cm2: float, k_limit: float = 1.5) -> bool:
    """
    Returns True if the given charge/area combination falls within the
    safe region (k below k_limit), False otherwise.
    """
    return shannon_k(charge_nC, area_cm2) < k_limit


def evaluate_stimulation(
    duration_us: float,
    rheobase_mA: float,
    chronaxie_us: float,
    area_cm2: float,
    k_limit: float = 1.5,
):
    """
    Runs the full evaluation for a given stimulation setup: computes
    threshold current/charge, charge density, Shannon k-value, and a
    safe/unsafe verdict. Returns a dictionary of all results, useful
    both for printing and for feeding into plots.
    """
    I_th = threshold_current(duration_us, rheobase_mA, chronaxie_us)
    Q_th = threshold_charge(duration_us, rheobase_mA, chronaxie_us)
    D_th = charge_density(Q_th, area_cm2)
    k = shannon_k(Q_th, area_cm2)
    safe = k < k_limit

    return {
        "duration_us": duration_us,
        "rheobase_mA": rheobase_mA,
        "chronaxie_us": chronaxie_us,
        "area_cm2": area_cm2,
        "threshold_current_mA": I_th,
        "threshold_charge_nC": Q_th,
        "charge_density_uC_cm2": D_th,
        "shannon_k": k,
        "k_limit": k_limit,
        "is_safe": safe,
    }
