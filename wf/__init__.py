"""Test L1 filtering
"""

import subprocess
from pathlib import Path

from latch import large_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchAuthor, LatchFile, LatchMetadata, LatchParameter


@large_task
def filter_L1_task(read2: LatchFile) -> LatchFile:

    # A reference to our output.
    file_L1 = Path("linker1_R2.fastq.gz").resolve()

    _bbduk_cmd = [
        "bbmap/bbduk.sh",
        f"in1={read2.local_path}",
        f"outm1={file_L1}",  
        "k=30",
        "mm=f",
        "rcomp=f",
        "restrictleft=103",
        "hdist=3",
        #"stats={qc_data}/{wildcards.sample}_stats.linker1.txt",
        "threads=46",
        "literal=GTGGCCGATGTTTCGCATCGGCGTACGACT"
        ]

    subprocess.run(_bbduk_cmd)

    return LatchFile(str(file_L1), "latch:///linker1_R2.fastq.gz")

@large_task
def filter_L2_task(read2: LatchFile) -> LatchFile:

    # A reference to our output.
    file_L2 = Path("linker2_R2.fastq.gz").resolve()

    _bbduk_cmd = [
        "bbmap/bbduk.sh",
        f"in1={read2.local_path}",
        f"outm1={file_L2}",
        "k=30",
        "mm=f",
        "rcomp=f",
        "restrictleft=65",
        "hdist=3",
        # "stats={qc_data}/{wildcards.sample}_stats.linker2.txt"
        "threads=46",
        "literal=ATCCACGTGCTTGAGAGGCCAGAGCATTCG"
        ]

    subprocess.run(_bbduk_cmd)

    return LatchFile(str(file_L2), "latch:///linker2_R2.fastq.gz")


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
        "read1": LatchParameter(
            display_name="Read 1",
            description="Paired-end read 1 file to be processed.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "read2": LatchParameter(
            display_name="Read 2",
            description="Paired-end read 2 file to be processed.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
    },
    tags=[],
)


@workflow(metadata)
def spatial_atac(read1: LatchFile, read2: LatchFile) -> (LatchFile, LatchFile):
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
    filter1 = filter_L1_task(read2=read2)
    return read1, filter_L2_task(read2=filter1)


"""
Add test data with a LaunchPlan. Provide default values in a dictionary with
the parameter names as the keys. These default values will be available under
the 'Test Data' dropdown at console.latch.bio.
"""
LaunchPlan(
    spatial_atac,
    "Test Data",
    {
        "read1": LatchFile("s3:///BASESPACE_IMPORTS/projects/PL000121/D01027_NG01679_L1/D01027_NG01679_S1_L001_R1_001.fastq.gz"),
        "read2": LatchFile("s3:///BASESPACE_IMPORTS/projects/PL000121/D01027_NG01679_L1/D01027_NG01679_S1_L001_R2_001.fastq.gz"),
    },
)
