'''Testing move of r2 from original location to cell-ranger_input'''

import os
from pathlib import Path

from latch import small_task
from latch.types import LatchDir, LatchFile

@small_task
def copy_r1(output_dir: LatchDir) -> (LatchDir):

        r1 = LatchFile("latch:///BASESPACE_IMPORTS/projects/PL000121/D01033_NG01681_L1/D01033_NG01681_S3_L001_R1_001.fastq.gz")
        
        os.mkdir("/root/output")
        os.system(f"mv {r1.local_path} /root/output")
        os.system("touch /root/output/foo.txt")

        return LatchDir("/root/output", output_dir.remote_path)

if __name__ == '__main__':
        copy_r1(output_dir="latch:///cell-ranger_inputs/")

