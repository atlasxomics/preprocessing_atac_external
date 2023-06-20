"""AtlasXomics Inc, preprocessing ATAC-seq external"""

import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from latch import large_task, medium_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import (
    LatchAuthor,
    LatchDir,
    LatchFile,
    LatchMetadata,
    LatchParameter,
    LatchRule
)

from wf.outliers import plotting_task

class Species(Enum):
    mouse = "refdata-cellranger-arc-mm10-2020-A-2.0.0"
    human = "refdata-cellranger-arc-GRCh38-2020-A-2.0.0"
    rat = "Rnor6"

class BarcodeFile(Enum):
    x50 = "bc50.txt.gz"
    x50_old = "bc50_old.txt.gz"
    x96 = "bc96.txt.gz"

@medium_task(retries=0)
def filter_task(
    r1: LatchFile,
    r2: LatchFile,
    run_id: str
) -> Tuple[LatchFile, LatchFile, LatchFile, LatchFile]:

    filtered_r1_l1 = Path(f"{run_id}_linker1_R1.fastq.gz").resolve()
    filtered_r2_l1 = Path(f"{run_id}_linker1_R2.fastq.gz").resolve()
    l1_stats = Path(f"{run_id}_l1_stats.txt").resolve()

    _bbduk1_cmd = [
        "bbmap/bbduk.sh",
        f"in1={r1.local_path}",
        f"in2={r2.local_path}",
        f"outm1={str(filtered_r1_l1)}",
        f"outm2={str(filtered_r2_l1)}",
        "skipr1=t",
        "k=30",
        "mm=f",
        "rcomp=f",
        "restrictleft=103",
        "hdist=3",
        f"stats={l1_stats}",
        "literal=GTGGCCGATGTTTCGCATCGGCGTACGACT"
        ]

    subprocess.run(_bbduk1_cmd)

    filtered_r1_l2 = Path(f"{run_id}_linker2_R1.fastq.gz").resolve()
    filtered_r2_l2 = Path(f"{run_id}_linker2_R2.fastq.gz").resolve()
    l2_stats = Path(f"{run_id}_l2_stats.txt").resolve()

    _bbduk2_cmd = [
        "bbmap/bbduk.sh",
        f"in1={str(filtered_r1_l1)}",
        f"in2={str(filtered_r2_l1)}",
        f"outm1={str(filtered_r1_l2)}",
        f"outm2={str(filtered_r2_l2)}",
        "skipr1=t",
        "k=30",
        "mm=f",
        "rcomp=f",
        "restrictleft=65",
        "hdist=3",
        f"stats={l2_stats}",
        "literal=ATCCACGTGCTTGAGAGGCCAGAGCATTCG"
    ]

    subprocess.run(_bbduk2_cmd)

    return (
            LatchFile(
                str(filtered_r1_l2),
                f"latch:///atac_outs/{run_id}/inputs/{run_id}_S1_L001_R1_001.fastq.gz"
        ),
            LatchFile(
                str(filtered_r2_l2),
                f"latch:///atac_outs/{run_id}/preprocessing/{run_id}_linker2_R2.fastq.gz"
        ),
            LatchFile(
                str(l1_stats),
                f"latch:///atac_outs/{run_id}/preprocessing/{l1_stats.name}"
        ),
            LatchFile(
                str(l2_stats),
                f"latch:///atac_outs/{run_id}/preprocessing/{l2_stats.name}"
        )
    )

@medium_task(retries=0)
def process_bc_task(
    r2: LatchFile,
    run_id: str,
) -> LatchDir:
    """ Process read2: save genomic portion as read3, extract 16 bp
    barcode seqs and save as read3
    """

    outdir = Path("inputs/").resolve()
    os.mkdir(outdir)
    new_r2 = Path(f"{outdir}/{run_id}_S1_L001_R2_001.fastq").resolve()
    r3 = Path(f"{outdir}/{run_id}_S1_L001_R3_001.fastq").resolve()

    _bc_cmd = [
        "python",
        "bc_process.py",
        "-i",
        r2.local_path,
        "-o2",
        f"{str(new_r2)}",
        "-o3",
        f"{str(r3)}"
    ]

    subprocess.run(_bc_cmd)

    return LatchDir(
        str(outdir),
        f"latch:///atac_outs/{run_id}/inputs/"
    )

@large_task(retries=0)
def cellranger_task(
    input_dir: LatchDir,
    run_id: str,
    species: Species,
    barcode_file: BarcodeFile
) -> LatchDir:
    """Run Cell Ranger ATAC on inputs dir; append run_id to all outfiles."""

    local_out = Path(f"{run_id}/outs/").resolve()
    barcode_path = Path(f"{barcode_file.value}").resolve()

    # overwrite default barcode file with DBiT barcode file
    _barcode_cmd = [
        "cp",
        f"{barcode_path}",
        "/root/cellranger-atac-2.1.0/lib/python/atac/barcodes/737K-cratac-v1.txt.gz"
    ]
    subprocess.run(_barcode_cmd)

    _cr_command = [
    "cellranger-atac-2.1.0/cellranger-atac",
    "count",
    f"--id={run_id}", 
    f"--reference={species.value}",
    f"--fastqs={input_dir.local_path}",
    "--localcores=96",
    "--localmem=192",
    "--force-cells=2500",
    ]

    subprocess.run(_cr_command)

    # Ensure pipeline ran correctly
    try:
        os.listdir(local_out)
    except FileNotFoundError:
        print("No output files detected; check logs for failure")

    # Make plot with lane averages, highlighting outliers, move to out dir
    positions_paths = {
        "x50"     : "latch:///spatials/x50_all_tissue_positions_list.csv",
        "x50_old" : "latch:///spatials/x50-old_tissue_positions_list.csv",
        "x96"     : "latch:///spatials/x96_all_tissue_positions_list.csv"
        }
    positions_file = LatchFile(positions_paths[barcode_file.name])
    plotting_task(f"{local_out}/singlecell.csv", positions_file.local_path)
    subprocess.run(["mv", "/root/lane_qc.pdf", str(local_out)])

    # Append run_id to outs and check for out_dir
    for f in os.listdir(local_out):
        os.rename(f'{local_out}/{f}', f'{local_out}/{run_id}_{f}')

    return LatchDir(str(local_out), f"latch:///atac_outs/{run_id}/outs/")

metadata = LatchMetadata(
    display_name="preprocessing ATAC-seq",
    author=LatchAuthor(
        name="AtlasXomics, Inc.",
        email="jamesm@atlasxomics.com",
        github="github.com/atlasxomics",
    ),
    repository="https://github.com/atlasxomics/preprocessing_atac_external",
    parameters={
        "r1": LatchParameter(
            display_name="read 1",
            description="Read 1 must contain genomic sequence.",
            batch_table_column=True,
        ),
        "r2": LatchParameter(
            display_name="read 2",
            description="Read 2 must contain barcode sequences \
                        and end with >35bp of genomic sequence.",
            batch_table_column=True,
        ),
        "run_id": LatchParameter(
            display_name="run id",
            description="Identifier/name of run",
            batch_table_column=True,
            rules=[
                LatchRule(
                    regex="^[^/].*",
                    message="run id cannot start with a '/'"
                )
            ]
        ),
        "species": LatchParameter(
            display_name="species",
            placeholder="select species for reference genome",
            description="Select reference genome for alignment.",
            batch_table_column=True,
        ),
        "barcode_file": LatchParameter(
            display_name="barcode file",
            description="Expected sequences of barcodes used is assay; \
                        bc50.txt.gz for SOP 50x50, bc96.txt.gz for 96x96, \
                        bc50_old.txt.gz for version from Deng, 2022 of 50x50.",
            batch_table_column=True,
        ),
    },
)

@workflow(metadata)
def spatial_atac(
    r1: LatchFile,
    r2: LatchFile,
    run_id: str,
    species: Species,
    barcode_file: BarcodeFile = BarcodeFile.x50,
) -> LatchDir:
    """Pipeline for processing spatial ATAC-seq data generated via DBiT-seq.

    preprocessing ATAC-seq external
    ----

    This workflow will convert fastq files from a spatial ATAC-seq experiemnt 
    (as per [Deng, 2022](https://www.nature.com/articles/s41586-022-05094-1))
    into ATAC-seq fragments and assay performance metrics.

    # Workflow overview

    * filter read2 on linker 1 identify via bbduk
    * filter read2 on linker 2 identify via bbduk
    * split read2 into genomic (read3) and barcode (read2)
    * run Cell Ranger ATAC
    """

    filtered_r1, filtered_r2, _, _ = filter_task(
        r1=r1,
        r2=r2,
        run_id=run_id
    )
    input_dir = process_bc_task(
        r2=filtered_r2,
        run_id=run_id
    )
    return cellranger_task(
        input_dir=input_dir,
        run_id=run_id,
        species=species,
        barcode_file=barcode_file
    )

LaunchPlan(
    spatial_atac,
    "demo",
    {
        "r1" : LatchFile("latch:///fastq_files/demo/demo_S3_L001_R1_001.fastq.gz"),
        "r2" : LatchFile("latch:///fastq_files/demo/demo_S3_L001_R2_001.fastq.gz"),
        "run_id" : "demo",
        "species" : Species.human,
        "barcode_file" : BarcodeFile.x50
    },
)
