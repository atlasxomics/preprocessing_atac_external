from pathlib import Path
import os

from latch import small_task
from latch.types import LatchDir, LatchFile

@small_task
def update_dir(
    output_dir: LatchDir,
) -> LatchDir:
    os.mkdir('/root/output') # An empty dir
    os.system('touch /root/output/test.txt') # A file in the dir
    return LatchDir('/root/output', output_dir.remote_path)

if __name__ == '__main__':
    update_dir(output_dir="latch:///cell-ranger_inputs/")