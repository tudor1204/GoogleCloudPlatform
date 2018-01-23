# Prometheus dummy exporter

A simple prometheus-dummy-exporter container exposes a single Prometheus metric with a constant value. The metric name, value and port on which metric will be served can be passed by flags.

This container is then deployed in the same pod with another container, prometheus-to-sd, configured to use the same port. It scrapes the metric and publishes it to Stackdriver.

# Prometheus to Stackdriver adapter

This adapter isn't part of the sample code, but a standard component used by
many Kubernetes applications. Learn more about it
[here](https://github.com/GoogleCloudPlatform/k8s-stackdriver/tree/master/prometheus-to-sd).
