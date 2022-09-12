FROM golang:1.18 as builder
WORKDIR /app
RUN go mod init secret-test
RUN go get cloud.google.com/go/secretmanager/apiv1
RUN go get google.golang.org/genproto/googleapis/cloud/secretmanager/v1
COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o /secret-access

FROM alpine
WORKDIR /
RUN apk add --no-cache ca-certificates
COPY --from=builder /secret-access /secret-access
CMD ["/secret-access"]