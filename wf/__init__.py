import os
from pathlib import Path
import subprocess

from latch import large_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchAuthor, LatchDir, LatchFile, LatchMetadata, LatchParameter


@large_task(cache=True)
def filter_r2_task(r1: LatchFile, r2: LatchFile) -> (LatchFile, LatchFile):

    bbduk1_cmd = [
        "bbmap/bbduk.sh",
        f"in1={r1.local_path}",
        f"in2={r2.local_path}",
        "outm1=/root/D01033_NG01681_linker1_R1.fastq.gz",
        "outm2=/root/D01033_NG01681_linker1_R2.fastq.gz",
        "skipr1=t",
        "k=30",
        "mm=f",
        "rcomp=f",
        "restrictleft=103",
        "hdist=3",
        "stats=/root/D01033_NG01681_linker1_stats.txt",
        "threads=46",
        "literal=GTGGCCGATGTTTCGCATCGGCGTACGACT"
        ]

    subprocess.run(bbduk1_cmd)

    bbduk2_cmd = [
        "bbmap/bbduk.sh",
        "in1=/root/D01033_NG01681_linker1_R1.fastq.gz",
        "in2=/root/D01033_NG01681_linker1_R2.fastq.gz",
        "outm1=/root/D01033_NG01681_linker2_R1.fastq.gz",
        "outm2=/root/D01033_NG01681_linker2_R2.fastq.gz",
        "skipr1=t",
        "k=30",
        "mm=f",
        "rcomp=f",
        "restrictleft=65",
        "hdist=3",
        "stats=/root/D01033_NG01681_linker2_stats.txt",
        "threads=46",
        "literal=ATCCACGTGCTTGAGAGGCCAGAGCATTCG"
        ]

    subprocess.run(bbduk2_cmd)

    filtered_r1 = Path("D01033_NG01681_linker2_R1.fastq.gz").resolve()
    filtered_r2 = Path("D01033_NG01681_linker2_R2.fastq.gz").resolve()

    return (
            LatchFile(str(filtered_r1), f"latch:///preprocessing/D01033_NG01681_linker2_R1.fastq.gz"),
            LatchFile(str(filtered_r2), f"latch:///preprocessing/D01033_NG01681_linker2_R2.fastq.gz")
        )

@large_task(cache=True)
def process_bc_task(r2: LatchFile) -> (LatchFile, LatchFile):
    """ Process read2: save genomic portion as read3, extract
    barcode seqs and save as read3
    """

    bc_cmd = [
        "python",
        "bc_process.py",
        "--input",
        r2.local_path,
        "--output_R2",
        "/root/D01033_NG01681_S1_L001_R2_001.fastq",
        "--output_R3",
        "/root/D01033_NG01681_S1_L001_R3_001.fastq"
        ]

    subprocess.run(bc_cmd)

    file_r2 = Path("D01033_NG01681_S1_L001_R2_001.fastq").resolve()
    file_r3 = Path("D01033_NG01681_S1_L001_R3_001.fastq").resolve()

    return ( 
        LatchFile(str(file_r2), f"latch:///cell-ranger_inputs/D01033_NG01681_S1_L001_R2_001.fastq"),
        LatchFile(str(file_r3), f"latch:///cell-ranger_inputs/D01033_NG01681_S1_L001_R3_001.fastq")
    )

@large_task(cache=True)
def copy_r1_task(r1: LatchFile) -> (LatchFile):

        return LatchFile(r1.local_path, "latch:///cell-ranger_inputs/D01033_NG01681_S1_L001_R1_001.fastq.gz")

@large_task
def cellranger_task(
    input_dir: LatchDir = "latch:///cell-ranger_inputs",
    output_dir: LatchDir = "latch:///outs"
) -> (LatchDir):

    cr_command = [
    "cellranger-atac-2.1.0/cellranger-atac",
    "count",
    "--id=D01033_NG01681", # this will need to be dynamic
    "--reference=refdata-cellranger-arc-GRCh38-2020-A-2.0.0",
    f"--fastqs={input_dir.local_path}",
    "--localcores=96",
    "--localmem=192",
    "--force-cells=2500",
    ]

    subprocess.run(cr_command)

    cr_outputdir = Path('/root/D01033_NG01681/outs').resolve()

    return LatchDir(cr_outputdir, output_dir.remote_path)

"""The metadata included here will be injected into your interface."""
metadata = LatchMetadata(
    display_name="ATX-test-2",
    documentation="your-docs.dev",
    author=LatchAuthor(
        name="James McGann",
        email="jamesm@atlasxomics.com",
        github="github.com/jpmcga",
    ),
    repository="https://github.com/jpmcga/Spatial_ATAC-seq/",
    license="MIT",
    parameters={
        "r1": LatchParameter(
            display_name="Read 1",
            description="Paired-end read 1 file to be processed.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "r2": LatchParameter(
            display_name="Read 2",
            description="Paired-end read 2 file to be processed.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
    },
    tags=[],
)

@workflow(metadata)
def spatial_atac(r1: LatchFile, r2: LatchFile) -> (LatchFile, LatchFile, LatchFile):
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

    filtered_r1, filtered_r2 = filter_r2_task(r1=r1, r2=r2)
    new_r2, r3 = process_bc_task(r2=filtered_r2)
    new_r1 = copy_r1_task(r1=filtered_r1)
    # cellranger_task(input_dir="latch:///cell-ranger_inputs", output_dir="latch:///outs")
    return new_r1, new_r2, r3

"""
Add test data with a LaunchPlan. Provide default values in a dictionary with
the parameter names as the keys. These default values will be available under
the 'Test Data' dropdown at console.latch.bio.
"""
LaunchPlan(
    spatial_atac,
    "Test Data",
    {
        "r1": LatchFile("latch:///BASESPACE_IMPORTS/projects/PL000121/D01033_NG01681_L1/D01033_NG01681_S3_L001_R1_001.fastq.gz"),
        "r2": LatchFile("latch:///BASESPACE_IMPORTS/projects/PL000121/D01033_NG01681_L1/D01033_NG01681_S3_L001_R2_001.fastq.gz"),
    },
)
