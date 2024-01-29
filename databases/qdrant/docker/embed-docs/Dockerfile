FROM python:3.11-slim-bookworm

ENV QDRANT_URL http://qdrant:6333
ENV COLLECTION_NAME training-docs
RUN mkdir -p /documents
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod 765 endpoint.py
EXPOSE 5001

CMD ["/app/embedding-job.py"]
ENTRYPOINT ["python"]