'''Testing move of r2 from original location to cell-ranger_input'''

import os

from latch import small_task
from latch.types import LatchFile

@small_task
def copy_r1(r1: LatchFile) -> (LatchFile):

        return LatchFile(r1.local_path, "latch:///cell-ranger_inputs/S3_L001_R1_001.fastq.gz")

if __name__ == '__main__':
        copy_r1(
        r1=LatchFile("latch:///BASESPACE_IMPORTS/projects/PL000121/D01033_NG01681_L1/D01033_NG01681_S3_L001_R1_001.fastq.gz")
        )

