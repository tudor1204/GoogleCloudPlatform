from flask import Flask, request, Response, jsonify
import logging
import sys
import os
from flask_cors import CORS
import whereami

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # otherwise our emojis get hosed
CORS(app)  # enable CORS

# define Whereami object
whereami = whereami.Whereami()


@app.route('/healthz')  # healthcheck endpoint
def i_am_healthy():
    return ('OK')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):

    payload = whereami.build_payload(request.headers)

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
