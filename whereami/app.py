from flask import Flask, request, Response, jsonify
import logging
import sys
import os
from flask_cors import CORS
from opencensus import trace
import whereami_payload
import requests

from concurrent import futures
import multiprocessing

import grpc

from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

import whereami_pb2
import whereami_pb2_grpc

# Prometheus export setup
from prometheus_flask_exporter import PrometheusMetrics
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server

# OpenCensus imports
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.grpc import client_interceptor
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
from opencensus.trace import config_integration, samplers, span_context
from opencensus.trace.propagation import google_cloud_format
from opencensus.trace.propagation import trace_context_http_header_format
from opencensus.trace.propagation import b3_format

# see if GCP PROJECT ID is available via env or METADATA
project_id = os.getenv('project_id')
if not project_id:

    r = requests.get(whereami_payload.METADATA_URL + 'project/project-id',
                                headers=whereami_payload.METADATA_HEADERS)
    if r.ok:
        project_id = r.text

# flask setup
app = Flask(__name__)
exporter = stackdriver_exporter.StackdriverExporter(project_id=project_id)
sampler = samplers.ProbabilitySampler(rate=1)
# check to see if backend; if so, expect headers
# TODO - add check to see if service is a backend service
#middleware = FlaskMiddleware(app, exporter=exporter, sampler=sampler, propagator=GoogleCloudFormatPropagator, excludelist_paths=['healthz'])
# do we have a valid project ID? if so, enable tracing middleware
if project_id:
    logging.info("Project ID %s detected; enabling Cloud Trace exports" % project_id)
    #middleware = FlaskMiddleware(app, exporter=exporter, sampler=sampler, excludelist_paths=['healthz', 'metrics'], propagator=google_cloud_format.GoogleCloudFormatPropagator())
    middleware = FlaskMiddleware(app, exporter=exporter, sampler=sampler, excludelist_paths=['healthz', 'metrics'], propagator=b3_format.B3FormatPropagator())
    #middleware = FlaskMiddleware(app, exporter=exporter, sampler=sampler, excludelist_paths=['healthz', 'metrics'], propagator=trace_context_http_header_format.TraceContextPropagator())
app.config['JSON_AS_ASCII'] = False  # otherwise our emojis get hosed
CORS(app)  # enable CORS
metrics = PrometheusMetrics(app) # enable Prom metrics

# gRPC setup
grpc_serving_port = 9090
grpc_metrics_port = 8080 # prometheus /metrics, same as flask port

# define Whereami object
whereami_payload = whereami_payload.WhereamiPayload()

# create gRPC class
class WhereamigRPC(whereami_pb2_grpc.WhereamiServicer):

    def GetPayload(self, request, context):
        payload = whereami_payload.build_payload(None)
        return whereami_pb2.WhereamiReply(**payload)


# if selected will serve gRPC endpoint on port 9090
# see https://github.com/grpc/grpc/blob/master/examples/python/xds/server.py
# for reference on code below
def grpc_serve():
    # the +5 you see below re: max_workers is a hack to avoid thread starvation
    # working on a proper workaround
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()+5),
        interceptors=(PromServerInterceptor(),)) # interceptor for metrics

    # Add the application servicer to the server.
    whereami_pb2_grpc.add_WhereamiServicer_to_server(WhereamigRPC(), server)

    # Create a health check servicer. We use the non-blocking implementation
    # to avoid thread starvation.
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1))
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    # Create a tuple of all of the services we want to export via reflection.
    services = tuple(
        service.full_name
        for service in whereami_pb2.DESCRIPTOR.services_by_name.values()) + (
            reflection.SERVICE_NAME, health.SERVICE_NAME)

    # Start an end point to expose metrics at host:$grpc_metrics_port/metrics
    start_http_server(grpc_metrics_port) # starts a flask server for metrics

    # Add the reflection service to the server.
    reflection.enable_server_reflection(services, server)
    server.add_insecure_port('[::]:' + str(grpc_serving_port))
    server.start()

    # Mark all services as healthy.
    overall_server_health = ""
    for service in services + (overall_server_health,):
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)

    # Park the main application thread.
    server.wait_for_termination()


# HTTP heathcheck
@app.route('/healthz')  # healthcheck endpoint
@metrics.do_not_track() # exclude from prom metrics
def i_am_healthy():
    return ('OK')


# default HTTP service
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):

    #print(middleware.propagator.from_headers(request))
    trace_id = middleware.propagator.from_headers(request.headers).trace_id
    span_id = span_context.generate_span_id()
    print(span_context.SpanContext)
    print(trace_id)
    print(span_id)
    payload = whereami_payload.build_payload(request.headers, trace_id, span_id)

    # split the path to see if user wants to read a specific field
    requested_value = path.split('/')[-1]
    if requested_value in payload.keys():

        return payload[requested_value]

    return jsonify(payload)

if __name__ == '__main__':
    config_integration.trace_integrations(['logging'])
    out_hdlr = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #     '%(asctime)s - %(name)s - %(levelname)s - traceId=%(traceId)s - spanId=%(spanId)s - %(message)s')
    out_hdlr.setFormatter(fmt)
    out_hdlr.setLevel(logging.INFO)
    logging.getLogger().addHandler(out_hdlr)
    logging.getLogger().setLevel(logging.INFO)
    app.logger.handlers = []
    app.logger.propagate = True
    config_integration.trace_integrations(['logging'])
    #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - traceId=%(traceId)s - spanId=%(spanId)s - %(message)s')
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # decision point - HTTP or gRPC?
    if os.getenv('GRPC_ENABLED') == "True":
        logging.info("gRPC server listening on port 9090")
        grpc_serve()

    else:
        app.run(
            host='0.0.0.0', port=int(os.environ.get('PORT', 8080)),
            threaded=True)
