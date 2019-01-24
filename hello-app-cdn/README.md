# Hello Application w/ CDN example

This example shows how to build and deploy a containerized Go web server
application using [Kubernetes](https://kubernetes.io).

This application is compatible with the CDN feature of Google Cloud Platform in
that it returns the appropriate header to ensure responses are cached.

This directory contains:

- `main.go` contains the HTTP server implementation. It responds to all HTTP
  requests with a  `Hello, world!` response.
- `Dockerfile` is used to build the Docker image for the application.

