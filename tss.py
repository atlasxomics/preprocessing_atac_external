# Copyright (c) 2019 10x Genomics, Inc. All rights reserved.
"""
Tools for ATAC metric calculations
from cellranger-atac-2.1.0/lib/python/atac/metrics/__init__.py
"""

from __future__ import division, print_function, absolute_import

import numpy as np
import pandas as pd
from six import ensure_str

# Constants for computing CTCF footprinting score
UPSTR_CTCF_PEAK_POS = "-23"
DOWNSTR_CTCF_PEAK_POS = "34"
CTCF_VALLEY_POS = "-3"


def calculate_tss_score_and_profile(relative_positions):
    """Calculates a TSS enrichment score and returns the summed signal over
    -1kB to +1kB from an input CSV file.
    """
    xvals = np.arange(-1000, 1000 + 1)
    tss_df = pd.read_csv(ensure_str(relative_positions), float_precision="high")
    yvals = tss_df[[str(x) for x in xvals]].sum(axis=0)
    if any(yvals > 0):
        min_nonzero = yvals[yvals > 0].min()
        yvals /= min_nonzero
        score = yvals.median()
        return score, np.array(yvals), xvals
    return 0.0, np.array(yvals), xvals


def calculate_ctcf_score_and_profile(relative_positions):
    """Calculates a CTCF enrichment score and returns the summed signal over
    -250bp to +250bp from an input CSV file.
    """
    ctcf_df = pd.read_csv(ensure_str(relative_positions))
    xvals = np.arange(-250, 250 + 1)
    yvals = ctcf_df[[str(x) for x in xvals]].sum(axis=0)

    if max(yvals) > 0:
        yvals /= max(yvals)
        score = yvals[UPSTR_CTCF_PEAK_POS] + yvals[DOWNSTR_CTCF_PEAK_POS] - yvals[CTCF_VALLEY_POS]
        return score, np.array(yvals), xvals
    return 0.0, np.array(yvals), xvals