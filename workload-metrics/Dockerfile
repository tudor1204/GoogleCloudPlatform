# Copyright 2021 Google Inc.
#
# SPDX-License-Identifier: Apache-2.0

FROM golang:1.17-alpine as builder
WORKDIR /src
ADD . /src
RUN CGO_ENABLED=0 go build -o /workload-metrics

FROM gcr.io/distroless/static
COPY --from=builder /workload-metrics workload-metrics