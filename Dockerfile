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
RUN curl -o Rnor6.tar.gz "https://atx-novogene.s3.us-east-1.amazonaws.com/references/Rnor6.tar.gz?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIFA0McaisbwoWAmch1Cvh848gWBz4LNboRMSD%2Fc4XjxfAiBV5jwMZLgmj16UPB5fWuQCN1myo2AXDqzSEvwUJZGSqCrtAgia%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDMwNzA3NTg2NjkyNyIM6PIMCLXDab9xpYgtKsECbdZ%2BVoMLm1HVY6o%2BoG57QWWiwGxi0m3EjkAKPES%2B0Wt5eSve5qern%2BnEqgrdu2gTnzi%2BUs11135hAT1mp6tWf%2BmSID4SnQDVTXa1xQPZEQwWyXtc%2BEWCmaA93TK468TutQP%2F7wiua35W9JW3VpFlV%2BEOua5UeruSqahr7ambhbdl4HMEnht%2FcnmsLSqaalkocbJJt9qm%2FK30frc0fNpxl03IoaJS%2FVJiXk01v0zW5cd%2F7s7nEWOB37rJWCT3s8ahGGn%2F8xKEDmhUNWmk5IMlRKBlus8QTSkIUhwmrAhgER79pJOF6O1ft8egVTV2v15WkhpXxzFgHKXGPYa0Sswi9%2FMuE8necLmmPh3Z6vyuP323tFIYmfk6HNJSN%2FaoHeG0CAEx0Gz1pypJv6LQtUWEYtdcjpjTLaLppliG6UX%2FKVPxMP788KIGOrQCbbeS63HOZtp0l%2FN4qJm2zdq2Kprl8pelaoADXAPW7uk5DgA61auocHT7gqUupgsbPg8FhIG%2Fn3WX6aMtgrWRfyiqsZR2CtIfPQIKvfFq466qhufs2J6w%2FRiM7iHsUsxJbcuXmgF2Zyi0OsmeaeiEtg751BSnUHL2isgH9bDSX6HSKRRbO9Hko4h4GyVv9v4QgX8Ui6dY6NL2hpygPd5dna2dM%2FY8XLfZwtILW%2Fx2k1%2BohLOaLmIuxnKYSTwTtlt%2FtoPvRmyRwXngXn1KagSfVpWUqXOmKobz7zNmfFB8XmzhSim7J6Qt%2BYKEYik57f76VqZfCINMwvhFSuEoPjLRbXV%2Bq%2BqxlQsXjord9ZsXTdCE6IltwomAxIV%2FMYTq4s%2Bbkhw6beCBOHdp9Tvi7PVI2WNz4sU%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230511T010219Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAUO7ZF4EXWHZXRGED%2F20230511%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=9afb6ae2baa5fef77602c011af58918aefeb40dccc0b7162eedae8e049066f95" && \
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
