FROM ubuntu:focal
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt install -y git python3-pip prodigal diamond-aligner \
    && pip3 install setuptools wheel requests packaging tqdm \    
    && pip3 install protobuf==3.20.* scikit-learn==0.23.2 h5py==2.10.0 numpy==1.19.2 tensorflow==2.5.0 lightgbm==3.2.1 pandas==1.4.0 scipy==1.8.0

RUN git clone --recursive https://github.com/chklovski/checkm2.git && cd checkm2 \
    && python3 setup.py install

ENV PATH="$HOME/.local/bin:$PATH"
CMD checkm2
