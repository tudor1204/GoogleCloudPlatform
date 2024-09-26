
FROM python:3.11-slim
WORKDIR /app
RUN apt-get -y update
RUN apt-get -y install git
COPY requirements.txt ./
RUN python -m pip install --upgrade pip

# Install latest JAX and libtpu for trillium support
RUN pip install -U --pre jax[tpu] -f https://storage.googleapis.com/jax-releases/jax_nightly_releases.html -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
RUN pip install -U --pre libtpu-nightly -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/google/maxdiffusion.git

# Set trillium configs
ENV ENABLE_TPUNETD_CLIENT=false
ENV JAX_PLATFORMS=tpu,cpu
ENV ENABLE_PJRT_COMPATIBILITY=true

COPY main.py ./
EXPOSE 8000
ENTRYPOINT ["python", "main.py"]
