"""
Shared plotting style for all figures in this project, so every plot
has a consistent, clean, publication-style look. Import and call
apply_style() at the top of any plotting script.
"""

import matplotlib.pyplot as plt

# A consistent, colourblind-friendly palette used across all figures.
COLORS = {
    "primary": "#2A6F97",    # deep blue
    "secondary": "#E8871E",  # warm orange
    "accent": "#5DA271",     # green
    "danger": "#C1436D",     # magenta/red
    "neutral": "#8895A7",    # muted grey-blue
    "safe_fill": "#5DA271",
}


def apply_style():
    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 200,
        "font.size": 11,
        "font.family": "sans-serif",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "medium",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.7,
        "axes.axisbelow": True,
        "legend.frameon": True,
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#DDDDDD",
        "legend.fontsize": 9.5,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })
