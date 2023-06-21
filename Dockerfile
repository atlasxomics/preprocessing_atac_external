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
RUN curl -o cellranger-atac-2.1.0.tar.gz "https://cf.10xgenomics.com/releases/cell-atac/cellranger-atac-2.1.0.tar.gz?Expires=1687342420&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZi4xMHhnZW5vbWljcy5jb20vcmVsZWFzZXMvY2VsbC1hdGFjL2NlbGxyYW5nZXItYXRhYy0yLjEuMC50YXIuZ3oiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2ODczNDI0MjB9fX1dfQ__&Signature=gFuPPOT2nfD6r3gVcZcmx0txrkJT0q3Jxgvi1YYGccGQi8v1APPhpjlSRVhJEhXWSRGnp5a7B2tTMUQfAFQ~S51~U9KMQwNqV6fAEj5LL0mbuWAtWnyctTWUwbuPy-9Wts~X2jK3v1pJdGUXIhEw8iJQ41DGs5-JIAZnnlb2UcYr660H-oE4Zte0qBktbvZgkk4r~0t2ytFUxXZ4QP81QvG4ckCmiHl038WQ3140ZKka4hDZrCpJ2LkibnPnX~Z4v2iuwvamt~KHytS3lHxLZo-6RM9K8bxrvP~HiQ4sfA0jTmtyJyrUQQlqlaXGJYoGZO6z~-yBLjtBQFIK~OyL1g__&Key-Pair-Id=APKAI7S6A5RYOXBWRPDA" && \ 
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
RUN curl -o Rnor6.tar.gz "https://atx-st-references.s3.us-east-1.amazonaws.com/rnor6-atac.tar.gz?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEFcaCXVzLWVhc3QtMSJHMEUCIDsQkXEn7qE%2Bb6nVGsPUQtqJeMvveial9uMkFnu7E39XAiEA%2BKIovJtjOD3XR1Iaffj1txOQh8msNq%2F%2BRRWh0NPNvqQq1QMIsP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw0NTQyMjE1ODA0NjQiDBTEvvKAb3qqgcO5kSqpA%2Bm4azW93D5le5d%2FAtdUtuLWJOHzR5ZTcaHD5zVfh%2F%2BkV4C%2ByEVAn9J2CuXoEDLQvN%2BOAr7GlDFzJw4kYzhSNR%2Ba2qJuSHsBv%2BZ0u5ByVf2MUKKrIEmlu%2FCRko%2FXeaV%2Fm4rdQLDDqkriCLlwTQVcYZb96iQlXuSd%2FdX0tfGFlJyRQp%2Fhz7u29lecBrJoV5YPUjZaFYqokyPRF5Jd1ICrbevfpa1%2FKI3B5hWqRi1rvOGt2WxO3rZ5PoIjtsCE8LwVRiqJPWUnYqSYyQ74zPp77Xr6x6kG2OFIuSdCPnMdZxb19qQBvlclNUSPDP05FLEsF8xABrRfPrl%2BNYcR3%2Ff2Cpjal1inoqTv8KKY04S%2BRS8%2Foxanpommns40IrPMm1e1%2Fz%2FZ776NQWv3lqgmrMfr9To%2BKR3p0flMjKul6AeWwEbTO69DnDAGJUihuJ0E84Wa0NeqmxH24i1I2XJwrCV3lgv4GjC92NRknW4JpOdlA6IG4581P5R0g7fny8qKcsRlv8TX74FMDGjhHCbbGA3CpkBODaSjacxHITZj4jODyX%2BtwVEMR0chnJH2MLneyKQGOpQC9ICXfz614lXRn77TtSN6%2B0Ov9AXBsWNNaOqsPHekk4BR5a5o%2FUeu22MCC4%2B7PHbWl3OmyurO1UUVtxHneQkxC4C8MrU8wV4UL3O68VjVJYz8eVy%2BM9ZqygvAdLMdE0MFSXpmSPwRLeOOYrPcQvNA6OTG51%2BwzU2GtFzWByIco5xedaovhJjwLrPsFTrQ41o%2FtZBvm3hzeJhY4BJOXTRBk9eQo4MfQCOJHcmH5asa7pxY2TX7rV8xE2NKGECmu%2BdhKnlD9VsExhCGhG3pwG6pB1yXxf1Uso1tsI%2FkkO8OHkLdN%2F%2BnK6k9dUtH4xbqmeuRPhKQcXB1Zi8%2B0a97NzYnHbt9PFzXvm3fX14WPG5BLghLFf9U&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230620T225937Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAWTQNXJCYBO4RLW5P%2F20230620%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=e828582b2814a564be2cff38438bce393af69398812bcb817b7a00c7b05ccba4" && \
    tar -xvzf Rnor6.tar.gz && \
    rm Rnor6.tar.gz

# Copy barcode files to root dir
COPY bc50.txt.gz /root/bc50.txt.gz
COPY bc50_old.txt.gz /root/bc50_old.txt.gz
COPY bc96.txt.gz /root/bc96.txt.gz

RUN python3 -m pip install matplotlib

# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
RUN python3 -m pip install --upgrade latch
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root
