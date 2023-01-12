FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:dd8f-main

RUN apt-get update -y && \
    apt-get install -y curl unzip

RUN apt-get install -y default-jdk
RUN curl -L https://sourceforge.net/projects/bbmap/files/BBMap_39.01.tar.gz/download -o \
    BBMap_39.01.tar.gz && \
    tar -xvzf BBMap_39.01.tar.gz && \
    rm BBMap_39.01.tar.gz
RUN python3 -m pip install biopython

# cellranger download link has weird options, wonder if it'll work?
RUN curl "https://cf.10xgenomics.com/releases/cell-atac/cellranger-atac-2.1.0.tar.gz?Expires=1673514390&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZi4xMHhnZW5vbWljcy5jb20vcmVsZWFzZXMvY2VsbC1hdGFjL2NlbGxyYW5nZXItYXRhYy0yLjEuMC50YXIuZ3oiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2NzM1MTQzOTB9fX1dfQ__&Signature=dGQ19KhysT-YVXDB6IgFNCf7sKi2xzzYcIDA4JP~AexjzspkjJJuDCnrsgabYI1nnC4di4RwG6IVl6wwGnJ9JrjdNl4z8z8EcXVlRLvaStvOf23rybZEtGvv8l2eTo0l6iiXBQzcjeZdqcBbV8I7cJt6GGzdpxmcq4s1TlNmZO5nctQcQrtPRsY3V4SczL5U9NSDFmEtU39kBoZQNujFiHrf38KZCRJ420Zq-Phgr80EfJXobWhiN-DVG9ozWgQTlgPnOVcJoKxLTo53VB71ABi8xzBgT~e8IkYdNbcj4IbOOFRQHgAax0-ZxD~ZVLMZtuf0UI6ITVDEDr3IakD6Iw__&Key-Pair-Id=APKAI7S6A5RYOXBWRPDA" -o \
    cellranger-atac-2.1.0.tar.gz && \
    tar -xzvf cellranger-atac-2.1.0.tar.gz && \
    rm cellranger-atac-2.1.0.tar.gz
RUN curl -O https://cf.10xgenomics.com/supp/cell-atac/refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz && \
    tar -xzvf refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz && \
    rm refdata-cellranger-arc-GRCh38-2020-A-2.0.0.tar.gz
RUN curl -O https://cf.10xgenomics.com/supp/cell-atac/refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz && \
    tar -xzvf refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz && \
    rm refdata-cellranger-arc-mm10-2020-A-2.0.0.tar.gz

# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
RUN python3 -m pip install --upgrade latch
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root
