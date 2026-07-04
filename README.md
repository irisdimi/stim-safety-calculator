# Neural Stimulation Safety Calculator

A Python tool for analysing whether neural stimulation parameters are likely to be both effective and safe.

The calculator uses two standard bioelectronics models:

- **Weiss/Lapicque strength-duration model** to estimate the current needed to excite neural tissue.
- **Shannon charge-density safety model** to check whether stimulation remains within a chosen safety limit.

## Features

- Calculates threshold current
- Calculates threshold charge
- Calculates charge density
- Computes Shannon `k` safety value
- Gives a safe / unsafe verdict
- Generates strength-duration and Shannon safety plots
- Compares monophasic and biphasic stimulation waveforms
- Includes a cochlear implant mapping example using the Greenwood function

## Example

Input:

```text
Pulse duration: 200 µs
Rheobase: 0.5 mA
Chronaxie: 150 µs
Electrode area: 0.01 cm²
Safety limit: k = 1.5
```

Output:

```text
Threshold current: 0.875 mA
Threshold charge: 175.0 nC
Charge density: 17.50 µC/cm²
Shannon k-value: 0.486
Verdict: Safe
```

## Installation

Clone the repository:

```bash
git clone https://github.com/irisdimi/stim-safety-calculator.git
cd stim-safety-calculator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main calculator:

```bash
python main.py
```

Or run the interactive version:

```bash
python interactive_calculator.py
```

## Limitations

This tool is intended for educational and first-pass design analysis only. It does not replace experimental validation, clinical testing, regulatory review, or device-specific safety limits.

## Author

Aya Banna
Biomedical Engineering (Honours)
University of Sydney
