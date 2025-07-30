DEFAULT_COLOR_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]


def assign_default_colors(labels):
    """Assigns a default color per label deterministically"""
    unique_labels = sorted(set(labels))
    return {
        label: DEFAULT_COLOR_PALETTE[i % len(DEFAULT_COLOR_PALETTE)]
        for i, label in enumerate(unique_labels)
    }
