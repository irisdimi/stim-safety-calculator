# Neural Stimulation Safety Calculator

Calculates safe electrical stimulation parameters for neural tissue, using two established models from BMET 2902 coursework: the Weiss/Lapicque strength-duration curve and the Shannon (1992) charge density safety model.

## What it does

Given an electrode's pulse duration, rheobase, chronaxie, and area, this tool:
- Calculates the minimum current/charge needed to trigger a neural response
- Calculates the resulting charge density
- Checks that charge density against the Shannon safety limit
- Plots both the strength-duration curve and the Shannon safety boundary, with your specific setup marked on each

## Setup

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

**Fixed example parameters** (edit values directly in the file):
```bash
cd src
python3 main.py
```

**Interactive** (type in your own values each run):
```bash
cd src
python3 interactive.py
```

Both generate two plots into `../figures/`.

## The Models

**Strength-duration (Weiss/Lapicque):**
```
I_th(d) = I_rh * (1 + chronaxie / d)
```
Minimum current needed to trigger a response, as a function of pulse duration.

**Shannon safety model (1992):**
```
log10(D) = k - log10(Q)
```
Where D = charge density (uC/cm²), Q = charge per phase (uC), and k is an empirical safety constant (k≈1.5 conservative, k≈1.85 historical Shannon limit).

⚠️ Double-check constants against your own lecture notes — different sources use slightly different conventions.

## Structure

```
stim-safety-calculator/
├── README.md
├── requirements.txt
├── figures/
└── src/
    ├── stim_model.py     # core equations
    ├── plots.py          # strength-duration + Shannon plots
    ├── main.py            # fixed example parameters
    └── interactive.py    # type in your own values
```
