# Sample gRPC Client/Server
This folder contains a sample gRPC Server to use with the gRPC HealthCheck proxy

## Pre-requisites
You need to deploy [grpcurl](https://github.com/fullstorydev/grpcurl) to test the server

## Build the Server
```bash
docker build . -t grpc_server
```
## Test the gRPC Server Without TLS

```bash
# Server
docker run --net=host -p 50051:50051\
  grpc_server --grpcport :50051 --insecure

# Client
grpcurl -plaintext localhost:50051 echo.EchoServer.SayHello
```

The output should look like

```bash
{
  "message": "Hello   from hostname HOSTNAME"
}

```

## Test the gRPC Server With TLS

```bash
# Server
docker run --net=host -p 50051:50051 \
  grpc_server --grpcport :50051 \
  --tlsCert=certs/grpc_server_crt.pem \
  --tlsKey=certs/grpc_server_key.pem

# Client
docker run --net=host -p 50051:50051 \
   -t docker.io/salrashid123/grpc_app /grpc_client \
      --host localhost:50051 --tlsCert certs/CA_crt.pem \
      -skipHealthCheck --servername grpc.domain.com
```
