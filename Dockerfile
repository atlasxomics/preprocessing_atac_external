FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:dd8f-main

RUN apt-get update -y && \
    apt-get install -y curl unzip

RUN apt-get install -y default-jdk
RUN curl -L https://sourceforge.net/projects/bbmap/files/BBMap_39.01.tar.gz/download -o \
    BBMap_39.01.tar.gz && \
    tar -xvzf BBMap_39.01.tar.gz && \
    rm BBMap_39.01.tar.gz
RUN python3 -m pip install biopython slims-python-api

# cellranger download link has weird options, wonder if it'll work?
RUN curl -o cellranger-atac-2.1.0.tar.gz "https://cf.10xgenomics.com/releases/cell-atac/cellranger-atac-2.1.0.tar.gz?Expires=1677219504&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZi4xMHhnZW5vbWljcy5jb20vcmVsZWFzZXMvY2VsbC1hdGFjL2NlbGxyYW5nZXItYXRhYy0yLjEuMC50YXIuZ3oiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2NzcyMTk1MDR9fX1dfQ__&Signature=VcNdi5cTx0CT9W-lBGa7RoU8PQCPCnRc27xOfVgl3dBTb23tUoQhQEhfMRgAfz4WLfWr0~0zSlIvytLpCkbGUVme9NJ4qU1KiOo4mQEek2JPKt2ZKArqJP2OGrviL2AP3RqLUS-T2wAFZV7gyZzsgNnHMLANO30xbayQxITU~EIdkCgy9epclro1vVHONFmj6Ap1Bis98LAaDLoi3e0vcfi~Ra70nU02JMf867G9iTKExswLiE7VYOXQgFbOCZ4lX9eJcUTdQFdzAgMR~EcweUnTcs-olYhODWgY0ZVdFtSpldI6grCOlRVhjZSnBp9q0qNPO8xrYjfqhaZbDC9fzw__&Key-Pair-Id=APKAI7S6A5RYOXBWRPDA" -o \
    cellranger-atac-2.1.0.tar.gz && \
    tar -xzvf cellranger-atac-2.1.0.tar.gz && \
    rm cellranger-atac-2.1.0.tar.gz
RUN curl -O https://cf.10xgenomics.com/supp/cell-atac/refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz && \
    tar -xzvf refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz && \
    rm refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz
RUN curl -O https://cf.10xgenomics.com/supp/cell-atac/refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz && \
    tar -xzvf refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz && \
    rm refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz

COPY bc_process.py /root/bc_process.py

# Change cellranger to return median not max
COPY tss.py /root/cellranger-atac-2.1.0/lib/python/atac/metrics/__init__.py

# Root barcodefile for barcode script, replace default barcode file
COPY 737K-cratac-v1.txt.gz /root/737K-cratac-v1.txt.gz
COPY 737K-cratac-v1.txt.gz /root/cellranger-atac-2.1.0/lib/python/atac/barcodes/737K-cratac-v1.txt.gz

# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
RUN python3 -m pip install --upgrade latch
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root
