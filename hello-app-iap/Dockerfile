FROM golang:1.8-alpine
ADD . /go/src/hello-app-iap
RUN go install hello-app-iap

FROM alpine:latest
COPY --from=0 /go/bin/hello-app-iap .
CMD ["./hello-app-iap"]
