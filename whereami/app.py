from flask import Flask, request, Response, jsonify
import logging
import sys
import os
from flask_cors import CORS
import whereami_payload

import grpc
from concurrent import futures
from grpc_reflection.v1alpha import reflection

import whereami_pb2
import whereami_pb2_grpc

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # otherwise our emojis get hosed
CORS(app)  # enable CORS

# define Whereami object
whereami_payload = whereami_payload.WhereamiPayload()


# create gRPC class
class WhereamigRPC(whereami_pb2_grpc.WhereamiServicer):

    def GetPayload(self, request, context):
        payload = whereami_payload.build_payload(None)
        return whereami_pb2.WhereamiReply(**payload)


# if selected will serve gRPC endpoint on port 9090
def grpc_serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    whereami_pb2_grpc.add_WhereamiServicer_to_server(WhereamigRPC(), server)
    SERVICE_NAMES = (
        whereami_pb2.DESCRIPTOR.services_by_name['Whereami'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port('[::]:9090')
    server.start()
    server.wait_for_termination()


# HTTP heathcheck
@app.route('/healthz')  # healthcheck endpoint
def i_am_healthy():
    return ('OK')


# default HTTP service
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):

    payload = whereami_payload.build_payload(request.headers)

    return jsonify(payload)

if __name__ == '__main__':
    out_hdlr = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    out_hdlr.setFormatter(fmt)
    out_hdlr.setLevel(logging.INFO)
    logging.getLogger().addHandler(out_hdlr)
    logging.getLogger().setLevel(logging.INFO)
    app.logger.handlers = []
    app.logger.propagate = True

    # decision point - HTTP or gRPC?
    if os.getenv('GRPC_ENABLED') == "True":
        logging.info("gRPC server listening on port 9090")
        grpc_serve()

    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), threaded=True)
