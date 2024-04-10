#!/bin/bash

export PROJECT=$(gcloud config list project --format "value(core.project)")

docker build . -f Dockerfile -t "gcr.io/${PROJECT}/jax-pingpong-tcpx:latest"

docker push "gcr.io/${PROJECT}/jax-pingpong-tcpx:latest"