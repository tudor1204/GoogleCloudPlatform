# [START gke_batch_aiml_workload_dockerfile]
FROM python:3.7-slim
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ./worker.py /worker.py
COPY ./rediswq.py /rediswq.py
COPY ./model_training.py /model_training.py

CMD  python worker.py
# [END gke_batch_aiml_workload_dockerfile]
