# Use non-slim image due to OS dependencies of python packages. This gives us
# git, build-essential, libglib2 (opencv) and gomp (torchaudio).
FROM python:3.12

COPY /requirements.txt .

# Our python requirements have some OS dependencies beyond the base layer:
#
# * imagebind pulls in cartopy which has OS dependencies on geos and proj
# * opencv has a runtime OS dependency on libgl1-mesa-glx
#
# The dev dependencies are installed temporarily to compile the wheels.
# We leave the only the runtime dependencies, to keep the image smaller.
RUN apt-get update && \
    # install build and runtime dependencies
    apt-get install -y --no-install-recommends \
        libgeos-dev \
        libproj-dev \
        libgeos-c1v5 \
        libproj25 \
        libgl1-mesa-glx && \
    # Install everything except xformers first
    grep -v "\bxformers\b" requirements.txt > /tmp/r.txt && pip install -r /tmp/r.txt && \
    # Now, install xformers, as it should be able to see torch now
    grep "\bxformers\b" requirements.txt > /tmp/r.txt && pip install -r /tmp/r.txt && \
    # remove build dependencies
    apt-get purge -y libgeos-dev libproj-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p ./data ./src ./stages
COPY ./data ./data
COPY ./src ./src
COPY ./stages ./stages

