import os
from pathlib import Path
import subprocess

from latch import large_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchAuthor, LatchDir, LatchFile, LatchMetadata, LatchParameter


@large_task(cache=True)
def filter_task(
    r1: LatchFile,
    r2: LatchFile,
    run: str
) -> (LatchFile, LatchFile):

    filtered_r1_l1 = Path(f"{run}_linker1_R1.fastq.gz").resolve()
    filtered_r2_l1 = Path(f"{run}_linker1_R2.fastq.gz").resolve()

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
        f"stats=/root/{run}_linker1_stats.txt",
        "threads=46",
        "literal=GTGGCCGATGTTTCGCATCGGCGTACGACT"
        ]

    subprocess.run(_bbduk1_cmd)

    filtered_r1_l2 = Path(f"{run}_linker2_R1.fastq.gz").resolve()
    filtered_r2_l2 = Path(f"{run}_linker2_R2.fastq.gz").resolve()

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
        f"stats=/root/{run}_linker2_stats.txt",
        "threads=46",
        "literal=ATCCACGTGCTTGAGAGGCCAGAGCATTCG"
        ]

    subprocess.run(_bbduk2_cmd)

    return (
            LatchFile(
                str(filtered_r1_l2),
                f"latch:///runs/{run}/preprocessing/{run}_linker2_R1.fastq.gz"
            ),
            LatchFile(
                str(filtered_r2_l2),
                f"latch:///runs/{run}/preprocessing/{run}_linker2_R2.fastq.gz"
            )
        )

@large_task(cache=True)
def process_bc_task(r2: LatchFile, run: str) -> (LatchFile, LatchFile):
    """ Process read2: save genomic portion as read3, extract
    barcode seqs and save as read3
    """

    new_r2 = Path(f"{run}_S1_L001_R2_001.fastq").resolve()
    r3 = Path(f"{run}_S1_L001_R3_001.fastq").resolve()

    _bc_cmd = [
        "python",
        "bc_process.py",
        "--input",
        r2.local_path,
        "--output_R2",
        f"{str(new_r2)}",
        "--output_R3",
        f"{str(r3)}"
        ]

    subprocess.run(_bc_cmd)

    return ( 
        LatchFile(
            str(new_r2),
            f"latch:///runs/{run}/cellranger_inputs/{run}_S1_L001_R2_001.fastq"
        ),
        LatchFile(
            str(r3),
            f"latch:///runs/{run}/cellranger_inputs/{run}_S1_L001_R3_001.fastq"
        )
    )

@large_task(cache=True)
def copy_r1_task(r1: LatchFile, run: str) -> (LatchFile):

    return LatchFile(
        r1.local_path,
        f"latch:///runs/{run}/cellranger_inputs/{run}_S1_L001_R1_001.fastq.gz"
        )

@large_task
def cellranger_task(
    input_dir: LatchDir,
    output_dir: LatchDir,
    run: str
) -> (LatchDir):

    local_out = Path(f'{run}/outs/').resolve()

    cr_command = [
    "cellranger-atac-2.1.0/cellranger-atac",
    "count",
    f"--id={run}", 
    "--reference=refdata-cellranger-arc-GRCh38-2020-A-2.0.0",
    f"--fastqs={input_dir.local_path}",
    "--localcores=96",
    "--localmem=192",
    "--force-cells=2500",
    ]

    subprocess.run(cr_command)

    return LatchDir(local_out, output_dir.remote_path)

"""The metadata included here will be injected into your interface."""
metadata = LatchMetadata(
    display_name="Spatial ATAC-seq",
    documentation="your-docs.dev",
    author=LatchAuthor(
        name="James McGann",
        email="jamesm@atlasxomics.com",
        github="github.com/jpmcga",
    ),
    repository="https://github.com/jpmcga/spatial-atacseq_latch/",
    license="MIT",
    parameters={
        "r1": LatchParameter(
            display_name="read 1",
            description="Read 1 must contain genomic sequence.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "r2": LatchParameter(
            display_name="read 2",
            description="Read 2 must contain barcode sequences \
                        and end with >35bp of genomic sequence.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "run": LatchParameter(
            display_name="run",
            description="Name of run, defailt to Dxxxxx_NGxxxxx format.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
    },
    tags=[],
)

@workflow(metadata)
def spatial_atac(
    r1: LatchFile,
    r2: LatchFile,
    run: str
) -> (LatchDir):
    """Description...

    Spatial ATAC-seq
    ----

    Process data from DBiT-seq experiments for spatially-resolved epigenomics:

    > See Deng, Y. et al 2022.

    # Steps

    * filter read2 on linker 1 identify via bbduk
    * filter read2 on linker 2 identify via bbduk
    * split read2 into genomic (read3) and barcode (read2)
    * run Cell Ranger ATAC
    """

    filtered_r1, filtered_r2 = filter_task(r1=r1, r2=r2, run=run)
    new_r2, r3 = process_bc_task(r2=filtered_r2, run=run)
    new_r1 = copy_r1_task(r1=filtered_r1, run=run)
    
    return cellranger_task(
        input_dir=f"latch:///runs/{run}/cellranger_inputs/",
        output_dir=f"latch:///runs/{run}/outs/"
        )
     

"""
Add test data with a LaunchPlan. Provide default values in a dictionary with
the parameter names as the keys. These default values will be available under
the 'Test Data' dropdown at console.latch.bio.
"""
LaunchPlan(
    spatial_atac,
    "Test Data",
    {
        "r1" : LatchFile("latch:///BASESPACE_IMPORTS/projects/PL000121/D01033_NG01681_L1/D01033_NG01681_S3_L001_R1_001.fastq.gz"),
        "r2" : LatchFile("latch:///BASESPACE_IMPORTS/projects/PL000121/D01033_NG01681_L1/D01033_NG01681_S3_L001_R2_001.fastq.gz"),
        "run" : "D01033_NG01681"
    },
)
