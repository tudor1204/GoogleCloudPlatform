FROM golang:1.19.2
ADD . /go/src/hello-app
RUN go install hello-app

FROM alpine:latest
COPY --from=0 /go/bin/hello-app .
CMD ["./hello-app"]
