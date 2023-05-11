import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from latch import large_task, medium_task, small_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import (
    LatchAuthor,
    LatchDir,
    LatchFile,
    LatchMetadata,
    LatchParameter,
    LatchRule
)

from latch.registry.table import Table

import wf.lims as lims

class Species(Enum):
    mouse = "refdata-cellranger-arc-mm10-2020-A-2.0.0"
    human = "refdata-cellranger-arc-GRCh38-2020-A-2.0.0"
    rat = "Rnor6"

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
                f"latch:///cr_outs/{run_id}/cellranger_inputs/{run_id}_S1_L001_R1_001.fastq.gz"
        ),
            LatchFile(
                str(filtered_r2_l2),
                f"latch:///cr_outs/{run_id}/preprocessing/{run_id}_linker2_R2.fastq.gz"
        ),
            LatchFile(
                str(l1_stats),
                f"latch:///cr_outs/{run_id}/preprocessing/{l1_stats.name}"
        ),
            LatchFile(
                str(l2_stats),
                f"latch:///cr_outs/{run_id}/preprocessing/{l2_stats.name}"
        )
    )


@medium_task(retries=0)
def process_bc_task(
    r2: LatchFile,
    run_id: str,
    bulk: bool
) -> LatchDir:
    """ Process read2: save genomic portion as read3, extract 16 bp
    barcode seqs and save as read3
    """

    outdir = Path("cellranger_inputs/").resolve()
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

    if bulk:
        _bc_cmd.append('-b')

    subprocess.run(_bc_cmd)

    return LatchDir(
        str(outdir),
        f"latch:///cr_outs/{run_id}/cellranger_inputs/"
    )


@large_task(retries=0)
def cellranger_task(
    input_dir: LatchDir,
    run_id: str,
    species: Species
) -> (LatchDir):
    """Run Cell Ranger ATAC on cellranger_inputs dir; append run_id to all
    outfiles.
    """

    local_out = Path(f'{run_id}/outs/').resolve()

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

    try: # Append run_id to outs and check for out_dir
        for f in os.listdir(local_out):
            os.rename(f'{local_out}/{f}', f'{local_out}/{run_id}_{f}')
    except FileNotFoundError:
        print("No output files detected; check Cell Ranger logs for failure")

    return LatchDir(
        str(local_out),
        f"latch:///cr_outs/{run_id}/outs/"
    )

@small_task(retries=0)
def lims_task(
    results_dir: LatchDir,
    run_id: str,
    upload: bool,
    ng_id: Optional[str]
) -> LatchDir:

    if upload:
    
        data = Path(results_dir.local_path + f'/{run_id}_summary.csv').resolve()
        
        slims = lims.slims_init()
        results = lims.csv_to_dict(data)
    
        payload = {lims.mapping[key]:value for (key, value) in results.items()
                    if key in lims.mapping.keys() and value not in lims.NA}
    
        if ng_id:
            pk = lims.get_pk(ng_id, slims)
        else:
            try:
                pk = lims.get_pk(run_id.split('_')[-1], slims)
            except IndexError:
                print('Invalid SLIMS ng_id.')
    
        payload['rslt_fk_content'] = pk
        payload['rslt_fk_test'] = 39
        payload['rslt_cf_value'] = 'upload'

        print(lims.push_result(payload, slims))
    
        return results_dir

    return results_dir

@small_task(retries=0)
def upload_latch_registry(
    results_dir: LatchDir,
    run_id: str,
    table_id: str = '390'
):
    table = Table(table_id)

    summary_file = f"{results_dir.remote_path}{run_id}_summary.csv"
    single_cell_file = f"{results_dir.remote_path}{run_id}_singlecell.csv"
    spatial_fragment_file = f"{results_dir.remote_path}{run_id}_fragments.tsv.gz"

    with table.update() as updater:
        updater.upsert_record(
            run_id,
            spatial_fragment_file=LatchFile(spatial_fragment_file)
        )

        updater.upsert_record(
            run_id,
            summary_csv=LatchFile(summary_file)
        )

        updater.upsert_record(
            run_id,
            single_cell_file=LatchFile(single_cell_file)
        )

metadata = LatchMetadata(
    display_name="Spatial ATAC-seq",
    author=LatchAuthor(
        name="James McGann",
        email="jpaulmcgann@gmail.com",
        github="github.com/jpmcga",
    ),
    repository="https://github.com/jpmcga/spatial-atacseq_latch/",
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
            description="ATX Run ID with optional prefix, default to \
                        Dxxxxx_NGxxxxx format.",
            batch_table_column=True,
            placeholder="Dxxxxx_NGxxxxx",
            rules=[
                LatchRule(
                    regex="^[^/].*",
                    message="run id cannot start with a '/'"
                ),
                LatchRule(
                    regex="_NG[0-9]{5}$",
                    message="Provide ng_id in ng_id field if upload to \
                    SLIMS desired."
                )
            ]
        ),
        "species": LatchParameter(
            display_name="species",
            description="Select reference genome for cellranger atac.",
            batch_table_column=True,
        ),
        "bulk": LatchParameter(
            display_name="bulk",
            description="If True, barcodes will be randomly assigned to reads.",
            batch_table_column=True,
        ),
       "upload_to_slims": LatchParameter(
            display_name="upload to slims",
            description="Select for CellRanger outs (summary.csv) to be \
            upload to SLIMS; if selected provide ng_id",
            batch_table_column=True,
        ),
        "ng_id": LatchParameter(
            display_name="ng_id",
            description="Provide SLIMS ng_id (ie. NG00001) if pushing to \
                        SLIMS and run_id does not end in '_NG00001'.",
            placeholder="NGxxxxx",
            batch_table_column=True,
            rules=[
                LatchRule(
                    regex="^NG[0-9]{5}$",
                    message="ng_id must match NGxxxxx format."
                ),
            ]
        ),
        "table_id": LatchParameter(
            display_name="Registry Table ID",
            description="Provide the ID of the Registry table. Files that will be populated in the table are: singlecell.csv, fragments.tsv.gz, and summary.csv"
        )
    },
)


@workflow(metadata)
def spatial_atac(
    r1: LatchFile,
    r2: LatchFile,
    run_id: str,
    species: Species,
    bulk: bool,
    upload_to_slims: bool,
    ng_id: Optional[str],
    table_id: str = "390"
) -> LatchDir:
    """Pipeline for processing Spatial ATAC-seq data generated via DBiT-seq.

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

    filtered_r1, filtered_r2, _, _ = filter_task(
        r1=r1,
        r2=r2,
        run_id=run_id
    )
    input_dir = process_bc_task(
        r2=filtered_r2,
        run_id=run_id,
        bulk=bulk
    )
    cr_outs = cellranger_task(
        input_dir=input_dir,
        run_id=run_id,
        species=species
    )

    upload_latch_registry(
        results_dir=cr_outs,
        run_id=run_id,
        table_id=table_id
    )

    return lims_task(
        results_dir=cr_outs,
        run_id=run_id,
        upload=upload_to_slims,
        ng_id=ng_id
    )


LaunchPlan(
    spatial_atac,
    "test data",
    {
        "r1" : LatchFile("latch:///downsampled/D01033_NG01681/ds_D01033_NG01681_S3_L001_R1_001.fastq.gz"),
        "r2" : LatchFile("latch:///downsampled/D01033_NG01681/ds_D01033_NG01681_S3_L001_R2_001.fastq.gz"),
        "run_id" : "ds_D01033_NG01681",
        "species" : Species.human,
        "bulk" : False,
        "upload_to_slims" : False,
        "ng_id" : None
    },
)


if __name__ == '__main__':
    lims_task(
        results_dir=LatchDir("latch:///cr_outs/B00352_NG01939/outs"),
        run_id="B00352_NG01939",
        ng_id='NG01939'
    )
