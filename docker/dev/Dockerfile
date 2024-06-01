# Docker image
FROM python:3.10.12-slim

RUN apt -y update && apt -y upgrade
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt -y install --no-install-recommends \
    # Necessary for pip install
    gcc g++ libc-dev \
    # For development and debug
    bash curl git net-tools vim \
    # For scikit-learn (scipy)
    gfortran libopenblas-dev liblapack-dev \
    # For opencv-python
    libopencv-dev \
    # # For building pafprocess module
    # swig \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# for updating python module
RUN pip install --upgrade pip

ARG WORKING_DIRECTORY
WORKDIR /${WORKING_DIRECTORY}

# Install pip modules
COPY ./docker/dev/requirements.txt ./
RUN pip install -Ur requirements.txt

# NOTE: pytorch family
RUN pip3 install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu
