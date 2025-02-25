FROM ubuntu:24.04

# Install necessary packages
RUN apt update && apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    g++ \
    gcc \
    python3.12-dev

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages in the virtual environment
RUN pip install --upgrade pip
RUN pip install torch
RUN pip install wheel setuptools
RUN pip install transformers xformers
