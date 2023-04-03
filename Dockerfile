FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:dd8f-main

RUN apt-get update -y && \
    apt-get install -y curl unzip

RUN apt-get install -y default-jdk
RUN curl -L https://sourceforge.net/projects/bbmap/files/BBMap_39.01.tar.gz/download -o \
    BBMap_39.01.tar.gz && \
    tar -xvzf BBMap_39.01.tar.gz && \
    rm BBMap_39.01.tar.gz
RUN python3 -m pip install biopython slims-python-api

# cellranger download link, needs to be updated periodically
RUN curl -o cellranger-atac-2.1.0.tar.gz "https://cf.10xgenomics.com/releases/cell-atac/cellranger-atac-2.1.0.tar.gz?Expires=1680577702&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZi4xMHhnZW5vbWljcy5jb20vcmVsZWFzZXMvY2VsbC1hdGFjL2NlbGxyYW5nZXItYXRhYy0yLjEuMC50YXIuZ3oiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2ODA1Nzc3MDJ9fX1dfQ__&Signature=UPhtVUmXBJYiFobugrrqGEULfXd2T3znhEVBZqLfJVv0deBiQLPvq0fOeXl5yK~7KWvvFb0BaFJzgBA~MlrrF60JsdW1lumykLBaApIRbvRy68D09gTXQlrrXurmnaS~TvDsNTguRYNxGWDi2MMUTDW2yI-vBFALHmLLXQhuu3x7FibP6RL17cblg-9fyUKdudyUBcM~zIb2SkaXupDyL1UtxCWFNGagBAS-vwihrVgEAlKwC~SdcnsBoFCvuszB~ttvM6nMFAnDCr6y9Gywa5p3n7jj-gvz6bT041I68U-mOCCLL8~7qssi1gP42kn3aN2Cl73nTArLoZp-4hDa8w__&Key-Pair-Id=APKAI7S6A5RYOXBWRPDA" && \ 
    tar -xzvf cellranger-atac-2.1.0.tar.gz && \
    rm cellranger-atac-2.1.0.tar.gz
RUN curl -O https://cf.10xgenomics.com/supp/cell-atac/refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz && \
    tar -xzvf refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz && \
    rm refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz
RUN curl -O https://cf.10xgenomics.com/supp/cell-atac/refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz && \
    tar -xzvf refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz && \
    rm refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz

# Copy helper script, rat reference genome
COPY bc_process.py /root/bc_process.py

COPY Rnor6.tar.gz /root/Rnor6.tar.gz
RUN tar -xvzf Rnor6.tar.gz && \
    rm Rnor6.tar.gz

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
