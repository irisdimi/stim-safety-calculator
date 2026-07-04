"""
Defines stimulation current waveforms as functions of time.

Real neurostimulation devices rarely use simple rectangular pulses.
The main reason: a rectangular monophasic pulse delivers net DC charge
into tissue, which over many repetitions causes electrode corrosion
and tissue damage through electrochemical reactions. Real devices use
CHARGE-BALANCED waveforms instead - the net charge delivered over a
full cycle is zero, even though a "useful" (cathodic) phase still
depolarizes the neuron.

Each function below returns the current (in normalized units, -1 to
+1) at a given time t, given the pulse's shape parameters. Multiply
by an amplitude to scale.
"""

import numpy as np


def rectangular(t: np.ndarray, duration: float) -> np.ndarray:
    """
    Simple rectangular monophasic pulse: constant current for the
    full duration, then off. Not charge-balanced - included as the
    baseline case matching the classic Weiss/Lapicque formula.
    """
    return np.where((t >= 0) & (t < duration), 1.0, 0.0)


def biphasic_symmetric(t: np.ndarray, phase_duration: float) -> np.ndarray:
    """
    Charge-balanced symmetric biphasic pulse: a cathodic (depolarizing,
    +1) phase, immediately followed by an equal-amplitude, equal-duration
    anodic (+1 -> -1) recovery phase. Net charge over the full pulse is
    zero. This is the most common charge-balancing scheme in practice.
    """
    cathodic = (t >= 0) & (t < phase_duration)
    anodic = (t >= phase_duration) & (t < 2 * phase_duration)
    return np.where(cathodic, 1.0, np.where(anodic, -1.0, 0.0))


def biphasic_asymmetric(t: np.ndarray, cathodic_duration: float, anodic_ratio: float = 4.0) -> np.ndarray:
    """
    Charge-balanced ASYMMETRIC biphasic pulse: a brief, high-amplitude
    cathodic phase (the "useful" excitation phase) followed by a longer,
    lower-amplitude anodic recovery phase. This is common in real devices
    (e.g. many cochlear implant stimulation strategies) because it keeps
    the efficient short cathodic phase for excitation while still
    achieving charge balance, without needing an equally brief (and
    therefore disruptive) anodic phase.

    anodic_ratio controls how much longer the anodic phase is relative
    to the cathodic phase (and therefore how much lower its amplitude
    must be to balance charge). anodic_ratio=4 means the anodic phase
    is 4x longer and 1/4 the amplitude.
    """
    anodic_duration = cathodic_duration * anodic_ratio
    anodic_amplitude = 1.0 / anodic_ratio

    cathodic = (t >= 0) & (t < cathodic_duration)
    anodic = (t >= cathodic_duration) & (t < cathodic_duration + anodic_duration)
    return np.where(cathodic, 1.0, np.where(anodic, -anodic_amplitude, 0.0))


def biphasic_anodic_first(t: np.ndarray, phase_duration: float) -> np.ndarray:
    """
    Charge-balanced symmetric biphasic pulse, but with phase ORDER
    reversed: the hyperpolarizing (anodic) phase comes first, followed
    by the depolarizing (cathodic) phase. Still charge-balanced overall,
    but this ordering is known to REQUIRE MORE CURRENT to trigger a
    response, because the initial anodic phase drives the membrane
    away from threshold before the cathodic phase even begins - the
    cathodic phase must first "undo" that hyperpolarization before it
    can start driving the membrane toward threshold. This is sometimes
    called anodal pre-hyperpolarization or anodal block, and it is the
    reason most real devices deliberately lead with the cathodic phase.
    """
    anodic = (t >= 0) & (t < phase_duration)
    cathodic = (t >= phase_duration) & (t < 2 * phase_duration)
    return np.where(anodic, -1.0, np.where(cathodic, 1.0, 0.0))


WAVEFORMS = {
    "rectangular": rectangular,
    "biphasic_symmetric": biphasic_symmetric,
    "biphasic_asymmetric": biphasic_asymmetric,
    "biphasic_anodic_first": biphasic_anodic_first,
}
