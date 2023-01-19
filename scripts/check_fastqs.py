from gzip import open as gzopen
import os

from latch.types import LatchFile, LatchDir

def check_fastqs(input_dir: LatchDir):
    
    for file in os.listdir(input_dir.local_path):
        print(file)
        path = input_dir.local_path + "/" + file
        if file.endswith(".gz"):
            with gzopen(path, "rt") as handle:
                for i in range(50):
                    print(handle.readline())
                print()
                print()
        else:
            with open(path, "rt") as handle:
                for i in range(50):
                    print(handle.readline())
                print()
                print()

    return

if __name__ == '__main__':
    check_fastqs(input_dir="latch:///runs/D01033_NG01681/cellranger_inputs")

