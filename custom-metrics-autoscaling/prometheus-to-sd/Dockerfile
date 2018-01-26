# Copyright 2018 Google Inc.

FROM golang:1.7.3
ADD . /go/src/prometheus-dummy-exporter
RUN go get github.com/prometheus/client_golang/prometheus
RUN CGO_ENABLED=0 GOOS=linux go install prometheus-dummy-exporter

FROM alpine:latest
COPY --from=0 /go/bin/prometheus-dummy-exporter .
