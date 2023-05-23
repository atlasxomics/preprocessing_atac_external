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

# Needs to be updated periodically
RUN curl -o Rnor6.tar.gz "https://atx-st-references.s3.us-east-1.amazonaws.com/rnor6-atac.tar.gz?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEQVqXAIE9XMpnVso37%2BnIQaEVr%2F42b%2B9iDJ0rvbhiJBAiEAtZBR1nraaqPNkGuHAj6K4bqU9ZhhoKamEqQpzIj4gKAq1QMI4P%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw0NTQyMjE1ODA0NjQiDM8rrDhCqfByKeiLjSqpA%2FeOv2M24%2FE%2BvZMh0ZFKRkMrihb4dBKMekDb%2BkHPfRf%2FymfarBdAt9TEDcO15amAwilBVqQWe7cz25n5WfScZj0rEZWYiwewe45nfYhoNb1xsx9U5sLiEcM528N35fforWxA3Aw8b0klxiFxy8cRGVMYbgXGbmuHiyd06FPwa7j6%2FkaBClb1%2FYxH0VlRhe5zFYKFsOf%2B%2FiRjkbMgsaNboON56zx0T6ue5NOV5a19uWW974jqdzrZNJ03QOn6%2BCSWaWeSqEEDn3mjjhqNuScjK1SCulGrJNfsocxKRtUuvO8Lj8gLM37wZ2AkXpO7wuFWky%2BBqQI44EgExjYl1niPSDh6WvRAXvvJzXype2AEzZs48EG70Jb7Bc63shKWehf7Spya%2B8lmzz%2FUAi8UuWSzzkIstJCYpKi1HHPMMYmmkialUGdlgpMOZnKtAPTMY6Id1oaPBY0LnBXmJwr7bzlsUC%2BzApXePZPDxoie22ha14i4yWGKc9SWUrSQ2%2Bm57b9WVBZaMXTDKIMStqU46Z1xn1kQDEEE6j6%2FT6g2FAE%2FHS92Z9GWRamJ%2F66yMPiPtaMGOpQCc0ko1uBvAHizth8zksZ4Hqoc3T2LaZDHIkdk6ecsSzEp4TdGqPxElJ6vFr6nyqywNPNPZY1HAn%2FkE5wgsz0d4JM9qfJbONLz7XpRp4kbrBQf2PfP5DelnDCQcVGeeaR0eY19EKMRyNP5uADrM46nXRya2sWt7jhIo2qCTryHEKaey0lef42Q7%2Be0NtSoJeneFDcn7pwhdlGu9%2BAe%2BE8wrByfrJb9tnwcYjpJuaeWTwwMKCgRmDunMICbk5PcVHMbyUz8O3wPXF72pQFribrq%2FctqVjs%2F8LaFZCmeIQLAuGux%2BZlpFh1oSmdPjnFc0wO4PI%2BVPJu7slgq1AeEqL263v88EU92fWB1T8Oz7yCZimlGRp%2F%2B&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230523T231209Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAWTQNXJCYMEQHTUUC%2F20230523%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=2cf5672d48d04f574092ade74b7e321c38c6f17b6514ae5308f6358a8ee0cfbe" && \
    tar -xvzf Rnor6.tar.gz && \
    rm Rnor6.tar.gz

# Copy barcode files to root dir
COPY bc50.txt.gz /root/bc50.txt.gz
COPY bc96.txt.gz /root/bc96.txt.gz

# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
RUN echo 'hello'
RUN python3 -m pip install --upgrade latch
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root
