# gRPC Health-Check Proxy

`grpc-hc-proxy` is a webserver proxy for [gRPC Health Checking Protocol][https://github.com/grpc/grpc/blob/master/doc/health-checking.md].

This utility starts up an HTTP(S_ server which responds back to a client after making an RPC
call to a downstream server's gRPC healthcheck endpoint (`/grpc.health.v1.Health/Check`).

If the healthcheck passes, it responses back to the original http client will be `200`. If the
gRPC HealthCheck failed, a `503` is returned. If the service is not registered, a `404` is returned

Basically, this is an http proxy for the gRPC healthcheck protocol.

  `client--->http-->grpc_heatlh_proxy-->gRPC HealthCheck-->gRPC Server`

This utility uses similar flags, cancellation and timing snippets for the grpc call from [grpc-health-probe](https://github.com/grpc-ecosystem/grpc-health-probe). Use that tool as a specific [Liveness and Readiness Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/) for Kubernetes.

This utility can be used in the same cli mode but also as a generic HTTP interface (eg, as httpHealthCheck probe for Cloud Load Balancers that doesn't support gRPC).

For more information on the CLI mode without http listener, see the section at the end.

> This is not an official Google project and is unsupported by Google

## gRPC Health Checking Protocol

The gRPC server must implement the [gRPC Health Checking Protocol v1][https://github.com/grpc/grpc/blob/master/doc/health-checking.md]. This means you must register the `Health` service and implement the `rpc Check` that returns a `SERVING` status.

The [sample](https://github.com/boredabdel/kubernetes-engine-samples/tree/main/grpc-hc-proxy/sample-server) gRPC server included in this repo below for golang implements it at:

```golang
func (s *Server) Check(ctx context.Context, in *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error)
```

## Sample gRPC Server

The [example-server/](https://github.com/boredabdel/kubernetes-engine-samples/tree/main/grpc-hc-proxy/sample-server) folder contains certificates and sample gRPC server application to test with. 

## Building the proxy

To build the proxy directly, run

```bash
go build -o grpc-hc-proxy main.go
```

make it executable

```
chmod +x grpc-hc-proxy
```

## EXAMPLES

The examples below demonstrate how the proxy can be used to perform healthcheck of a downstream gRPC server with serviceName `echo.EchoService` listening on `:50051`.

You need to have a local gRPC Server started first, check the sample server for [instructions](https://github.com/boredabdel/kubernetes-engine-samples/tree/main/grpc-hc-proxy/sample-server) on how to do that

You can enable verbose logging with glog levels by appending `--logtostderr=1 -v 10`

### HTTP to the gRPC HealthCheck proxy

`grpc-hc-proxy` will listen on `:8080` for HTTP healthcheck requests on path `/healthz`.

`client->http->grpc_health_proxy->gRPC Server`

```bash
./grpc-hc-proxy \
  --http-listen-addr localhost:8080 \
  --http-listen-path /healthz \
  --grpcaddr localhost:50051 \
  --service-name echo.EchoServer \
  --logtostderr=1 -v 1
```

- Invoke the http proxy

```bash
curl http://localhost:8080/healthz
```

---

## HTTPS to the gRPC HealthCheck proxy

The `grpc-hc-proxy` will listen on `:8080` for HTTPS healthcheck requests on path `/healthz`.

The proxy will use the keypairs [http_server_crt.pem, http_server_key.pem] (https://github.com/boredabdel/kubernetes-engine-samples/tree/main/grpc-hc-proxy/sample-server/certs)

```bash
./grpc-hc-proxy \
  --http-listen-addr localhost:8080 \
  --http-listen-path /healthz \
  --grpcaddr localhost:50051 \
  --https-listen-cert sample-server/certs/http_server_crt.pem \
  --https-listen-key sample-server/certs/http_server_key.pem \
  --service-name echo.EchoServer \
  --logtostderr=1 -v 1
```

```bash
curl \
  --cacert sample-server/certs/CA_crt.pem \
  --resolve 'http.domain.com:8080:127.0.0.1' \
    https://http.domain.com:8080/healthz
```

---

## mTLS to the gRPC HealthCheck proxy

The `grpc-hc-proxy` will listen on `:8080` for HTTPS with mTLS healthcheck requests on path `/healthz`.

The proxy will use the keypairs [http_server_crt.pem, http_server_key.pem] (https://github.com/boredabdel/kubernetes-engine-samples/tree/main/grpc-hc-proxy/sample-server/certs) for the proxy and verify client certificates issued using the keypairs [client_crt.pem, client_key.pem] (https://github.com/boredabdel/kubernetes-engine-samples/tree/main/grpc-hc-proxy/sample-server/certs)

```bash
./grpc-hc-proxy \
  --http-listen-addr localhost:8080 \
  --http-listen-path /healthz \
  --grpcaddr localhost:50051 \
  --https-listen-cert sample-server/certs/http_server_crt.pem \
  --https-listen-key sample-server/certs/http_server_key.pem \
  --https-listen-ca sample-server/certs/CA_crt.pem
  --grpc-service-name echo.EchoServer \
  --https-listen-verify \
  --logtostderr=1 -v 1
```

```bash
curl \
  --cacert sample-server/certs/CA_crt.pem \
  --key sample-server/certs/client_key.pem \
  --cert sample-server/certs/client_crt.pem \
  --resolve 'http.domain.com:8080:127.0.0.1' \
    https://http.domain.com:8080/healthz
```

---

### mTLS between the proxy and the gRPC Server

Options to establish mTLS from the http proxy to the gRPC server

- `client->http->grpc_health_proxy->mTLS->gRPC server`

In the example below, `grpc_client_crt.pem` and `grpc_client_key.pem` are the TLS client credentials to present to the gRPC server

```bash
./grpc-hc-proxy \
  --http-listen-addr localhost:8080 \
  --http-listen-path /healthz \
  --grpcaddr localhost:50051 \
  --grpctls \
  --service-name echo.EchoServer \
  --grpc-ca-cert sample-server/certs/CA_crt.pem \
  --grpc-client-cert sample-server/certs/client_crt.pem \
  --grpc-client-key sample-server/certs/client_key.pem \
  --grpc-sni-server-name grpc.domain.com --logtostderr=1 -v 1
```


```bash
curl http://localhost:8080/healthz
```

### mTLS to Proxy and gRPC service

`client->https->grpc_health_proxy->mTLS->gRPC Server`

```bash
./grpc-hc-proxy \
  --http-listen-addr localhost:8080 \
  --http-listen-path /healthz \
  --grpcaddr localhost:50051 \
  --https-listen-cert sample-server/certs/http_server_crt.pem \
  --https-listen-key sample-server/certs/http_server_key.pem \
  --service-name echo.EchoServer \
  --https-listen-verify \
  --https-listen-ca sample-server/certs/CA_crt.pem \
  --grpctls \
  --grpc-client-cert sample-server/certs/client_crt.pem \
  --grpc-client-key sample-server/certs/client_key.pem \
  --grpc-ca-cert sample-server/certs/CA_crt.pem \
  --grpc-sni-server-name grpc.domain.com \
  --logtostderr=1 -v 1
```

```bash
curl  \
  --resolve 'http.domain.com:8080:127.0.0.1' \
  --cacert sample-server/certs/CA_crt.pem \
  --key sample-server/certs/client_key.pem \
  --cert sample-server/certs/client_crt.pem \
  https://http.domain.com:8080/healthz
```

## grpc-hc-proxy Flags

### Required flags

| Option | Description |
|:------------|-------------|
| **`-http-listen-addr`** | host:port for the http(s) listener |
| **`-grpcaddr`** | downstream gRPC host:port the proxy will connect to |
| **`-service-name`** | gRPC service name to check  |

### optional flags

Run the proxy with --help to get the full list of flags

```bash
./grpc-hc-proxy --help
```

--- 

#### TLS Certificates

Sample TLS certificates for use with this tool are under `example/certs` folder:

- `CA_crt.pem`:  Root CA
- `grpc_server_crt.pem`:  TLS certificate for the gRPC server
- `http_server_crt.pem`:  TLS certificate for the proxy
- `client_crt.pem`: Client certificate to use while connecting via mTLS to the proxy

---

### Kubernetes Pod Healthcheck

You can use this utility as a proxy for pods healthcheck in Kubernetes.

This is useful for external services (eg. loadbalancers) that utilize HTTP but need to verify a gRPC services health status.

In the kubernetes deployment below, an http request to the healthcheck serving port (`:8080`) will reflect
the status of the gRPC service listening on port `:50051`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
  labels:
    type: myapp-deployment-label
spec:
  replicas: 1
  selector:
    matchLabels:
      type: myapp
  template:
    metadata:
      labels:
        type: myapp
    spec:
      containers:
      - name: grpc-hc-proxy
        image: docker.io/salrashid123/grpc_health_proxy #Will fix once the images are under google-samples
        args: [ 
          "--http-listen-addr=0.0.0.0:8080",
          "--grpcaddr=localhost:50051",
          "--service-name=echo.EchoServer",
          "--logtostderr=1",
          "-v=1"
        ]
        ports:
        - containerPort: 8080
      - name: grpc-app
        image: docker.io/salrashid123/grpc_only_backend #Will fix once the images in under google-samples
        args: [
          "/grpc_server",
          "--grpcport=0.0.0.0:50051",
          "--insecure"
        ]
        ports:
        - containerPort: 50051
```