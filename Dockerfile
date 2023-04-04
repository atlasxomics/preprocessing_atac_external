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

RUN curl -o Rnor6.tar.gz "https://atx-novogene.s3.us-east-1.amazonaws.com/references/Rnor6.tar.gz?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEAcaCXVzLWVhc3QtMSJHMEUCIDnXOG7sazT8MX7%2FLRYYpIPB6ObsJiZwBVhlsGku%2FEIlAiEA5qDnibowvMTwixhNHSF7jezQBGLBARe%2FDBbbueNg5D8q7QII4P%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgwzMDcwNzU4NjY5MjciDCkrfnmbAw4QGoHXPyrBAokZDToAW3YpLT5UbQOEHSTXR6HCrqZWGbLw%2FnRb6ovKauhbeIR08w4zWBKD7CLyxKG197lIxb0D0ZdwiIvFEm8pmfFElV%2BXkHyNSJrIwd9eVj9LjmJRmcjWtuAmXmG0mSwz408g78G0hcHVxvCdwrT2Cnb5b5ZUx%2B4NnSbQQqz8JVNMoNRFQL71fhJ2h2pYlhaXesQAHSJI4%2BVzMQI1f09DVBJIpaAGmLw23L1YGRy8SWLvS6VnbSOs0x4XuYnPRYR97K3KrPAZPOV3TJU4fUu3rph3eGHwd1gn%2FloQUhLtU9%2BFn25w5gAQ3LeepYhqW9ujqDLmWupuRtDaW3coeu7hD1D3y69Q9XrcHZD8Kz7SA%2BvB9yH27fkg8Dm6x8Ea%2BXBBlGwroJb%2FwjsgkgMpn1RWU228RqHhS4ysXqqOiPnoTjCdtq2hBjqzAl5Vh9Ky2iLiVf4AthdE%2FysJ0FEPnBTDiyYbwvDZTU7O4yfVU8ET9GQbSOdUr%2Bs8czHGXAXEVGue71tsAtmQ7i02RVI2QY%2FgcEGfK%2BQu%2FERxtJiia9P4g2wMzRPieXycQ2WAeYgm9awLBJa7Wc5pCp0YmimuBnzgO3pFVS7zVkuzQkYm6gak3D72CjDglBsM9x8o32OJsvVEmMdRKpmUBsNSnLkQEOWQnXE1Lz9r8ljdLcvHULfskFQ3wD%2F%2FwYAiFkCMZTSP63TUt4GKFd3rox4q%2FWjTUhAKhv4NTzShnI0OjJ8dxhKvVbKotMdMYHh0ZNibdC9VnG7sgXrreCi9BmNsD7Bj1W6BRVGwLGnEisWefQAzExaeWxtJLQuCQdyjRZUqG9mcAFpKiDdRk9eVZOzpYd0%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230403T235920Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAUO7ZF4EXSGZ3G2FL%2F20230403%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=43f7b1bca79e839e36a7aac16eb81c701ea6e5d819bc35626f505ac6fd66582d" && \
    tar -xvzf Rnor6.tar.gz && \
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
