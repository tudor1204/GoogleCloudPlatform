# Copyright 2018 Google Inc.

FROM golang:1.7.3
ADD . /go/src/direct-to-sd
RUN go get cloud.google.com/go/compute/metadata
RUN go get golang.org/x/oauth2
RUN go get google.golang.org/api/monitoring/v3
RUN CGO_ENABLED=0 GOOS=linux go install direct-to-sd

FROM alpine:latest
RUN apk -U add ca-certificates
COPY --from=0 /go/bin/direct-to-sd .

