# Fermi-LAT lecture environment.
#
# Image contents: the runtime (fermipy + fermitools + gammapy + JupyterLab),
# the patched notebooks, and the gammapy tutorial datasets.
# Lecture data (PG 1553, TXS 0506) is downloaded separately on first run via
# setup_data.sh from a Dropbox URL configured in that script.
#
# Build:
#   bash student-environment/build.sh
#
# Run:
#   docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data fermipy-lecture
#
# fermitools is x86_64-only.  On Apple Silicon, Docker uses Rosetta automatically.

# fermitools is x86_64-only — pin the platform.  Override with --build-arg
# PLATFORM=... if you ever need to test another arch.
ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} condaforge/miniforge3:24.3.0-0

LABEL org.opencontainers.image.title="Fermi-LAT + gammapy lecture environment"
LABEL org.opencontainers.image.description="fermipy 1.4.0 + gammapy 1.3 + fermitools 2.2.0 + lecture notebooks"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Build the conda env.  We install curl + ca-certificates via conda so we
# don't depend on apt at all (avoids flaky archive.ubuntu.com mirrors).
COPY student-environment/environment.yml /tmp/environment.yml
RUN mamba env create -f /tmp/environment.yml \
 && mamba clean -afy \
 && rm /tmp/environment.yml

SHELL ["conda", "run", "--no-capture-output", "-n", "fermipy-lecture", "/bin/bash", "-c"]

# Pre-fetch gammapy tutorial datasets (~260 MB) — small enough to bake in.
ENV GAMMAPY_DATA=/opt/gammapy-data/1.3
RUN mkdir -p /opt/gammapy-data \
 && gammapy download datasets --out ${GAMMAPY_DATA}

# Patched notebooks.
COPY student-environment/notebooks /home/student/notebooks

# Data fetcher + entrypoint.
ENV LECTURE_DATA=/opt/lecture-data
COPY student-environment/setup_data.sh /usr/local/bin/setup_data.sh
COPY student-environment/start.sh      /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/setup_data.sh /usr/local/bin/start.sh \
 && mkdir -p ${LECTURE_DATA}

# Non-root user.
RUN useradd --create-home --shell /bin/bash student \
 && chown -R student:student /home/student ${LECTURE_DATA} ${GAMMAPY_DATA}
USER student
WORKDIR /home/student/notebooks

EXPOSE 8888
ENTRYPOINT ["/usr/local/bin/start.sh"]
