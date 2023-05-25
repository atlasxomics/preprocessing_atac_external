import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pathlib import Path
from typing import List, Tuple, Union

def get_axis_avgs(
    singlecell_path: Path,
    positions_path: Path
) -> pd.DataFrame:
    """
    Given CellRanger singlecell.csv and positions.csv (on/off tissue), return
    pd.DataFrame with median row and column counts for each lane.
    """
    
    sc = pd.read_csv(singlecell_path)
    sc = sc[sc["barcode"] != "NO_BARCODE"]
    sc["barcode"] = sc["barcode"].apply(lambda x: x.strip("-1"))

    positions = pd.read_csv(positions_path, header=None)
    positions.columns = ["barcode", "on_tissue", "row", "column"]

    merged = pd.merge(sc, positions)

    avgs = [merged.groupby([axis]).median()["passed_filters"]
            for axis in ["row", "column"]]

    df = pd.merge(avgs[0], avgs[1], right_index=True, left_index=True)
    df.columns = ["row_avg", "col_avg"]
    df.index.name = None
    
    return df

def get_upper_bounds(
    avgs: Union[pd.Series, List[float]],
    sigma: int=1
) -> Tuple[float, float]:    
    """
    Given pd.DataFrame with median row and column counts for each lane,
    return values above with a lane average is considered an outlier for
    """
        
    mean = np.mean(avgs)
    std = np.std(avgs)

    row, col = mean + sigma * std
    
    return row, col

def get_outliers(
    avgs: Union[pd.Series, List[float]],
    row_bound: float,
    col_bound: float
) -> pd.DataFrame:
    """Add boolean column identifying outliers to lane averages;
    merger with average to return a dataframe."""
    
    row_outliers = avgs["row_avg"] > row_bound
    col_outliers = avgs["col_avg"] > col_bound
    
    avgs = avgs.merge(row_outliers, left_index=True, right_index=True)
    avgs = avgs.merge(col_outliers, left_index=True, right_index=True)
    
    avgs.columns = ["row_avg", "col_avg", "row_outlier", "col_outlier"]
    
    return avgs

def plotting_task(
    singlecell_path: Path,
    positions_path: Path
):
    """Save a barplot.pdf to pwd containing row/column medians with outlier
    highlighted at sigma 1 and 2"""

    dfs = []
    for sigma in [1,2]:
        avgs = get_axis_avgs(singlecell_path, positions_path)
        row_bound, col_bound = get_upper_bounds(avgs, sigma=sigma)
        df = get_outliers(avgs, row_bound, col_bound)
        dfs.append((sigma, df))

    plt.rc("figure", figsize=(15,10))

    fig, ax = plt.subplots(4,1, sharex=True)
    plt.subplots_adjust(wspace=0, hspace=0.2)

    i = 0
    for sigma, df in dfs:

        row_x = df.index
        row_y = df["row_avg"]
        row_colors = df["row_outlier"]

        ax[i].bar(    
            [x + 1 for x in row_x[~row_colors]],
            row_y[~row_colors],
            color="blue",
            edgecolor=(0,0,0),
        )

        ax[i].bar(    
            [x + 1 for x in row_x[row_colors]],
            row_y[row_colors],
            color="red",
            edgecolor=(0,0,0),
            label = "outliers"
        )

        ax[i].set_title(f"row medians (sigma={sigma})")
        ax[i].set_ylabel("median frag counts")
        ax[i].legend()
        
        i += 1

        col_x = df.index
        col_y = df["col_avg"]
        col_colors = df["col_outlier"]

        ax[i].bar(    
            [x + 1 for x in col_x[~col_colors]],
            col_y[~col_colors],
            color="blue",
            edgecolor=(0,0,0),
        )

        ax[i].bar(    
            [x + 1 for x in col_x[col_colors]],
            col_y[col_colors],
            color="red",
            edgecolor=(0,0,0),
            label = "outlier"
        )

        ax[i].set_title(f"column medians (sigma={sigma})")
        ax[i].set_ylabel("median frag counts")
        ax[i].legend()

        xticks = [x + 1 for x in range(len(df.index))]
        font_size = 5 if len(df.index) == 96 else 9
        ax[i].set_xticks(xticks)
        ax[i].set_xticklabels(xticks, fontsize=font_size)

        i += 1
        
    plt.savefig("lane_qc.pdf")

if __name__ == "__main__":
    from enum import Enum
    from latch.types import LatchFile

    class BarcodeFile(Enum):
        x50 = "bc50.txt.gz"
        x50_old = "bc50_old.txt.gz"
        x96 = "bc96.txt.gz"

    positions_paths = {
        "x50"     : "latch:///spatials/x50_all_tissue_positions_list.csv",
        "x50_old" : "latch:///spatials/x50-old_tissue_positions_list.csv",
        "x96"     : "latch:///spatials/x96_all_tissue_positions_list.csv"
        }
    
    barcode_file = BarcodeFile.x50_old
    local_out = "~/latch/spatial-atac/scripts/outs"

    positions_file = LatchFile(positions_paths[barcode_file.name])
    plotting_task(f"{local_out}/singlecell.csv", positions_file.local_path)
