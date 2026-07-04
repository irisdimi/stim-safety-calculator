"""
Generalizes threshold-finding to ARBITRARY current waveforms, using
the RC "leaky integrator" model of a neuron membrane - the same
underlying physics Lapicque used to originally derive the
strength-duration relationship, just applied here to non-rectangular
pulses where no simple algebraic formula exists.

THE MODEL:
A neuron membrane charges toward threshold like a capacitor being
charged through a resistor:

    dV/dt = (I(t) - V/R) / C

Normalizing R=1 (we only care about relative current thresholds),
this simplifies to:

    dV/dt = (I(t) - V) / tau_m

where tau_m = R*C is the membrane time constant. The neuron fires
when V reaches a threshold voltage V_th.

CONNECTING TO CHRONAXIE:
For a simple rectangular pulse, this model has a closed-form solution,
and solving for when threshold current = 2x rheobase (the definition
of chronaxie) gives:

    tau_m = chronaxie / ln(2)

This lets us derive tau_m directly from the chronaxie value already
used elsewhere in this project, so results stay consistent with the
Weiss/Lapicque parameters you're already using.

NOTE: This RC/exponential model and the algebraic Weiss hyperbolic
formula (used in stim_model.py) are two DIFFERENT classical
approximations of the same real strength-duration behaviour. They
agree closely but not exactly. We need this RC formulation here
specifically because it lets us simulate non-rectangular waveforms,
which the algebraic formula cannot handle.
"""

import numpy as np


def tau_m_from_chronaxie(chronaxie_us: float) -> float:
    """Converts chronaxie to the equivalent membrane time constant."""
    return chronaxie_us / np.log(2)


def simulate_membrane(waveform_func, duration_total: float, amplitude: float,
                       tau_m: float, dt: float = 0.5, **waveform_kwargs) -> np.ndarray:
    """
    Simulates membrane voltage V(t) in response to a given current
    waveform, using simple forward Euler integration.

    Returns the array of V(t) values over the simulated time window.
    """
    t = np.arange(0, duration_total, dt)
    I = amplitude * waveform_func(t, **waveform_kwargs)

    V = np.zeros_like(t)
    for i in range(1, len(t)):
        dV = (I[i - 1] - V[i - 1]) / tau_m * dt
        V[i] = V[i - 1] + dV
    return t, V


def find_threshold_amplitude(waveform_func, rheobase_mA: float, chronaxie_us: float,
                              duration_total: float, dt: float = 0.5,
                              **waveform_kwargs) -> float:
    """
    Finds the minimum current amplitude for a given waveform shape that
    just reaches threshold voltage, using bisection search.

    V_th is set equal to rheobase_mA, since for a rectangular pulse
    (R=1), steady-state V = I, and threshold is defined as the current
    that works for an infinitely long pulse (V_th = I_rh).
    """
    tau_m = tau_m_from_chronaxie(chronaxie_us)
    V_th = rheobase_mA

    lo, hi = 0.0, rheobase_mA * 50  # search range - generous upper bound
    for _ in range(60):  # bisection iterations, more than enough precision
        mid = (lo + hi) / 2
        _, V = simulate_membrane(waveform_func, duration_total, mid, tau_m, dt, **waveform_kwargs)
        if V.max() >= V_th:
            hi = mid
        else:
            lo = mid
    return hi
