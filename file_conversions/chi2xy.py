# coding: utf-8
"""
Function to convert all .chi files in a given directory to .xy files.
Skips rows with metadata in .chi file specified in function argument.
Optional xy_dir argument to specify different output directory for .xy files.

Note: on Windows the chi_dir and xy_dir paths should be given as raw strings (r"your\path\here") to avoid issues with os separators (slashes).
"""

from pathlib import Path
import pandas as pd

def chi2xy(chi_dir, rows_to_skip, xy_dir=None, xy_float_format="%.8f", xy_delimiter="\t"):
    chi_dir = Path(chi_dir)
    xy_dir = Path(xy_dir) if xy_dir is not None else chi_dir

    # Ensure the output directory exists
    xy_dir.mkdir(parents=True, exist_ok=True)

    # Iterate over all .chi files using pathlib
    for chi_path in chi_dir.glob("*.chi"):
        xy_path = xy_dir / f"{chi_path.stem}.xy"

        # pandas accepts Path objects directly
        data = pd.read_csv(
            chi_path,
            skiprows=rows_to_skip,
            header=None,
            delimiter='\\s+'
        )

        data.to_csv(xy_path, index=False, float_format=xy_float_format, header=False, sep=xy_delimiter)
